from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Dict, Any
from app.api.dependencies import verify_api_key
from app.schemas.response import StandardResponse
from app.services.webhook_service import process_webhook
from app.database.mongodb import get_database
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/vapi/webhook", response_model=StandardResponse, dependencies=[Depends(verify_api_key)])
async def receive_webhook(payload: Dict[str, Any]):
    logger.info("Incoming webhook received")
    try:
        await process_webhook(payload)
        return StandardResponse(
            success=True,
            message="Webhook received"
        )
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process webhook"
        )

@router.get("/conversations", response_model=StandardResponse, dependencies=[Depends(verify_api_key)])
async def get_conversations(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100)):
    db = get_database()
    try:
        cursor = db["conversations"].find({"deleted": {"$ne": True}}).sort("createdAt", -1).skip(skip).limit(limit)
        conversations = await cursor.to_list(length=limit)
        
        for conv in conversations:
            conv["_id"] = str(conv["_id"])
            
        return StandardResponse(
            success=True,
            message="Conversations retrieved successfully",
            data={"conversations": conversations}
        )
    except Exception as e:
        logger.error(f"Error fetching conversations: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")

@router.get("/conversations/{call_id}", response_model=StandardResponse, dependencies=[Depends(verify_api_key)])
async def get_conversation(call_id: str):
    db = get_database()
    try:
        conversation = await db["conversations"].find_one({"callId": call_id, "deleted": {"$ne": True}})
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
            
        conversation["_id"] = str(conversation["_id"])
        
        cursor = db["messages"].find({"callId": call_id}).sort("timestamp", 1)
        messages = await cursor.to_list(length=1000)
        
        for msg in messages:
            msg["_id"] = str(msg["_id"])
            
        conversation["messages"] = messages
        
        return StandardResponse(
            success=True,
            message="Conversation retrieved successfully",
            data=conversation
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching conversation {call_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")

@router.delete("/conversations/{call_id}", response_model=StandardResponse, dependencies=[Depends(verify_api_key)])
async def delete_conversation(call_id: str):
    db = get_database()
    try:
        result = await db["conversations"].update_one(
            {"callId": call_id, "deleted": {"$ne": True}},
            {"$set": {"deleted": True}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
            
        return StandardResponse(
            success=True,
            message="Conversation soft deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation {call_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
