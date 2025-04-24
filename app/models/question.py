from pydantic import BaseModel

class QuestionResponse(BaseModel):
    """Response model for question answers"""
    answer: str
    confidence: float
    source: str 