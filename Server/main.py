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
    session_limit_minutes: Optional[int] = 1
    intervention_frequency: Optional[str] = "medium"  # low, medium, high

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
            platform = platform_info.get("platform")
            
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

# Add this to your main.py FastAPI app

# @app.get("/check_intervention")
# async def check_for_intervention():
#     """
#     Endpoint for the frontend to check if an intervention is needed.
#     This allows the frontend to poll for notifications without having to
#     process OCR data directly.
#     """
#     try:
#         # Get current platform session if any
#         current_platform = None
#         async with aiosqlite.connect(DB_PATH) as db:
#             cursor = await db.execute(
#                 "SELECT platform FROM sessions WHERE end_time IS NULL ORDER BY start_time DESC LIMIT 1"
#             )
#             result = await cursor.fetchone()
#             if result:
#                 current_platform = result[0]
        
#         if not current_platform:
#             return {
#                 "intervention_required": False
#             }
        
#         # Get usage stats for the platform
#         usage_stats = await get_usage_stats(current_platform)
        
#         # Check if intervention is needed
#         intervention_needed, reason = await check_intervention_needed(current_platform, usage_stats)
        
#         if intervention_needed:
#             # Generate a personalized message
#             message = generate_intervention_message(current_platform, usage_stats)
            
#             # Determine intervention type based on usage severity
#             if usage_stats.get("current_session_minutes", 0) > 30 or usage_stats.get("today_minutes", 0) > 90:
#                 intervention_type = "overlay"  # More intrusive for heavy usage
#             else:
#                 intervention_type = "notification"  # Less intrusive for moderate usage
            
#             return {
#                 "intervention_required": True,
#                 "intervention_data": {
#                     "type": intervention_type,
#                     "message": message,
#                     "reason": reason,
#                     "usage_stats": usage_stats
#                 }
#             }
        
#         return {
#             "intervention_required": False
#         }
        
#     except Exception as e:
#         logger.error(f"❌ Error checking for intervention: {e}")
#         raise HTTPException(status_code=500, detail=str(e))