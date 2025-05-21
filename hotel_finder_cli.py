#!/usr/bin/env python3
"""
CLI entry point for hotel finder using RapidApiClient
"""
from rapidapi_client import RapidApiClient
import sys

def main(city, state):
    client = RapidApiClient(debug=True)

    locations_response = client.locations(city, state)
    print(locations_response.message)
    dest_id = locations_response.dest_id
    if not dest_id:
        return
    
    search_response = client.search(dest_id)
    print(search_response.message)
    for i, h in enumerate(search_response.hotels):
        print(f'{i+1:>2}. {h.name} {h.min_total_price}')


if __name__ == "__main__":
    if len(sys.argv) == 3:
        city = sys.argv[1]
        state = sys.argv[2]
        main(city, state)
    else:
        print("Usage: python hotel_finder_cli.py <city> <state>")
