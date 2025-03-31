from fastapi import APIRouter, Query, HTTPException
from pydantic import ValidationError
from app.backend import SearchEngine
import uuid

from app.schemas.search_engine_data import SearchEngineModel, SearchEngineData


api_router = APIRouter()

data_path = "../data/news_articles.xlsx"
dense_llm_model = "nli-bert-large-max-pooling"
# Additional Data
enrich_data_url = None
se = SearchEngine(dense_llm_model, data_path)
# Load LLM embeddings
se.initialize_dense_retriever()


@api_router.get("/search/", status_code=200, response_model=SearchEngineModel)
def search_news(query: str = Query(..., description="Search query text")):
    request_id = str(uuid.uuid4())
    try:
        data = se.search_engine(query)
        #validate_output = SearchEngineData(**data)
        code = 200
        message = "Success"
    except ValidationError as e:
        print(f"Error {e}")
        raise HTTPException(
            status_code=500, detail="Internal Server Error"
        )

    return {"code": code, "message": message, "data": data, "request_id": request_id}





