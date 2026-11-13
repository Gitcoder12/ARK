from pydantic import BaseModel


class AIEntity(BaseModel):
    """
    Represents a synthetic consciousness with replaceable cognitive components.
    Used to simulate the 'Ship of Theseus' problem in AI alignment.
    """

    name: str
    # The "brain" components
    memory_core: list[str]
    logic_core: dict[str, float]
    personality_vector: float

    def respond_to_stimulus(self, stimulus: str) -> str:
        """
        Simulates how the entity behaves based on its current internal state.
        This is the behavioral signature we use to measure identity drift.
        """
        if stimulus in self.memory_core:
            return (
                f"I remember {stimulus}. "
                f"My personality dictates a response of {self.personality_vector}."
            )
        return f"I don't remember {stimulus}."
