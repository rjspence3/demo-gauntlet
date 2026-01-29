
import dspy

class StandardPromptSignature(dspy.Signature):
    """
    You are an expert roleplay simulator for startup pitch practice.
    
    Task:
    1. Adopt the specific 'Persona Context' provided below (e.g., specific role, personality patterns, hidden agenda).
    2. Analyze the 'Challenge Question' posed by this persona.
    3. Review the 'Deck Evidence' (facts from the presentation).
    4. Formulate a verbal response that:
       - Is in-character for the persona.
       - Is technically accurate based *only* on the Deck Evidence.
       - Directly addresses the core objection.
       - Is concise and convincing.

    Do not hallucinate facts outside the evidence. Maintain the persona's tone (skeptical, impatient, etc).
    """
    
    persona_context = dspy.InputField(desc="The role, personality, and constraints of the character.")
    challenge_question = dspy.InputField(desc="The question asked by the character.")
    deck_evidence = dspy.InputField(desc="Reference material from the slideshow.")
    
    response = dspy.OutputField(desc="The character-aligned response.")

class StandardAgent(dspy.Module):
    """
    Represents a 'Standard' good prompt engineering approach.
    Uses a detailed system prompt (Instructions in Signature) and Zero-Shot inference.
    """
    def __init__(self):
        super().__init__()
        # Standard approach often uses Chain of Thought implicitly or explicitly
        # We use dspy.Predict to simulate a standard 'One Shot' or 'Zero Shot' prompt 
        # without the DSPy optimizer's few-shot selection.
        self.prog = dspy.ChainOfThought(StandardPromptSignature)
        
    def forward(self, persona_context, challenge_question, deck_evidence):
        return self.prog(
            persona_context=persona_context,
            challenge_question=challenge_question,
            deck_evidence=deck_evidence
        )
