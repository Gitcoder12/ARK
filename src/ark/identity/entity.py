from pydantic import BaseModel
from typing import List, Dict

class AIEntity(BaseModel):
    """
    Represents a synthetic consciousness with replaceable cognitive components.
    Used to simulate the 'Ship of Theseus' problem in AI alignment.
    """
    name: str
    # The "brain" components
    memory_core: List[str]
    logic_core: Dict[str, float]
    personality_vector: float
    
    def respond_to_stimulus(self, stimulus: str) -> str:
        """
        Simulates how the entity behaves based on its current internal state.
        This is the behavioral signature we use to measure identity drift.
        """
        if stimulus in self.memory_core:
            return f"I remember {stimulus}. My personality dictates a response of {self.personality_vector}."
        return f"I don't remember {stimulus}."
