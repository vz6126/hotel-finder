#!/usr/bin/env python3
"""
CLI entry point for hotel finder using RapidApiClient
"""
from rapidapi_client import RapidApiClient

if __name__ == "__main__":
    client = RapidApiClient(save_responses=True)
    dest_id = client.locations("Houston", "Texas")
    client.search(dest_id)
