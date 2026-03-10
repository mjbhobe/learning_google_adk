"""schemas.py - common schema to share date between agents"""

from pydantic import BaseModel


class TravelRequest(BaseModel):
    destination: str
    start_date: str
    end_date: str
    budget: float
