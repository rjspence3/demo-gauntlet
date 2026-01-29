"""
Module for generating challenger avatars.
"""
import os
import random
from typing import Dict, Protocol, Optional

class ImageProvider(Protocol):
    """Protocol for image generation providers."""
    def generate_image(self, prompt: str) -> str:
        """Generate an image from a prompt."""
        ...

class MockImageProvider:
    """Mock image provider for testing."""
    def generate_image(self, prompt: str) -> str:
        """Return a mock image path."""
        return "/avatars/default.png"

class AvatarGenerator:
    """
    Generates avatars for challenger personas.
    """
    def __init__(self, assets_dir: str = "frontend/public/avatars", provider: Optional[ImageProvider] = None):
        """
        Initialize the AvatarGenerator.
        """
        self.assets_dir = assets_dir
        self.provider = provider or MockImageProvider()

    def generate_avatar_set(self, persona_id: str, style: str) -> Dict[str, str]:
        """
        Generates a set of avatars for different emotions/states.
        Returns a dictionary mapping state to image URL/path.
        """
        states = ["neutral", "skeptical", "impressed", "thoughtful"]
        avatars = {}
        
        base_url = "/avatars" # Relative to frontend public dir
        
        for state in states:
            # For MVP, we'll just use a generic placeholder or a specific file if it exists
            # e.g., /avatars/skeptic_neutral.png
            
            # Check if specific file exists (mock check)
            filename = f"{persona_id}_{state}.png"
            # file_path = os.path.join(self.assets_dir, filename)
            
            # For now, return the expected URL path
            avatars[state] = f"{base_url}/{filename}"
            
        return avatars

    def generate_single_avatar(self, prompt: str) -> str:
        """
        Generates a single avatar image from a prompt.
        """
        return self.provider.generate_image(prompt)
