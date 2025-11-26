import os
import json
from typing import Optional, Any, Dict, List
from dataclasses import asdict
from backend.models.core import ResearchDossier, Challenge

class SessionStore:
    def __init__(self, base_path: str = "./data/sessions"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)
        
    def _get_path(self, session_id: str, filename: str) -> str:
        session_dir = os.path.join(self.base_path, session_id)
        os.makedirs(session_dir, exist_ok=True)
        return os.path.join(session_dir, filename)

    def save_dossier(self, session_id: str, dossier: ResearchDossier) -> None:
        path = self._get_path(session_id, "dossier.json")
        with open(path, "w") as f:
            json.dump(asdict(dossier), f, indent=2)

    def get_dossier(self, session_id: str) -> Optional[ResearchDossier]:
        path = self._get_path(session_id, "dossier.json")
        if not os.path.exists(path):
            return None
        
        with open(path, "r") as f:
            data = json.load(f)
            return ResearchDossier(**data)
            
    # We can also store a cached deck summary here if needed
    def save_deck_summary(self, session_id: str, summary: str) -> None:
        path = self._get_path(session_id, "deck_summary.txt")
        with open(path, "w") as f:
            f.write(summary)
            
    def get_deck_summary(self, session_id: str) -> Optional[str]:
        path = self._get_path(session_id, "deck_summary.txt")
        if not os.path.exists(path):
            return None
        with open(path, "r") as f:
            return f.read()

    def save_interaction(self, session_id: str, interaction: Dict[str, Any]) -> None:
        path = self._get_path(session_id, "history.json")
        history = []
        if os.path.exists(path):
            with open(path, "r") as f:
                try:
                    history = json.load(f)
                except json.JSONDecodeError:
                    history = []
        
        history.append(interaction)
        
        with open(path, "w") as f:
            json.dump(history, f, indent=2)

    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        path = self._get_path(session_id, "history.json")
        if not os.path.exists(path):
            return []
        
        with open(path, "r") as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                return []
            except json.JSONDecodeError:
                return []
    def save_challenges(self, session_id: str, challenges: List[Challenge]) -> None:
        path = self._get_path(session_id, "challenges.json")
        existing_challenges = []
        if os.path.exists(path):
            with open(path, "r") as f:
                try:
                    existing_challenges = json.load(f)
                except json.JSONDecodeError:
                    pass
        
        # Append new challenges
        existing_challenges.extend([asdict(c) for c in challenges])
        
        with open(path, "w") as f:
            json.dump(existing_challenges, f, indent=2)

    def get_challenge(self, session_id: str, challenge_id: str) -> Optional[Challenge]:
        path = self._get_path(session_id, "challenges.json")
        if not os.path.exists(path):
            return None
            
        with open(path, "r") as f:
            try:
                data = json.load(f)
                for item in data:
                    if item.get("id") == challenge_id:
                        return Challenge(**item)
            except json.JSONDecodeError:
                return None
        return None
