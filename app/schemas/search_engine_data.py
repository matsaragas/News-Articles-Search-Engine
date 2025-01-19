from pydantic import BaseModel
from typing import List, Dict


class SearchEngineModel(BaseModel):
    code: int
    message: str
    data: Dict
    request_id: str


class SearchEngineData(BaseModel):
    search_dict: List[Dict]