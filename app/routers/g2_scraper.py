#this should ideally be a cron job, that was increasing the scope so creating an API for now.

from fastapi import APIRouter
from managers.g2_scraping_manager import crawl_g2_website

router = APIRouter()


@router.get("/g2_scraper")
async def crawl_g2_prod_website():
    return await crawl_g2_website(number_of_rows=5)