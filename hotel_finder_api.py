from datetime import date, timedelta
import urllib.parse, json
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional
from rapidapi_client import RapidApiClient

app = FastAPI()

class Hotel(BaseModel):
    hotel_name: str
    min_total_price: float
    soldout: int
    accommodation_type_name: Optional[str] = None

@app.get("/hotels")
def find_hotels(city: str = Query(...), state: str = Query(...)):
    client = RapidApiClient(debug=False)

    res = client.locations(city, state)
    dest_id = res.get("dest_id")
    if not dest_id:
        return {"message": res.get("message"), "results": []}
    
    res = client.search(dest_id)
    results = res.get("results", [])
    hotels = [
        {
            "hotel_name": h["hotel_name"],
            "min_total_price": h["min_total_price"]
        } for h in results
    ]
    return {"message": res.get("message", ""), "results": hotels}
