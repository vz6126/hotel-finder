from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List
from rapidapi_client import RapidApiClient

app = FastAPI()

class Hotel(BaseModel):
    name: str
    min_total_price: float

class HotelsResponse(BaseModel):
    message: str
    hotels: List[Hotel]

@app.get("/hotels", response_model=HotelsResponse)
def find_hotels(city: str = Query(...), state: str = Query(...)):
    client = RapidApiClient()

    locations_response = client.locations(city, state)
    dest_id = locations_response.dest_id
    if not dest_id:
        return HotelsResponse(message=locations_response.message, hotels=[])
    
    search_response = client.search(dest_id)
    hotels = [
        Hotel(
            name=h.name,
            min_total_price=h.min_total_price
        ) for h in search_response.hotels
    ]
    return HotelsResponse(message=search_response.message, hotels=hotels)
