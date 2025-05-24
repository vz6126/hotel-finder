import os
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional
from rapidapi_client import RapidApiClient
from fastapi.openapi.utils import get_openapi
from datetime import date

app = FastAPI(
    title="Hotel Search API",
    version="0.0.1",
    description="Booking.com–backed hotel lookup"
)    

class Hotel(BaseModel):
    name: str
    min_total_price: float

class HotelsResponse(BaseModel):
    message: str
    hotels: List[Hotel]

@app.get("/hotels", response_model=HotelsResponse)
def find_hotels(
    city: str = Query(...),
    state: str = Query(...),
    checkin_date: Optional[date] = Query(None, description="Check-in date (format: YYYY-MM-DD)")
):
    client = RapidApiClient()

    locations_response = client.locations(city, state)
    dest_id = locations_response.dest_id
    if not dest_id:
        return HotelsResponse(message=locations_response.message, hotels=[])
    
    search_response = client.search(dest_id, checkin_date)
    hotels = [
        Hotel(
            name=h.name,
            min_total_price=h.min_total_price
        ) for h in search_response.hotels
    ]
    return HotelsResponse(message=search_response.message, hotels=hotels)


def custom_openapi():
    # Generate the standard schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    # Inject the servers list
    openapi_schema["servers"] = [{
        "url": os.getenv("BASE_URL", "https://hotel-finder-h3c5.onrender.com"), 
        "description": "Production" 
    }]
    return openapi_schema

app.openapi = custom_openapi

@app.get("/ai-plugin.json", include_in_schema=False)
async def plugin_manifest():
    return {
  "schema_version": "v1",
  "name_for_human": "Hotel Search",
  "name_for_model": "hotel_search",
  "description_for_human": "Search hotels via Booking.com (RapidAPI)",
  "description_for_model": "Use this to look up hotels by city, state, and check-in date. If no check-in date is provided, it defaults to today.",
  "auth": {
    "type": "none"
  },
  "api": {
    "type": "openapi",
    "url": "https://hotel-finder-h3c5.onrender.com/openapi.json",
    "has_user_authentication": False
  }
}
