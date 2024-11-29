import asyncio
import logging as log
from db import db, fetch_n_rows
from services.summary_service import generate_summary_from_llm

collection = db["supaclear"]

async def generate_summary(number_of_rows: int = 1, generate_pdf: bool = False):
    """This method is only responsible for generating summaries for the given n rows. 
    these n rows are from database which are indexed as per the indexing algorithm i.e. date created

    Args:
        number_of_rows (int, optional): number of rows for which summary is required to be created. Defaults to 1.
    """
    product_information_list = await fetch_n_rows(collection=collection, n=number_of_rows)
    batch_size = 5 #TODO: Move to config
    results = []
    for i in range(0, len(product_information_list), batch_size):
        batch = product_information_list[i:i + batch_size]  # Get a batch of links
        log.info(f"Processing batch to get review page: {batch}")
        responses = await asyncio.gather(*(generate_summary_from_llm(prod_info_dict, generate_pdf=generate_pdf) for prod_info_dict in batch))
        results.extend(responses)
    response = {}
    for prod_dict, res in zip(product_information_list, results):
        response[prod_dict["title"]] = res
    if not generate_pdf:
        return response
    if generate_pdf:
        return ""

#TODO: ADD EXCEPTION HANDLING AND EDGE CASES
async def generate_summary_with_fq(fq: str, generate_pdf: bool = False):
    """This method is only responsible for generating summaries for the given n rows. 
    these n rows are from database which are indexed as per the indexing algorithm i.e. date created

    Args:
        number_of_rows (int, optional): number of rows for which summary is required to be created. Defaults to 1.
    """
    product_information_list = await fetch_n_rows(collection=collection, n=1, filter_query=fq)
    batch_size = 5 #TODO: Move to config
    results = []
    for i in range(0, len(product_information_list), batch_size):
        batch = product_information_list[i:i + batch_size]  # Get a batch of links
        log.info(f"Processing batch to get review page: {batch}")
        responses = await asyncio.gather(*(generate_summary_from_llm(prod_info_dict) for prod_info_dict in batch))
        results.extend(responses)
    if not generate_pdf:
        return results
    if generate_pdf:
        return ""
