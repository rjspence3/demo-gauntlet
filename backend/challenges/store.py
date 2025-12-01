import json
import os
from typing import List, Optional, Dict
from backend.models.core import ChallengerPersona

class ChallengerStore:
    def __init__(self, data_path: str = "data/challengers.json"):
        self.data_path = data_path
        self._ensure_data_file()

    def _ensure_data_file(self):
        if not os.path.exists(self.data_path):
            os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
            with open(self.data_path, "w") as f:
                json.dump([], f)

    def list_personas(self) -> List[ChallengerPersona]:
        with open(self.data_path, "r") as f:
            data = json.load(f)
        return [ChallengerPersona(**p) for p in data]

    def get_persona(self, persona_id: str) -> Optional[ChallengerPersona]:
        personas = self.list_personas()
        for p in personas:
            if p.id == persona_id:
                return p
        return None

    def add_persona(self, persona: ChallengerPersona) -> None:
        personas = self.list_personas()
        # Check for duplicate ID
        if any(p.id == persona.id for p in personas):
            raise ValueError(f"Persona with ID {persona.id} already exists.")
        
        personas.append(persona)
        self._save_personas(personas)

    def update_persona(self, persona_id: str, updates: Dict) -> Optional[ChallengerPersona]:
        personas = self.list_personas()
        for i, p in enumerate(personas):
            if p.id == persona_id:
                # Apply updates
                updated_data = p.__dict__.copy()
                updated_data.update(updates)
                updated_persona = ChallengerPersona(**updated_data)
                personas[i] = updated_persona
                self._save_personas(personas)
                return updated_persona
        return None

    def _save_personas(self, personas: List[ChallengerPersona]):
        with open(self.data_path, "w") as f:
            json.dump([p.__dict__ for p in personas], f, indent=2)
