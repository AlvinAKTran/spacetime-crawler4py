import re
import time
from urllib.parse import urlparse
from utils.response import Response
from bs4 import BeautifulSoup as bs

def scraper(url: str, resp: Response) -> list[str]:
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url: str, resp: Response) -> list[str]:
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    time.sleep(0.5)
    if resp.status == 200:
        soup = bs(resp.raw_response.content, features='lxml')
        return [a['href'] for a in soup.find_all('a', href = True)]

    return list()

def is_valid(url: str) -> bool:
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        if len(url) > 200:
            # Filter out URLs that are too long, which are likely to be crawler traps
            return False
        
        parsed = urlparse(url)
        
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        if "uci.zoom.us" in parsed.netloc:
            # Filter out any Zoom links that might bypass our next filter.
            return False
        
        if "uci.edu" not in parsed.netloc: # Probably isn't as clean as using Regex, but works
            return False
        
        if parsed.fragment:
            # Filter any URLs with fragments to avoid crawling pages with the same HTML content 
            return False
        
        if re.search(r'page/\d{2,}', parsed.path):
            # Disable crawling of more than 10 pages of paginated content
            return False
        
        if re.search(
            r'\b(share|redirect|redirect_to|limit|sid'
            + r'|execution|ical|outlook|utm|utm_source|filter|action)\b', parsed.query.lower()):
            # Filter many common URL queries that likely to lead to crawler traps or non-content pages
            return False
        
        
        if re.search(r'\d{4}-\d{2}'+ r'|\d{2}-\d{4}', parsed.path + parsed.query):
            # Filters URLs with date patterns to avoid crawling infinite calendar crawler traps
            # More prone to false postives, but worth it to avoid as many traps as possible
            return False

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
