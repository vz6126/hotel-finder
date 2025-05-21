#!/usr/bin/env python3
"""
Hotel search API caller script
This script calls the Booking.com API to search for hotels
"""

import http.client
import json
from datetime import date, timedelta
import urllib.parse

class RapidApiClient:
    def __init__(self, config_path="config.json", save_responses=False):
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        self.headers = {
            'x-rapidapi-key': config["RAPIDAPI_KEY"],
            'x-rapidapi-host': "booking-com.p.rapidapi.com"
        }
        self.conn = http.client.HTTPSConnection("booking-com.p.rapidapi.com")
        self.save_responses = save_responses

    def _save_response(self, filename, json_data):
        if self.save_responses:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)

    def locations(self, city, state):
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

        filtered = [entry for entry in all \
                    if entry.get("dest_type") == "city" \
                    and entry.get("country") == 'United States' \
                    and entry.get("region") == state]
        self._save_response("locations-filtered.json", filtered)

        if len(filtered) == 1:
            print(f"Found {filtered[0]['label']} with dest_id={filtered[0]['dest_id']}")
            return filtered[0]['dest_id']
        elif len(filtered) > 1:
            print(f"Error: found {len(filtered)} locations for {city}, {state}")
            for i, entry in enumerate(filtered):
                print(f"{i}: {entry['label']} with dest_id={entry['dest_id']}")
            return 'location-ambiguous'
        else:
            print(f"Error: found no locations for {city}, {state}")
            return 'location-not-found'

    def search(self, dest_id):
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
        self.conn.request("GET", url, headers=self.headers)
        data = self.conn.getresponse().read()
        d = json.loads(data.decode("utf-8"))
        self._save_response("search-orig.json", d)

        all = d.get("result", [])
        not_hostels = [h for h in all if h.get("accommodation_type_name") != "Hostel"]
        print(f'Removed {len(all)-len(not_hostels)} hostels')

        available = [h for h in not_hostels if h.get("soldout") == 0]
        print(f'Removed {len(not_hostels)-len(available)} sold out')

        print(f'Found {len(available)} available hotels and motels:')
        for i, h in enumerate(available):
            print(f'{i+1:>2}. {h["hotel_name"]} {h["min_total_price"]}')


if __name__ == "__main__":
    client = RapidApiClient(save_responses=True)
    dest_id = client.locations("Houston", "Texas")
    client.search(dest_id)
