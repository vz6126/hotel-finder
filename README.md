# Hotel Finder

A Python project to search for hotels using the Booking.com API via RapidAPI. Provides both a command-line interface (CLI) and a REST API (FastAPI).

## Features
- Search for hotels in a given city and state in the United States
- Filter out hostels and sold-out properties
- Save API responses for debugging (optional)
- REST API endpoint for integration
- CLI for quick terminal usage

## Requirements
- Python 3.8+
- See `requirements.txt` for dependencies

## Setup
1. Clone the repository or download the files.
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Set your RapidAPI key as an environment variable:
   - On Windows (Powershell):
     ```powershell
     $env:RAPIDAPI_KEY = "your_rapidapi_key_here"
     ```
   - On Linux/macOS (bash):
     ```bash
     export RAPIDAPI_KEY="your_rapidapi_key_here"
     ```

## Usage

### CLI
Run the CLI to search for hotels in a specific city and state (e.g., Sacramento, California):
```powershell
python hotel_finder_cli.py Sacramento California
```

### REST API
Start the FastAPI server:
```powershell
python -m uvicorn hotel_finder_api:app --reload
```

Then open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for interactive API documentation.

#### Example API Call
```
GET /hotels?city=Sacramento&state=California
```

## Project Structure
- `rapidapi_client.py` - Core API client logic
- `hotel_finder_cli.py` - Command-line interface
- `hotel_finder_api.py` - FastAPI REST API
- `config.json` - Your API key (not included in version control)
- `requirements.txt` - Python dependencies

## License
MIT License
