import json
import tempfile
from typing import List, Dict
from bs4 import BeautifulSoup
import logging as log
import asyncio
import uuid
from .crawling_service import write_html_website_content_to_file
from db import db
from dropbox_helper import upload_files_to_drop_box


def _modify_g2_review_url_to_pricing(original_url):
    """
    Convert a G2 product reviews URL to its corresponding pricing page URL.
    
    Args:
        original_url (str): The original G2 product reviews URL
    
    Returns:
        str: The modified URL pointing to the pricing page
    """
    #assuming this is a fail safe function as we are scrolling
    modified_url = original_url.replace("/reviews", "/pricing")
    return modified_url

async def crawl_data_from_pricing_page(prod_name: str, link: str):
    """this method is responsible for crawling the respective pricing page and getting the pricing information

    Args:
        link (str): review link to the page
    """
    pricing_url = _modify_g2_review_url_to_pricing(link)
    file_name = f"{prod_name}_pricing.html"
    await write_html_website_content_to_file(url=pricing_url, file_name=file_name)
    with open(file_name, 'r') as f:
        html_doc = f.read()
    soup = BeautifulSoup(html_doc, 'html.parser')
    pricing_cost = soup.find_all('td', class_="editions__pricing editions__pricing--vertical")
    pricing_description = soup.find_all('td', class_="editions__description editions__description--spaced")
    cost_information = []
    for cost, description in zip(pricing_cost, pricing_description):
        pricing_text = cost.find_all('span')
        pricing_cost_text = ' '.join(span.text.strip() for span in pricing_text)
        description_tags = description.find_all('span')
        description_text = ' '.join(li.text.strip() for li in description_tags)
        cost_information.append({"pricing_cost": pricing_cost_text, "pricing_description": description_text})
    return cost_information


async def crawl_data_from_review_page(link_dict: dict):
    data_dict = {}
    name = link_dict.get("name")
    link = link_dict.get("link")
    file_name = f"{name}.html"
    # file_name = "Vertex AI.html" #for testing purposes
    await write_html_website_content_to_file(url=link, file_name=file_name)
    with open(file_name, 'r') as f:
        html_doc = f.read()
    soup = BeautifulSoup(html_doc, 'html.parser')
    product_head_title = soup.find('div', class_='product-head__title')
    sub_divs = product_head_title.find_all('div')  # Find all child divs
    title = sub_divs[0].text.strip()
    data_dict["title"] = title
    created_by = sub_divs[1].text.strip()
    data_dict["parent_company"] = created_by
    about_company = soup.find('div', attrs={'data-max-height-expand-event-description': 'PDPs Overview Description'})
    about_company = about_company.text.strip()
    data_dict["about_company"] = about_company
    product_description_tags = soup.find_all('div', class_='hide-if-js')
    product_description_title = product_description_tags[1].text.strip()
    product_description_and_information = product_description_tags[1]
    product_information = ""
    seller_information = ""
    seller = False # will improve on the naming
    for child in product_description_and_information.children: 
        if not seller and child.name == 'hr': 
            seller = True
        if child.name:  
            if not seller:
                product_information += child.text.strip()
            else:
                seller_information += child.text.strip() # seller information can be formatted even more.
    data_dict["product_information"] = product_information
    data_dict["seller_information"] = seller_information

    #get pricing information
    pricing_data = await crawl_data_from_pricing_page(prod_name=name, link=link)
    # pricing_data = {}
    data_dict["pricing"] = pricing_data

    print(json.dumps(data_dict, indent = 4))
    collection = db["supaclear"]
    result = await collection.insert_one(data_dict) #uploading to mongo db
    await create_md_file_and_upload_to_dropbox(data_dict)
    print(result) # to be removed in production code, for testing purposes. 

async def create_md_file_and_upload_to_dropbox(data_dict: dict):
    """This function is responsible for creating an md file and storing it in dropbox.
    
    NOTE: I wanted to use s3 but it required payment via my credit card, but I do not have one :P, 
    so had to use dropbox. 

    Args:
        data_dict (dict): data dict containing the information that will be used to generate an md file.

    Returns: void
    """
    markdown_content = f"""
## Company Name
# {data_dict.get('title')}

## Parent Company
# {data_dict.get('parent_company')}

## Company Information
{data_dict.get('about_company')}

## Product Information
{data_dict.get('product_information')}

## Seller Information
{data_dict.get('seller_information')}

## Pricing Information
{data_dict.get('pricing')}
"""
    file_name = f"{data_dict.get('title')}.md"
    with open(file_name, 'w') as f:
        f.write(markdown_content) #only for testing purposes
    await upload_files_to_drop_box(file_name=file_name)

#TODO: Handle the case where in number of rows exceeds the total number of rows present.
async def crawl_with_rows(number_of_rows: int) -> bool:
    """This function crawls data form the g2 website.

    NOTE: I wanted this function to be a cron job that runs every week or so. 
    Due to shortage of time, created this as an API for demonstartion purposes.

    NOTE: The indexing is async, therefore our overall system becomes consistent with some delay.
    Rollbacks are not being handled in the current case scenario as it would need a bit more time to implement.

    Args:
        number_of_rows (int): Number of rows of data that a user wants to be indexed
        in the database.

    Returns:
        bool: True if the query is queued to be indexed in the database. 
    """
    URL = "https://www.g2.com/categories/data-science-and-machine-learning-platforms"
    URL = "https://www.g2.com/categories/data-science-and-machine-learning-platforms?order=g2_score&page=14#product-list" # for testing purposes. 
    #NOTE: I am using paid version of proxy rotator, since my version does not have a huge limit, im starting from page 16 so that it can be tested for demo purposes
    links = []    
    counter = 0
    while(True):
        temp_file = tempfile.NamedTemporaryFile()
        file_name = f"{temp_file.name}.html"
        await write_html_website_content_to_file(url=URL, file_name=file_name)
        with open(file_name, 'r') as f:
            html_doc = f.read()
        temp_file.close()
        # with open("main_page.html", 'r') as f:
        #     html_doc = f.read()
        soup = BeautifulSoup(html_doc, 'html.parser')
        page_links = soup.find_all('a', class_='d-ib c-midnight-100 js-log-click')
        links.extend(page_links)
        next_tag = soup.find('a', attrs={'data-event-options': '{"value":"next","name":"Event::PaginationClicked"}'})
        if not next_tag:
            break
        URL = next_tag['href']
        break #for testing purposes
        # counter = counter + 1
        # if counter > 2: break # for testing purposes
    links_list: List[Dict] = []
    counter = 0
    for link in links:
        if link and 'href' in link.attrs:
            counter = counter + 1
            href = link['href']
            name = link.text.strip()
            links_list.append({"name": name, "link": href})
            if(counter == number_of_rows): break
    import pdb;pdb.set_trace()
    batch_size = 5 #TODO: Move to config
    results = []
    for i in range(0, len(links_list), batch_size):
        batch = links_list[i:i + batch_size]  # Get a batch of links
        log.info(f"Processing batch to get review page: {batch}")
        responses = await asyncio.gather(*(crawl_data_from_review_page(link_dict) for link_dict in batch))
        results.extend(responses)
    return True

async def crawl_with_product_name(product_name: str) -> bool:
    return True