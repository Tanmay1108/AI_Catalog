import asyncio
from services.g2_scraping_services import crawl_with_rows, crawl_with_product_name

async def crawl_g2_website(number_of_rows: int=0, product_name: str="") -> bool:
    if product_name != "":
        return await crawl_with_product_name(product_name=product_name)
    elif number_of_rows != 0:
        # return await crawl_with_rows(number_of_rows=number_of_rows)
        asyncio.create_task(crawl_with_rows(number_of_rows=number_of_rows))
        return True
    else:
        raise Exception("Please provide input") # 404 exception. add later