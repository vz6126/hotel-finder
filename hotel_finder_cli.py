#!/usr/bin/env python3
"""
CLI entry point for hotel finder using RapidApiClient
"""
from rapidapi_client import RapidApiClient
import sys
from datetime import date, datetime

def main(city, state, checkin_date):
    client = RapidApiClient(debug=True)

    locations_response = client.locations(city, state)
    print(locations_response.message)
    dest_id = locations_response.dest_id
    if not dest_id:
        return
    
    search_response = client.search(dest_id, checkin_date)
    print(search_response.message)
    for i, h in enumerate(search_response.hotels):
        print(f'{i+1:>2}. {h.name} {h.min_total_price}')


if __name__ == "__main__":
    if len(sys.argv) not in [3, 4]:
        print("Usage: python hotel_finder_cli.py <city> <state> [check-in date (YYYY-MM-DD)]")
        exit(0)

    city = sys.argv[1]
    state = sys.argv[2]
    checkin_date = date.today()
    if len(sys.argv) == 4:
        try:
            checkin_date = datetime.strptime(sys.argv[3], "%Y-%m-%d").date()
        except ValueError:
            print("Error: Check-in date must be in YYYY-MM-DD format")
            sys.exit(1)
            
    main(city, state, checkin_date)
