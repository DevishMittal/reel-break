import sqlite3
import aiosqlite
import datetime
import json
import os
from typing import Dict, Any, Tuple, List, Optional

# Database path
DB_PATH = "screenbreak.db"

async def init_db():
    """Initialize the database with required tables"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Create sessions table to track platform usage
        await db.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT,
            duration INTEGER DEFAULT 0
        )
        ''')
        
        # Create settings table for user preferences
        await db.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            daily_limit_minutes INTEGER DEFAULT 60,
            session_limit_minutes INTEGER DEFAULT 15,
            intervention_frequency TEXT DEFAULT 'medium',
            settings_json TEXT
        )
        ''')
        
        # Create statistics table for aggregated data
        await db.execute('''
        CREATE TABLE IF NOT EXISTS statistics (
            date TEXT PRIMARY KEY,
            total_minutes INTEGER DEFAULT 0,
            platform_breakdown TEXT,
            session_count INTEGER DEFAULT 0
        )
        ''')
        
        # Insert default settings if they don't exist
        await db.execute('''
        INSERT OR IGNORE INTO settings (id, daily_limit_minutes, session_limit_minutes, intervention_frequency)
        VALUES (1, 60, 15, 'medium')
        ''')
        
        await db.commit()

async def record_session(platform: str, timestamp: str) -> None:
    """Record or update a platform usage session"""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.datetime.now().isoformat()
    
    async with aiosqlite.connect(DB_PATH) as db:
        # First check if there's an open session for this platform
        cursor = await db.execute(
            "SELECT id, start_time FROM sessions WHERE platform = ? AND end_time IS NULL", 
            (platform,)
        )
        open_session = await cursor.fetchone()
        
        if open_session:
            # Update existing session
            session_id, start_time = open_session
            start_dt = datetime.datetime.fromisoformat(start_time)
            current_dt = datetime.datetime.now()
            duration_minutes = (current_dt - start_dt).total_seconds() // 60
            
            # Update the session duration but keep it open
            await db.execute(
                "UPDATE sessions SET duration = ? WHERE id = ?",
                (duration_minutes, session_id)
            )
        else:
            # Create a new session
            await db.execute(
                "INSERT INTO sessions (platform, start_time) VALUES (?, ?)",
                (platform, current_time)
            )
            
            # Update statistics for today
            cursor = await db.execute("SELECT * FROM statistics WHERE date = ?", (today,))
            stats_row = await cursor.fetchone()
            
            if stats_row:
                # Update existing stats
                await db.execute(
                    "UPDATE statistics SET session_count = session_count + 1 WHERE date = ?",
                    (today,)
                )
            else:
                # Create new stats row for today
                platform_breakdown = json.dumps({platform: 0})
                await db.execute(
                    "INSERT INTO statistics (date, total_minutes, platform_breakdown, session_count) VALUES (?, ?, ?, ?)",
                    (today, 0, platform_breakdown, 1)
                )
        
        await db.commit()

async def close_session(platform: str) -> None:
    """Close an open session for a platform"""
    current_time = datetime.datetime.now().isoformat()
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Get the open session
        cursor = await db.execute(
            "SELECT id, start_time, duration FROM sessions WHERE platform = ? AND end_time IS NULL", 
            (platform,)
        )
        open_session = await cursor.fetchone()
        
        if open_session:
            session_id, start_time, duration = open_session
            start_dt = datetime.datetime.fromisoformat(start_time)
            current_dt = datetime.datetime.now()
            duration_minutes = (current_dt - start_dt).total_seconds() // 60
            
            # Close the session
            await db.execute(
                "UPDATE sessions SET end_time = ?, duration = ? WHERE id = ?",
                (current_time, duration_minutes, session_id)
            )
            
            # Update statistics
            cursor = await db.execute("SELECT platform_breakdown, total_minutes FROM statistics WHERE date = ?", (today,))
            stats_row = await cursor.fetchone()
            
            if stats_row:
                platform_breakdown, total_minutes = stats_row
                platforms = json.loads(platform_breakdown)
                
                # Update platform time
                platforms[platform] = platforms.get(platform, 0) + duration_minutes
                new_total = total_minutes + duration_minutes
                
                await db.execute(
                    "UPDATE statistics SET total_minutes = ?, platform_breakdown = ? WHERE date = ?",
                    (new_total, json.dumps(platforms), today)
                )
        
        await db.commit()

async def get_usage_stats(platform: Optional[str] = None) -> Dict[str, Any]:
    """Get usage statistics for today, optionally filtered by platform"""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Get settings for goals
        cursor = await db.execute("SELECT daily_limit_minutes, session_limit_minutes FROM settings WHERE id = 1")
        settings = await cursor.fetchone()
        daily_goal, session_goal = settings if settings else (60, 15)
        
        # Get today's statistics
        cursor = await db.execute("SELECT total_minutes, platform_breakdown, session_count FROM statistics WHERE date = ?", (today,))
        stats_row = await cursor.fetchone()
        
        if not stats_row:
            return {
                "today_minutes": 0,
                "daily_goal_minutes": daily_goal,
                "current_session_minutes": 0,
                "session_goal_minutes": session_goal,
                "times_opened_today": 0,
                "platforms": {}
            }
        
        total_minutes, platform_breakdown, session_count = stats_row
        platforms = json.loads(platform_breakdown) if platform_breakdown else {}
        
        # Get current open session if any
        if platform:
            cursor = await db.execute(
                "SELECT start_time FROM sessions WHERE platform = ? AND end_time IS NULL", 
                (platform,)
            )
            open_session = await cursor.fetchone()
            
            current_session_minutes = 0
            if open_session:
                start_time = open_session[0]
                start_dt = datetime.datetime.fromisoformat(start_time)
                current_dt = datetime.datetime.now()
                current_session_minutes = (current_dt - start_dt).total_seconds() // 60
        else:
            # Check for any open session
            cursor = await db.execute("SELECT start_time FROM sessions WHERE end_time IS NULL ORDER BY start_time DESC LIMIT 1")
            open_session = await cursor.fetchone()
            
            current_session_minutes = 0
            if open_session:
                start_time = open_session[0]
                start_dt = datetime.datetime.fromisoformat(start_time)
                current_dt = datetime.datetime.now()
                current_session_minutes = (current_dt - start_dt).total_seconds() // 60
        
        # If platform is specified, filter stats
        if platform:
            platform_minutes = platforms.get(platform, 0)
            platform_sessions = await db.execute(
                "SELECT COUNT(*) FROM sessions WHERE platform = ? AND start_time LIKE ?", 
                (platform, f"{today}%")
            )
            platform_session_count = (await platform_sessions.fetchone())[0]
            
            return {
                "today_minutes": platform_minutes,
                "daily_goal_minutes": daily_goal,
                "current_session_minutes": current_session_minutes,
                "session_goal_minutes": session_goal,
                "times_opened_today": platform_session_count,
                "platform": platform
            }
        
        # Return overall stats
        return {
            "today_minutes": total_minutes,
            "daily_goal_minutes": daily_goal,
            "current_session_minutes": current_session_minutes,
            "session_goal_minutes": session_goal,
            "times_opened_today": session_count,
            "platforms": platforms
        }

async def check_intervention_needed(platform: str, usage_stats: Dict[str, Any]) -> Tuple[bool, str]:
    """Determine if an intervention is needed based on usage patterns"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Get intervention frequency setting
        cursor = await db.execute("SELECT intervention_frequency FROM settings WHERE id = 1")
        frequency = (await cursor.fetchone())[0]
        
        # Convert frequency to numerical thresholds
        if frequency == "low":
            session_threshold = 0.9  # 90% of limit
            daily_threshold = 0.8    # 80% of limit
        elif frequency == "medium":
            session_threshold = 0.75  # 75% of limit
            daily_threshold = 0.6     # 60% of limit
        else:  # high
            session_threshold = 0.5   # 50% of limit
            daily_threshold = 0.4     # 40% of limit
        
        daily_limit = usage_stats.get("daily_goal_minutes", 60)
        session_limit = usage_stats.get("session_goal_minutes", 15)
        
        current_daily = usage_stats.get("today_minutes", 0)
        current_session = usage_stats.get("current_session_minutes", 0)
        
        # Check if we should intervene
        if current_session >= session_limit:
            return True, "session_limit_exceeded"
        elif current_daily >= daily_limit:
            return True, "daily_limit_exceeded"
        elif current_session >= session_limit * session_threshold:
            return True, "session_limit_approaching"
        elif current_daily >= daily_limit * daily_threshold:
            return True, "daily_limit_approaching"
        
        # Check excessive session count
        if usage_stats.get("times_opened_today", 0) > 10:
            return True, "frequent_opening"
            
        return False, ""

async def update_user_settings(settings: Dict[str, Any]) -> None:
    """Update user preferences and settings"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Extract specific settings
        daily_limit = settings.get("daily_limit_minutes")
        session_limit = settings.get("session_limit_minutes")
        frequency = settings.get("intervention_frequency")
        
        update_fields = []
        update_values = []
        
        if daily_limit is not None:
            update_fields.append("daily_limit_minutes = ?")
            update_values.append(daily_limit)
            
        if session_limit is not None:
            update_fields.append("session_limit_minutes = ?")
            update_values.append(session_limit)
            
        if frequency is not None:
            update_fields.append("intervention_frequency = ?")
            update_values.append(frequency)
        
        # Store all settings as JSON for future extensibility
        update_fields.append("settings_json = ?")
        update_values.append(json.dumps(settings))
        
        # Update settings
        if update_fields:
            query = f"UPDATE settings SET {', '.join(update_fields)} WHERE id = 1"
            await db.execute(query, update_values)
            await db.commit()