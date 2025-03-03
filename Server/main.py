# Update your main.py in the server folder to add CORS
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # Add this import
from typing import Dict, Any, List, Optional
import logging
import json
import datetime
import os
from pydantic import BaseModel

from llm import detect_short_form_video, generate_intervention_message
from db_manager import (
    init_db, 
    record_session, 
    get_usage_stats, 
    check_intervention_needed,
    update_user_settings
)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://localhost:8000", "http://localhost:5173"],  # React app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database on startup
@app.on_event("startup")
async def startup_db_client():
    await init_db()

class UserSettings(BaseModel):
    daily_limit_minutes: Optional[int] = 60
    session_limit_minutes: Optional[int] = 15  # Changed from 1 to 15 to match default in db_manager
    intervention_frequency: Optional[str] = "medium"  # low, medium, high

# Add this function to standardize platform names
def standardize_platform_name(platform: str) -> str:
    """Standardize platform name to avoid confusion between similar platforms"""
    platform = platform.lower().strip()
    
    if "instagram" in platform or platform == "ig reels":
        return "Instagram Reels"
    elif "facebook" in platform or platform == "fb reels":
        return "Facebook Reels"
    elif "tiktok" in platform:
        return "TikTok"
    elif "youtube" in platform or "yt shorts" in platform:
        return "YouTube Shorts"
    elif "snapchat" in platform:
        return "Snapchat"
    else:
        return platform.title()  # Capitalize for display purposes

@app.post("/process_screen")
async def process_screen(request: Request) -> Dict[str, Any]:
    try:
        data = await request.json()

        if "data" not in data or not isinstance(data["data"], list) or not data["data"]:
            raise HTTPException(status_code=400, detail="Invalid OCR data format: Missing 'data' field.")

        ocr_text = data["data"][0]["content"].get("text", "").strip()
        timestamp = data.get("timestamp", datetime.datetime.now().isoformat())
        
        if not ocr_text:
            raise HTTPException(status_code=400, detail="No text found in OCR data.")

        # Analyze the screen content
        platform_info = json.loads(detect_short_form_video(ocr_text))
        
        logger.info(f"🔍 Platform detection result: {platform_info}")
        
        response_data = {
            "status": "success",
            "platform_detected": platform_info.get("detected", False),
            "platform": platform_info.get("platform", "none"),
            "confidence": platform_info.get("confidence", 0),
            "intervention_required": False
        }
        
        # If a video platform is detected, record the session and check if intervention is needed
        if platform_info.get("detected", False) and platform_info.get("platform") != "none":
            # Standardize platform name
            platform = standardize_platform_name(platform_info.get("platform"))
            response_data["platform"] = platform
            
            # Record this detection in the database
            await record_session(platform, timestamp)
            
            # Get usage statistics for the user
            usage_stats = await get_usage_stats(platform)
            
            # Check if we need to show an intervention
            intervention_needed, reason = await check_intervention_needed(platform, usage_stats)
            
            if intervention_needed:
                # Generate a personalized message
                message = generate_intervention_message(platform, usage_stats)
                
                # Determine intervention type based on usage severity
                if usage_stats.get("current_session_minutes", 0) > 30 or usage_stats.get("today_minutes", 0) > 90:
                    intervention_type = "overlay"  # More intrusive for heavy usage
                else:
                    intervention_type = "notification"  # Less intrusive for moderate usage
                
                response_data["intervention_required"] = True
                response_data["intervention_data"] = {
                    "type": intervention_type,
                    "message": message,
                    "reason": reason,
                    "usage_stats": usage_stats
                }
                
                logger.info(f"⚠️ Intervention triggered: {reason}")
        
        return response_data

    except Exception as e:
        logger.error(f"❌ Server Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/update_settings")
async def update_settings(settings: UserSettings) -> Dict[str, Any]:
    """Update user preferences and limits"""
    try:
        await update_user_settings(settings.dict())
        return {"status": "success", "message": "Settings updated successfully"}
    except Exception as e:
        logger.error(f"❌ Error updating settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/usage_stats")
async def get_stats() -> Dict[str, Any]:
    """Get user's usage statistics for dashboard display"""
    try:
        # Get overall stats, not platform-specific
        stats = await get_usage_stats()
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"❌ Error retrieving stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Uncomment and fix this endpoint
import aiosqlite
from db_manager import DB_PATH

@app.get("/check_intervention")
async def check_for_intervention():
    """
    Endpoint for the frontend to check if an intervention is needed.
    This allows the frontend to poll for notifications without having to
    process OCR data directly.
    """
    try:
        # Get current platform session if any
        current_platform = None
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute(
                "SELECT platform FROM sessions WHERE end_time IS NULL ORDER BY start_time DESC LIMIT 1"
            )
            result = await cursor.fetchone()
            if result:
                current_platform = result[0]
        
        if not current_platform:
            return {
                "intervention_required": False
            }
        
        # Get usage statistics for the platform
        usage_stats = await get_usage_stats(current_platform)
        
        # Check if intervention is needed
        intervention_needed, reason = await check_intervention_needed(current_platform, usage_stats)
        
        if intervention_needed:
            # Generate a personalized message
            message = generate_intervention_message(current_platform, usage_stats)
            
            # Determine intervention type based on usage severity
            if usage_stats.get("current_session_minutes", 0) > 30 or usage_stats.get("today_minutes", 0) > 90:
                intervention_type = "overlay"  # More intrusive for heavy usage
            else:
                intervention_type = "notification"  # Less intrusive for moderate usage
            
            return {
                "intervention_required": True,
                "intervention_data": {
                    "type": intervention_type,
                    "message": message,
                    "reason": reason,
                    "usage_stats": usage_stats
                }
            }
        
        return {
            "intervention_required": False
        }
        
    except Exception as e:
        logger.error(f"❌ Error checking for intervention: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Add this endpoint at the end of your file

@app.get("/debug/sessions")
async def debug_sessions() -> Dict[str, Any]:
    """Debug endpoint to view raw session data"""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT id, platform, start_time, end_time, duration FROM sessions ORDER BY start_time DESC LIMIT 50"
            )
            sessions = await cursor.fetchall()
            
            # Convert to list of dicts
            result = []
            for session in sessions:
                result.append(dict(session))
                
            return {"sessions": result}
    except Exception as e:
        logger.error(f"❌ Error retrieving debug data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Add this admin endpoint at the end of your file

@app.get("/admin/fix-platform-names")
async def fix_platform_names() -> Dict[str, Any]:
    """Admin endpoint to standardize platform names in the database"""
    try:
        updated_sessions = 0
        updated_stats = 0
        
        async with aiosqlite.connect(DB_PATH) as db:
            # First, get and update all sessions
            cursor = await db.execute("SELECT id, platform FROM sessions")
            sessions = await cursor.fetchall()
            
            for session_id, platform in sessions:
                standardized_name = standardize_platform_name(platform)
                if standardized_name != platform:
                    await db.execute(
                        "UPDATE sessions SET platform = ? WHERE id = ?",
                        (standardized_name, session_id)
                    )
                    updated_sessions += 1
            
            # Next, update statistics platform breakdown
            cursor = await db.execute("SELECT date, platform_breakdown FROM statistics")
            stats = await cursor.fetchall()
            
            for date, platform_breakdown in stats:
                if not platform_breakdown:
                    continue
                    
                platforms = json.loads(platform_breakdown)
                updated = False
                new_platforms = {}
                
                for platform, minutes in platforms.items():
                    standardized_name = standardize_platform_name(platform)
                    if standardized_name in new_platforms:
                        # Combine minutes if platform already exists under standardized name
                        new_platforms[standardized_name] = new_platforms[standardized_name] + minutes
                    else:
                        new_platforms[standardized_name] = minutes
                    
                    if standardized_name != platform:
                        updated = True
                
                if updated:
                    await db.execute(
                        "UPDATE statistics SET platform_breakdown = ? WHERE date = ?",
                        (json.dumps(new_platforms), date)
                    )
                    updated_stats += 1
            
            await db.commit()
            
        return {
            "status": "success",
            "message": f"Fixed platform names: {updated_sessions} sessions and {updated_stats} stat records updated",
        }
    except Exception as e:
        logger.error(f"❌ Error fixing platform names: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Add this debug endpoint

@app.get("/debug/platforms")
async def debug_platforms() -> Dict[str, Any]:
    """Debug endpoint to view all platform names in use"""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            # Get unique platforms from sessions
            cursor = await db.execute("SELECT DISTINCT platform FROM sessions")
            platforms = [row[0] for row in await cursor.fetchall()]
            
            # Get all platform breakdowns from statistics
            cursor = await db.execute("SELECT date, platform_breakdown FROM statistics")
            stats_platforms = {}
            
            for date, platform_breakdown in await cursor.fetchall():
                if platform_breakdown:
                    platforms_dict = json.loads(platform_breakdown)
                    stats_platforms[date] = platforms_dict
                
            return {
                "status": "success",
                "session_platforms": platforms,
                "statistics_platforms": stats_platforms
            }
    except Exception as e:
        logger.error(f"❌ Error retrieving platform data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/admin/reset-database", response_model=Dict[str, Any])
async def reset_database():
    """Admin endpoint to completely reset the database and start fresh"""
    try:
        import os
        
        # Close any database connections
        # Delete the database file if it exists
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
            logger.info("Existing database file deleted")
        
        # Reinitialize the database with clean tables
        await init_db()
        logger.info("Database reinitialized with fresh tables")
        
        return {
            "status": "success",
            "message": "Database has been completely reset"
        }
    except Exception as e:
        logger.error(f"❌ Error resetting database: {e}")
        raise HTTPException(status_code=500, detail=str(e))