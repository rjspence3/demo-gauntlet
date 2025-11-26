from fastapi import APIRouter, HTTPException, Depends
from backend.research.agent import ResearchAgent
from backend.models.core import ResearchDossier
from backend.models.llm import OpenAILLM, MockLLM, LLMClient
from backend.research.client import MockSearchClient
from backend.config import config

from backend.models.session import SessionStore

router = APIRouter(prefix="/research", tags=["research"])
session_store = SessionStore()

def get_agent() -> ResearchAgent:
    # Factory for agent, can inject dependencies here
    # For MVP, check for keys
    llm: LLMClient
    if config.OPENAI_API_KEY:
        llm = OpenAILLM(api_key=config.OPENAI_API_KEY)
    else:
        llm = MockLLM()
        
    # Check for search key (not yet in config, but placeholder)
    # if config.BRAVE_API_KEY:
    #     search = BraveSearchClient(api_key=config.BRAVE_API_KEY)
    # else:
    search = MockSearchClient()
    
    return ResearchAgent(llm_client=llm, search_client=search)

@router.post("/generate/{session_id}", response_model=ResearchDossier)
async def generate_research(session_id: str, agent: ResearchAgent = Depends(get_agent)) -> ResearchDossier:
    """
    Generates a research dossier for a given session.
    """
    # TODO: Fetch session metadata from store
    deck_title = "Demo Deck"
    tags = ["general"]
    
    # Generate research
    try:
        dossier = agent.run(session_id, deck_title, tags)
        
        # Save to session store
        session_store.save_dossier(session_id, dossier)
        
        return dossier
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research generation failed: {str(e)}") from e
