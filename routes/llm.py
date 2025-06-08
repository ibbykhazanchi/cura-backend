from fastapi import APIRouter, HTTPException
import httpx
import os
import logging
from pydantic import BaseModel
from openai import OpenAI

router = APIRouter(
    tags=["llm"]
)

logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
async def chat_completion(request: ChatRequest):
    """
    Send a chat completion request to OpenAI.
    
    Expected request body format:
    {
        "message": "Hello, how are you?"
    }
    """
    try:
        client = OpenAI()
        response = client.responses.create(
            model="gpt-4.1",
            instructions="""
            You are an AI assistant that helps answers questions about a user's medications. The medications you're going to help with are the following:            
                {
                    id: 1,
                    name: 'Lexapro',
                    genericName: 'escitalopram',
                    category: 'Antidepressant',
                    dosage: '10mg',
                    dueTime: '12:00',
                    frequency: 'daily',
                    instructions: 'Take with food',
                    taken: false,
                    nextIntake: null,
                    brandColor: '#2E5BFF',
                    streak: 5,
                    totalDoses: 30,
                    missedDoses: 2,
                    lastTaken: null,
                    refillDate: '2024-12-20',
                    prescribedBy: 'Dr. Smith'
                },
                {
                    id: 2,
                    name: 'Opill',
                    genericName: '',
                    category: 'Birth control',
                    dosage: '0.075mg',
                    dueTime: '09:00',
                    frequency: 'daily',
                    instructions: 'Take at same time daily',
                    taken: false,
                    nextIntake: null,
                    brandColor: '#2E5BFF',
                    streak: 12,
                    totalDoses: 21,
                    missedDoses: 0,
                    lastTaken: null,
                    refillDate: '2024-12-15',
                    prescribedBy: 'Dr. Johnson'
                },
                {
                    id: 3,
                    name: 'Metformin',
                    genericName: 'metformin HCl',
                    category: 'Diabetes',
                    dosage: '500mg',
                    dueTime: '18:00',
                    frequency: 'twice daily',
                    instructions: 'Take with dinner',
                    taken: false,
                    nextIntake: null,
                    brandColor: '#2E5BFF',
                    streak: 7,
                    totalDoses: 42,
                    missedDoses: 3,
                    lastTaken: null,
                    refillDate: '2024-12-25',
                    prescribedBy: 'Dr. Davis'
                }
            """,
            input=request.message
        )
        
        return {"response": response.output_text}
            
    except Exception as e:
        logger.error(f"Error in chat completion: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat completion: {str(e)}"
        )

@router.get("/session")
async def get_session():
    """
    Creates an ephemeral token for WebRTC connection.
    This token should be used by the client to establish a WebRTC connection with OpenAI's Realtime API.
    The token expires after one minute.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/realtime/sessions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4o-realtime-preview-2025-06-03",
                "voice": "verse",
            }
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to create ephemeral token"
            )
        return response.json() 