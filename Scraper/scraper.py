import time
import trafilatura
import feedparser
import cloudscraper

# Text that shows up when a site serves a bot-check / block page instead of the article
BLOCK_PAGE_MARKERS = [
    "enable javascript and cookies to continue",
    "please enable javascript",
    "javascript is disabled",
    "checking your browser",
    "just a moment...",
    "attention required",
    "verify you are human",
    "access denied",
]

def is_block_page(text):
    if not text:
        return True
    lowered = text.lower()
    # real articles are long; block pages are a line or two
    return len(text) < 500 and any(marker in lowered for marker in BLOCK_PAGE_MARKERS)

def extract_text(url, retry_wait=20): #extracts raw text for comparison
    text = _try_extract(url)
    if text is None and retry_wait: #blocks are usually temporary, wait a bit and try once more
        time.sleep(retry_wait)
        text = _try_extract(url)
    return text

def _try_extract(url):
    webpage = trafilatura.fetch_url(url) #downloads page in html format
    text = trafilatura.extract(webpage) #extracts the article, hopefully
    if is_block_page(text):
        text = None
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url)
        if response.status_code == 200: #403/503 = blocked, don't extract the error page
            text = trafilatura.extract(response.text)
            if is_block_page(text):
                text = None
    return text #None = still blocked

def feed_extraction(url): #extracts news rss entries
    feed = feedparser.parse(url)
    return feed.entries
