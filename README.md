### 1. Scraping Module (`scrap.py`)
Handles individual movie review scraping from IMDb.

**Key Features:**
- Converts TMDb IDs to IMDb IDs
- Scrapes reviews using Selenium WebDriver
- Preprocesses HTML content
- Handles Unicode and HTML entity decoding
- Saves reviews to text files

**Requirements:**
- Selenium WebDriver
- ChromeDriver (path: `/home/ran/chromedriver`)
- BeautifulSoup4
- Requests

### 2. Batch Scraping (`scrap_all.py`)
Manages batch scraping of multiple movies.

**Key Features:**
- Reads movie data from CSV file
- Implements retry mechanism (3 attempts per movie)
- Handles failures gracefully
- Includes delay between requests
- Tracks failed movies

**Usage:**
bash
python scrap_all.py # Starts batch scraping from index 333


### 3. Review Analysis API (`store_collections.py`)
Flask API for storing and querying movie reviews using vector embeddings.

**Key Features:**
- Vector store using ChromaDB
- LLaMA Index for embeddings and querying
- RESTful API endpoints
- CORS support for cross-origin requests

**API Endpoints:**
- POST `/api/chat/initialize`: Initialize chat context for a movie
- POST `/api/chat/query`: Query movie reviews

**Requirements:**
- ChromaDB
- LlamaIndex
- Ollama
- Flask
- Flask-CORS

## Setup

1. Install dependencies:
bash
pip install selenium beautifulsoup4 requests pandas chromadb llama-index flask flask-cors playwright


2. Install Ollama and required models:
bash
Install Ollama
curl https://ollama.ai/install.sh | sh
Pull required models
ollama pull llama3.1:8b
ollama pull mxbai-embed-large:latest


3. Configure ChromeDriver:
- Download ChromeDriver
- Place it in `/home/ran/chromedriver`
- Make it executable: `chmod +x /home/ran/chromedriver`

## Usage

1. Start scraping reviews:
bash
python scrap_all.py


2. Start the API server:
bash
python store_collections.py

![alt text](image.png)


## Notes
- The API server runs on port 5001
- CORS is configured to allow requests from localhost:3000
- Review scraping includes retry mechanism with delays
- Vector store uses top-5 similar reviews for answering queries

## Error Handling
- Failed scraping attempts are logged in `data/failed_reviews.txt`
- API endpoints return appropriate error messages and status codes
- Scraping includes 3 retry attempts per movie

## Cross-Origin Support
The API supports cross-origin requests from:
- http://localhost:3000
- http://127.0.0.1:3000

For production, update CORS settings in `store_collections.py` with appropriate origins.
"""
