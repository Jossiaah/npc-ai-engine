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
    
    #Ask ChromaDB to query its vector index for past interactions matching the new prompt
    historical_context = memory_manager.fetch_relevant_memories(payload.message)
    
    #Inject those long-term context memories straight into the system instructions
    dynamic_system_instruction = f"""
    {profile["system_instruction"]}
    
    HISTORICAL CONTEXT MEMORIES (Use these to adjust your behavior if the player references past events):
    {historical_context}
    """

    try:
        response = client.messages.create(
            model="claude-fable-5",
            max_tokens=250,
            system=dynamic_system_instruction,
            messages=[{"role": "user", "content": payload.message}]
        )
        
        raw_text_output = "".join([block.text for block in response.content if hasattr(block, 'text')])
        parsed_json_output = json.loads(raw_text_output)
        
        #Save this interaction into our Vector Space database so it can be recalled later
        interaction_id = str(uuid.uuid4())
        memory_manager.store_memory(
            player_statement=payload.message,
            npc_response=parsed_json_output["dialogue"],
            memory_id=interaction_id
        )
        
        return parsed_json_output
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
