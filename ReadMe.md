# SupaClear: AI Enterprise Software Platform Summarizer

## Problem Statement

SupaClear is a tool designed to collate and generate comprehensive one-page summaries of publicly available information on Artificial Intelligence and Machine Learning enterprise software platforms. The summaries include:

- Products and key features
- Platform differentiators
- Current clients and industries served
- Pricing information (where available)

## Key Features

- Web scraping of AI/ML software platform information
- Automated data collection from multiple sources
- Document storage in MongoDB
- LLM-powered summary generation
- PDF summary creation
- Proxy rotation for reliable web scraping

## Tech Stack

- Python
- FastAPI
- Selenium
- Beautiful Soup (bs4)
- MongoDB
- OpenAI/LLM Integration
- Dropbox (BLOB storage)

## Prerequisites

- Python 3.12
- MongoDB
- Dropbox Account
- OpenAI API Key
- Data Impulse Proxy Service Account

## Installation

```bash
# Clone the repository
git clone https://github.com/Tanmay1108/AI_Catalog.git
cd supaclear/app

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root with the following keys:

```
# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=supaclear

# Dropbox Configuration
DROPBOX_ACCESS_TOKEN=your_dropbox_access_token

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Data Impulse Proxy Configuration
DATA_IMPULSE_API_KEY=your_data_impulse_api_key
```

update the code to use these variables from your env file. 

## Running the Application

1. Start MongoDB server:
```bash
# On most systems
mongod
```

2. Run the FastAPI server:
```bash
# Run with Uvicorn
uvicorn main:app --reload
```

3. Access the API:
- Open your browser and navigate to `http://localhost:8000/docs`
- This will open the Swagger UI where you can interact with the APIs

## Available APIs

### G2 Scraper
- **Endpoint**: `/g2_scraper`
- **Method**: GET
- **Description**: Crawl G2 product website
- **Parameters**: 
  - `number_of_rows` (default: 5)
- **Returns**: Scraped product information

### Summary Generator
- **Endpoint**: `/summary_generator`
- **Method**: POST
- **Description**: Generate summaries for AI/ML platforms
- **Parameters**:
  - `number_of_rows` (default: 1)
- **Returns**: JSON-formatted summaries

### Summary PDF Generator
- **Endpoint**: `/summary_pdf_generator`
- **Method**: POST
- **Description**: Generate summaries and create PDFs
- **Parameters**:
  - `number_of_rows` (default: 1)
- **Returns**: PDF summaries

### Summary Generator with Fuzzy Query
- **Endpoint**: `/summary_generator_with_fq`
- **Method**: POST
- **Description**: Generate summaries with fuzzy query support
- **Parameters**:
  - `number_of_rows` (default: 1)
- **Returns**: PDF summaries with advanced querying

## Usage Example

1. Start by crawling G2 product website:
   - Hit `/g2_scraper` endpoint to collect platform data
2. Generate summaries:
   - Use `/summary_generator` for JSON summaries
   - Use `/summary_pdf_generator` for PDF summaries
   - Use `/summary_generator_with_fq` for advanced querying

## Future Improvements

- Exception handling framework
- Check API for async operations
- Database connection resilience
- Rollback mechanisms
- Get by product name feature
- Environment variable configuration
- Dockerization
- Expanded scraping capabilities

## Proxy and Scraping Considerations

- Uses Data Impulse for IP rotation
- Handles website blocking through sophisticated scraping techniques
- Configurable batch processing for URL scraping

## Limitations

- Currently limited to scraping up to page 16
- Requires paid proxy service for full functionality
- PDF generation requires Dropbox integration

## Contributing

Contributions are welcome! Please read the contributing guidelines and submit pull requests.


For more information please read the detailed document here: 
https://docs.google.com/document/d/13I8l2k0QlFUzyFOQK6-yk3MFIx7tWC4265KQ8m9f2yI/edit?tab=t.0