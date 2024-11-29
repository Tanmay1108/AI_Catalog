import requests
import time
from fake_useragent import UserAgent
from common.decorators import async_retry

@async_retry(max_retries=5, delay=5.0, backoff=2.0)
async def write_html_website_content_to_file(url: str, file_name: str, headers: dict = None) -> bool:
    """
    This function is responsible for crawling a 
    website and writing down the website content HTML 
    format into a given file

    NOTE: This function is not responsible for deleting a file.
    Make sure to handle the deletion and creation of the file in the 
    caller function. 

    Args:
        url(str): the URL that is required to be crawled
        file_name (str): file name where the content will be written
        headers(dict): headers that are required for that particular website.
    """

    session = requests.Session()
    proxy_auth= "" # store this to an env variable.
    proxies = {
        "http": f"http://{proxy_auth}",
        "https": f"https://{proxy_auth}"
    }
    if not headers: 
        # default headers for g2 or any random wesbsite.
        headers = {
        'User-Agent': UserAgent().random,
        'Accept-Language': 'en-GB,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Connection': 'keep-alive',
        'Referer': 'https://www.google.com'
        }
    time.sleep(5) # added to make sure that the browser does not block the request
    resp = session.get(url, proxies=proxies, headers=headers)
    if resp.status_code != 200:
        raise Exception("Soemthing went wrong please retry")
    with open(file_name, 'w') as f:
        f.write(resp.text)
    return True
