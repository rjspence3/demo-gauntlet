import dspy

class PersonaResponse(dspy.Signature):
    """Respond to a challenge question as a specific executive persona (CTO, CFO, etc).
    
    You must adopt the persona's perspective, goals, and fears. 
    Use the provided deck evidence to defend the proposal or address the challenge grounded in facts.
    """
    
    persona_context = dspy.InputField(desc="The role, goals, and specific fears/objections of the persona.")
    challenge_question = dspy.InputField(desc="The specific question or objection raised against the proposal.")
    deck_evidence = dspy.InputField(desc="Relevant facts and excerpts from the presentation deck.")
    
    response = dspy.OutputField(desc="The verbal response to the challenge, optimizing for accuracy, clarity, and completeness.")

class GauntletAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        # ChainOfThought forces the model to plan before speaking, 
        # often increasing 'Accuracy' and 'Truth Alignment' scores.
        self.prog = dspy.ChainOfThought(PersonaResponse)
        
    def forward(self, persona_context, challenge_question, deck_evidence):
        return self.prog(
            persona_context=persona_context, 
            challenge_question=challenge_question, 
            deck_evidence=deck_evidence
        )
        
    @classmethod
    def from_file(cls, path: str) -> 'GauntletAgent':
        """Load an optimized agent from a JSON file."""
        agent = cls()
        agent.load(path)
        return agent
