from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List
from rapidapi_client import RapidApiClient

app = FastAPI()

class Hotel(BaseModel):
    hotel_name: str
    min_total_price: float

class HotelListResponse(BaseModel):
    message: str
    results: List[Hotel]

@app.get("/hotels", response_model=HotelListResponse)
def find_hotels(city: str = Query(...), state: str = Query(...)):
    client = RapidApiClient()

    locations_response = client.locations(city, state)
    dest_id = locations_response.dest_id
    if not dest_id:
        return HotelListResponse(message=locations_response.message, results=[])
    
    search_response = client.search(dest_id)
    hotels = [
        Hotel(
            hotel_name=h.hotel_name,
            min_total_price=h.min_total_price
        ) for h in search_response.hotels
    ]
    return HotelListResponse(message=search_response.message, results=hotels)
