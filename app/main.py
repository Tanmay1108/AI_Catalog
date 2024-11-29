from fastapi import FastAPI
from routers import g2_scraper
from routers import summary
from dropbox_helper import dbx #for initiating connection

app = FastAPI()


app.include_router(g2_scraper.router, tags=["Scraping"])

app.include_router(summary.router, tags=["Summary"])


