#!/usr/bin/env python3
"""
CLI entry point for hotel finder using RapidApiClient
"""
from rapidapi_client import RapidApiClient

def main():
    client = RapidApiClient(save_responses=True)
    
    res = client.locations("Houston", "Texas")
    print(res["message"])
    dest_id = res["dest_id"]
    if not dest_id:
        return
    
    res = client.search(dest_id)
    print(res["message"])
    for h in res["results"]:
        print(f'{h["index"]:>2}. {h["hotel_name"]} {h["min_total_price"]}')


if __name__ == "__main__":
    main()
