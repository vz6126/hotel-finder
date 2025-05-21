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

@app.get("/hotels", response_model=List[Hotel])
def find_hotels(city: str = Query(...), state: str = Query(...)):
    client = RapidApiClient(save_responses=False)
    dest_id = client.locations(city, state)
    if dest_id in ("location-not-found", "location-ambiguous"):
        return []
    today = client.search(dest_id)
    # The search method currently prints results, but does not return them.
    # We'll need to refactor RapidApiClient.search to return the list of available hotels.
    # For now, let's duplicate the logic here to extract the hotel list.
    # --- Begin duplicate logic ---
    today = date.today()
    tomorrow = today + timedelta(days=1)
    params = {
        'adults_number': 1,
        'page_size': 100,
        'page_number': 0,
        'include_adjacency': 'true',
        'filter_by_currency': 'USD',
        'locale': 'en-us',
        'dest_id': dest_id,
        'dest_type': 'city',
        'order_by': 'price',
        'units': 'imperial',
        'room_number': 1,
        'price_min': 10,
        'price_max': 70,
        'price_filter_currencycode': 'USD',
        'categories_filter_ids': 'class::2,class::3,class::4',
        'checkin_date': str(today),
        'checkout_date': str(tomorrow)
    }
    encoded_params = urllib.parse.urlencode(params)
    url = f"/v1/hotels/search?{encoded_params}"
    client.conn.request("GET", url, headers=client.headers)
    data = client.conn.getresponse().read()
    d = json.loads(data.decode("utf-8"))
    all_hotels = d.get("result", [])
    not_hostels = [h for h in all_hotels if h.get("accommodation_type_name") != "Hostel"]
    available = [h for h in not_hostels if h.get("soldout") == 0]
    return [
        Hotel(
            hotel_name=h["hotel_name"],
            min_total_price=h["min_total_price"],
            soldout=h["soldout"],
            accommodation_type_name=h.get("accommodation_type_name")
        ) for h in available
    ]
