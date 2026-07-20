import os
import chromadb
from chromadb.config import Settings

class NPCMemoryManager:
    def __init__(self, npc_id: str):
        self.npc_id = npc_id
        self.chroma_client = chromadb.PersistentClient(path="./cofig/chroma_db")
        self.collection = self.chroma_client.get_or_create_collection(
            name=f"npc_memory_{npc_id}"
        )

    def store_memory(self, player_statement: str, npc_response: str, memory_id: str):
        """Saves a conversational event segment into semantic vector space."""
        combined_interaction = f"Player said: {player_statement} | NPC responded: {npc_response}"
        
        self.collection.add(
            documents=[combined_interaction],
            metadatas=[{"speaker": self.npc_id, "type": "dialogue"}],
            ids=[memory_id]
        )
    
    def fetch_relevant_memories(self, current_input: str, max_results: int = 2) -> str:
        """Queries vector index arrays to pull context matching what the player just stated."""
        results = self.collection.query(
            query_texts= [current_input],
            n_results=max_results
        )

        if not results or not results['documents'] or len(results['documents'][0]) == 0:
            return "No previous memories or contexual interactions found."
        
        return "\n".join(results['documents'][0])