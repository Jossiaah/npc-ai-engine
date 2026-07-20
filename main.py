import os
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from anthropic import Anthropic
from dotenv import load_dotenv

# 1. Load Environment Variables from your safe local .env file
load_dotenv()

# 2. Initialize the Core FastAPI Web Application Blueprint
app = FastAPI(title="Production GenAI NPC Engine")

# 3. Mount Static Asset Routes and Template Rendering Engines
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 4. Initialize the Anthropic Microservice Client Wrapper
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# 5. Safely Pull Global Structured NPC Character Profiles from JSON Config
with open("config/npc_profiles.json", "r") as f:
    NPC_PROFILES = json.load(f)

# 6. Setup Pydantic Runtime Data Validation Schemas for API Requests
class ChatRequest(BaseModel):
    npc_id: str
    message: str

# 7. Endpoint: Serve Main Single Page UI Framework Dashboard to Browser
@app.get("/")
async def serve_home(request: Request):
    return templates.TemplateResponse(
        request,             
        "index.html",        
        {"npcs": NPC_PROFILES} 
    )

# 8. Endpoint: Asynchronous Chat Logic Processing System Endpoint Routing Loop
@app.post("/api/v1/chat")
async def process_npc_chat(payload: ChatRequest):
    if payload.npc_id not in NPC_PROFILES:
        raise HTTPException(status_code=404, detail="NPC profile not found")
        
    profile = NPC_PROFILES[payload.npc_id]
    system_instruction = profile["system_instruction"]

    try:
        response = client.messages.create(
            model="claude-fable-5",
            max_tokens=250,
            system=system_instruction,
            messages=[{"role": "user", "content": payload.message}]
        )
        
        # This helper safely extracts text across ALL SDK versions
        raw_text_output = "".join([block.text for block in response.content if hasattr(block, 'text')])
        
        # Cleanly parse the character's internal JSON response schema 
        return json.loads(raw_text_output)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))