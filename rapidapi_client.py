#!/usr/bin/env python3
"""
Hotel search API caller script
This script calls the Booking.com API to search for hotels
"""

import http.client
import json
from datetime import date, timedelta
import os
import urllib.parse

class RapidApiClient:
    def __init__(self, debug=False):
        RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "Error: RAPIDAPI_KEY not set")
        self.headers = {
            'x-rapidapi-key': RAPIDAPI_KEY,
            'x-rapidapi-host': "booking-com.p.rapidapi.com"
        }
        self.conn = http.client.HTTPSConnection("booking-com.p.rapidapi.com")
        self.debug = debug
        self.debug_folder = 'logs'

    def _save_response(self, filename, json_data):
        if self.debug:
            os.makedirs(self.debug_folder, exist_ok=True)
            with open(f'{self.debug_folder}/{filename}', 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)

    def _debug(self, message):
        if self.debug:
            print(message)

    class LocationsResponse:
        def __init__(self, message: str, dest_id: str | None):
            self.message = message
            self.dest_id = dest_id

    def locations(self, city, state) -> "RapidApiClient.LocationsResponse":
        try:
            params = {
                'name': city,
                'locale': 'en-us'
            }
            encoded_params = urllib.parse.urlencode(params)
            url = f"/v1/hotels/locations?{encoded_params}"
            self.conn.request("GET", url, headers=self.headers)
            data = self.conn.getresponse().read()

            all = json.loads(data.decode("utf-8"))
            self._save_response("locations-orig.json", all)
            if isinstance(all, dict):
                raise ValueError(all.get('message', 'Unknown error'))

            filtered = [entry for entry in all \
                        if entry.get("dest_type") == "city" \
                        and entry.get("country") == 'United States' \
                        and entry.get("region") == state \
                        and entry.get("city_name") == city]
            self._save_response("locations-filtered.json", filtered)

            if len(filtered) == 1:
                message = f"Success: found {filtered[0]['label']} with dest_id={filtered[0]['dest_id']}"
                dest_id = filtered[0]['dest_id']
            elif len(filtered) != 1:
                message = f"Error: found {len(filtered)} locations for {city}, {state}\n"
                for i, entry in enumerate(filtered):
                    message += f"{i}: {entry['label']} with dest_id={entry['dest_id']}\n"
                dest_id = None
        except Exception as e:
            message = f"Error: {e}"
            dest_id = None

        return RapidApiClient.LocationsResponse(message, dest_id)

    class SearchResponse:
        def __init__(self, message: str, hotels: list["RapidApiClient.Hotel"]):
            self.message = message
            self.hotels = hotels

    class Hotel:
        def __init__(self, name: str, min_total_price: float):
            self.name = name
            self.min_total_price = min_total_price

    def search(self, dest_id, checkin_date=None) -> "RapidApiClient.SearchResponse":
        if checkin_date is None:
            checkin_date = date.today()
        checkout_date = checkin_date + timedelta(days=1)

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
            'checkin_date': str(checkin_date),
            'checkout_date': str(checkout_date)
        }

        encoded_params = urllib.parse.urlencode(params)
        url = f"/v1/hotels/search?{encoded_params}"
        self.conn.request("GET", url, headers=self.headers)
        data = self.conn.getresponse().read()
        d = json.loads(data.decode("utf-8"))
        self._save_response("search-orig.json", d)

        all = d.get("result", [])
        not_hostels = [h for h in all if h.get("accommodation_type_name") != "Hostel"]
        self._debug(f'Removed {len(all)-len(not_hostels)} hostels')

        available = [h for h in not_hostels if h.get("soldout") == 0]
        self._debug(f'Removed {len(not_hostels)-len(available)} sold out')

        available.sort(key=lambda x: x["min_total_price"])
        self._save_response("search-processed.json", available)

        return RapidApiClient.SearchResponse(
            message=f'Found {len(available)} available hotels and motels for {checkin_date}.',
            hotels=[
                RapidApiClient.Hotel(
                    name=h["hotel_name"],
                    min_total_price=h["min_total_price"]
                ) for h in available
            ]
        )
