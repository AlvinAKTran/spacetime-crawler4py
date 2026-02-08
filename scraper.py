import re
import time
from urllib.parse import urlparse, urlunparse, urljoin
from utils.response import Response
from bs4 import BeautifulSoup as bs

LONGEST_PAGE_COUNT = 0
LONGEST_PAGE_LINK = ""
SIMHASH_COUNTS = {}
SIMHASH_LIMIT = 3
WORD_FREQUENCY = {}


def tokenize(text):
    text = text.lower()
    text = re.findall(r"[a-z0-9]{3,}", text) # Only keep words with 3 or more characters to reduce noise
    return text


def term_frequency(tokens):
    tf = {}
    for token in tokens:
        if token not in tf:
            tf[token] = 0
        tf[token] += 1
    return tf


def sim_hash(text):
    vector = [0] * 64 #Create 64 bit vector for simhash
    tokens = tokenize(text) #tokenize the text
    tf = term_frequency(tokens) #get frequency

    for token, freq in tf.items(): #hash each token and update vector by freq
        token_hash = hash(token)
        for i in range(64):
            if token_hash & (1 << i): #GPT helped with bitwise opeartions
                vector[i] += freq
            else:
                vector[i] -= freq

    #Encodes content into 64 bit simhash
    simhash = 0 
    for i in range(64): 
        if vector[i] > 0: 
            simhash |= (1 << i) #GPT helped with bitwise operations

    return simhash


def is_low_information_page(text, html):
    tokenized_text = tokenize(text)
    page_hash = sim_hash(text)

    if len(tokenized_text) < 100:
        return True
    
    if len(html) > 0 and len(text) / len(html) < 0.05:
        return True

    if page_hash in SIMHASH_COUNTS:
        SIMHASH_COUNTS[page_hash] += 1
    else:
        SIMHASH_COUNTS[page_hash] = 1

    if SIMHASH_COUNTS[page_hash] > SIMHASH_LIMIT:
        return True


def scraper(url: str, resp: Response) -> list[str]:
    links = extract_next_links(url, resp)
    print(LONGEST_PAGE_COUNT)
    print(LONGEST_PAGE_LINK)
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
        text = soup.get_text(separator=" ")
        html = str(soup)
        links = list()

        with open('crawled_text.txt', 'a', encoding='utf-8') as file:
            file.write(text + '\n')

        if is_low_information_page(text, html): #condition for filtering out low information pages, which are likely to be crawler traps or non-content pages
            return list()

        global LONGEST_PAGE_COUNT, LONGEST_PAGE_LINK
        if len(text) > LONGEST_PAGE_COUNT:
            LONGEST_PAGE_COUNT = len(text)
            LONGEST_PAGE_LINK = url

            print(f"New longest page found: {LONGEST_PAGE_COUNT} characters at {LONGEST_PAGE_LINK}")

        for a in soup.find_all('a', href = True):
            parsed = urlparse(a['href'])

            url_as_list = list(parsed)
            url_as_list[5] = "" #set fragment to ""

            if url_as_list[1] != "": #netloc is not empty
                links.append(urlunparse(url_as_list))
            elif len(a['href']) == 0 or (a['href'][0] != "/" and a['href'][0] != ".") or ":" in a['href'] or "=" in a['href']: #some other non useful link/javascript/query
                pass
            else: #this link is a working path
                links.append(urljoin(url, urlunparse(url_as_list)))

        return links

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
        
        if "uci.zoom.us" in parsed.netloc.lower():
            # Filter out any Zoom links that might bypass our next filter.
            return False
        
        if not (parsed.netloc.lower().endswith("ics.uci.edu")
            or parsed.netloc.lower().endswith("cs.uci.edu")
            or parsed.netloc.lower().endswith("informatics.uci.edu")
            or parsed.netloc.lower().endswith("stat.uci.edu")):
            # Filter everything outside *.ics.uci.edu/*, *.cs.uci.edu/*, *.informatics.uci.edu/*, *.stat.uci.edu/*
            return False

        if (parsed.netloc.lower().startswith("gitlab.ics.uci.edu")):
            #Filter for gitlab pages, which is almost entirely made up of student repositories we don't want to access
            return False
        
        if ":" in parsed.path:
            #avoid branching jsonesque pages
            return False
        
        if re.search("doku.php", parsed.path):
            #site with a long directory of mostly not great information
            return False
        
        if "grape.ics.uci.edu" in parsed.netloc.lower():
            # Low information value and mostly password protected
            return False
        
        if "grape.ics.uci.edu" in parsed.netloc.lower():
            # Low information value and mostly password protected
            return False
        
        if parsed.fragment:
            # Filter any URLs with fragments to avoid crawling pages with the same HTML content 
            return False
        
        if re.search("commit\/", parsed.path):
            # Avoid crawling commit pages with low value and possible infinite crawl traps
            return False
        
        if re.search(r'page/\d{2,}', parsed.path):
            # Disable crawling of more than 10 pages of paginated content
            return False
        
        if re.search(
            r'\b(share|redirect|redirect_to|limit|sid'
            + r'|execution|ical|outlook|utm|utm_source|filter|action)\b', parsed.query.lower()):
            # Filter many common URL queries that likely to lead to crawler traps or non-content pages
            return False
        
        
        # if re.search(r'\d{4}-\d{2}'+ r'|\d{2}-\d{4}', parsed.path + parsed.query) or re.search(r'\/events\/', parsed.path):
        #     # Filters URLs with date patterns or mentions of events to avoid crawling infinite calendar crawler traps
        #     # More prone to false postives, but worth it to avoid as many traps as possible
        #     return False

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1|ppsx"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

