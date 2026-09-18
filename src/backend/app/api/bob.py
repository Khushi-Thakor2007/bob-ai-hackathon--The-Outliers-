from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.schemas import BobQueryRequest, BobQueryResponse
from app.ai.bob import BobAssistant

router = APIRouter(prefix="/bob", tags=["Bob AI Assistant"])

@router.post("/query", response_model=BobQueryResponse)
def query_bob_assistant(req: BobQueryRequest, db: Session = Depends(get_db)):
    result = BobAssistant.process_query(req.query, db)
    return BobQueryResponse(**result)
