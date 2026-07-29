from typing import Dict, Any
import logging
from datetime import datetime, timezone
from app.database.mongodb import get_database

logger = logging.getLogger(__name__)

async def process_webhook(payload: Dict[str, Any]):
    db = get_database()
    message = payload.get("message", {})
    if not isinstance(message, dict):
        logger.warning("Invalid webhook payload format")
        return

    event_type = message.get("type")
    
    # Try to extract the call object, or fallback to the message itself
    call = message.get("call", {})
    if not call and event_type not in ["end-of-call-report", "conversation-ended"]:
        call = message

    call_id = call.get("id") or message.get("callId")
    if not call_id:
        logger.warning("Webhook received without callId")
        return

    assistant_id = call.get("assistantId") or message.get("assistantId")
    
    customer = call.get("customer") or {}
    user_phone = customer.get("number") or message.get("customerNumber")
    
    phone_number = call.get("phoneNumber") or {}
    assistant_phone = phone_number.get("number") or message.get("assistantNumber")

    started_at = call.get("startedAt")
    ended_at = call.get("endedAt")
    duration = call.get("duration")
    status = call.get("status") or event_type

    # Upsert conversation document
    conversation_data = {
        "callId": call_id,
        "assistantId": assistant_id,
        "userPhone": user_phone,
        "assistantPhone": assistant_phone,
        "startedAt": started_at,
        "endedAt": ended_at,
        "duration": duration,
        "status": status,
        "updatedAt": datetime.now(timezone.utc).isoformat()
    }

    # Filter out None values to avoid overwriting existing data with nulls
    conversation_data = {k: v for k, v in conversation_data.items() if v is not None}

    try:
        await db["conversations"].update_one(
            {"callId": call_id},
            {
                "$set": conversation_data,
                "$setOnInsert": {"createdAt": datetime.now(timezone.utc).isoformat()}
            },
            upsert=True
        )
    except Exception as e:
        logger.error(f"Database error saving conversation {call_id}: {str(e)}")

    # Handle messages inside the webhook
    messages_list = message.get("messages", [])
    
    if event_type == "transcript" and message.get("transcript"):
        # Synthesize a message object for transcript events
        messages_list.append({
            "role": message.get("role", "system"),
            "message": message.get("transcript"),
            "time": datetime.now(timezone.utc).timestamp() * 1000
        })
        
    for msg in messages_list:
        if isinstance(msg, dict):
            msg_role = msg.get("role")
            msg_content = msg.get("message") or msg.get("content")
            
            # Format timestamp
            raw_time = msg.get("time") or msg.get("createdAt") or datetime.now(timezone.utc).isoformat()
            
            if msg_content:
                msg_doc = {
                    "conversationId": call_id,
                    "callId": call_id,
                    "role": msg_role,
                    "message": msg_content,
                    "timestamp": raw_time,
                    "createdAt": datetime.now(timezone.utc).isoformat()
                }
                try:
                    await db["messages"].insert_one(msg_doc)
                except Exception as e:
                    logger.error(f"Database error saving message for {call_id}: {str(e)}")
                    
    logger.info(f"Successfully processed webhook event '{event_type}' for callId: {call_id}")
