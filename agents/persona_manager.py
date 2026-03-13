import os
import re
from typing import Dict, Optional, List
from loguru import logger

class PersonaManager:
    """
    Manages specialized agent personas from the agency-agents library.
    Parses Markdown files to extract system instructions.
    """
    def __init__(self, external_path: str = "external/agency-agents"):
        self.base_path = external_path
        self.personas: Dict[str, str] = {}
        self._load_all_personas()

    def _load_all_personas(self):
        if not os.path.exists(self.base_path):
            logger.warning(f"Persona library not found at {self.base_path}")
            return

        for root, _, files in os.walk(self.base_path):
            for file in files:
                if file.endswith(".md"):
                    persona_name = file.replace(".md", "")
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            # Clean up content (strip frontmatter if exists, extract main instructions)
                            self.personas[persona_name] = self._clean_persona_content(content)
                    except Exception as e:
                        logger.error(f"Failed to load persona {persona_name}: {e}")
        
        logger.info(f"Loaded {len(self.personas)} expert personas from library.")

    def _clean_persona_content(self, content: str) -> str:
        # Remove potential YAML frontmatter
        content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)
        return content.strip()

    def get_persona(self, persona_name: str) -> Optional[str]:
        """Retrieve the system instructions for a specific persona."""
        return self.personas.get(persona_name)

    def list_available_personas(self) -> List[str]:
        return list(self.personas.keys())
