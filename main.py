import os
import json
import uuid
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from anthropic import Anthropic
from dotenv import load_dotenv
from src.memory import NPCMemoryManager

load_dotenv()

app = FastAPI(title="Production GenAI NPC Engine")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

with open("config/npc_profiles.json", "r") as f:
    NPC_PROFILES = json.load(f)

# Dynamically initialize individual memory manager nodes for all profiles on boot
MEMORY_BANKS = {npc_id: NPCMemoryManager(npc_id) for npc_id in NPC_PROFILES}

class ChatRequest(BaseModel):
    npc_id: str
    message: str

@app.get("/")
async def serve_home(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html", 
        {"npcs": NPC_PROFILES}
    )

@app.post("/api/v1/chat")
async def process_npc_chat(payload: ChatRequest):
    if payload.npc_id not in NPC_PROFILES:
        raise HTTPException(status_code=404, detail="NPC profile not found")
        
    profile = NPC_PROFILES[payload.npc_id]
    memory_manager = MEMORY_BANKS[payload.npc_id]
    
    historical_context = memory_manager.fetch_relevant_memories(payload.message)
    
    dynamic_system_instruction = f"""
    {profile["system_instruction"]}
    
    HISTORICAL CONTEXT MEMORIES:
    {historical_context}
    """

    try:
        response = client.messages.create(
            model="claude-fable-5",
            max_tokens=800,
            system=dynamic_system_instruction,
            messages=[{"role": "user", "content": payload.message}]
        )
        
        raw_text_output = "".join([block.text for block in response.content if hasattr(block, 'text')]).strip()
        
        # Defensive JSON parsing step
        try:
            return json.loads(raw_text_output)
        except json.JSONDecodeError:
            # Fallback Repair: If a string quote was cut off, try to append closing elements
            if not raw_text_output.endswith("}"):
                if not raw_text_output.endswith('"'):
                    raw_text_output += '"'
                raw_text_output += "}"
            return json.loads(raw_text_output)
            
    except Exception as e:
        # Gracefully handle validation failures without a hard 500 server drop
        return {
            "dialogue": "My thoughts are clouded... try addressing me again.",
            "emotion": "confused",
            "relationship_change": "No change (System Validation Bypass)"
        }

        
