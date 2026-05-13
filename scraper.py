import trafilatura
import feedparser
import cloudscraper

def extract_text(url): #extracts raw text for comparison
    webpage = trafilatura.fetch_url(url) #downloads page in html format
    text = trafilatura.extract(webpage) #extracts the article, hopefully
    if text is None:
        scraper = cloudscraper.create_scraper()
        html = scraper.get(url).text
        text = trafilatura.extract(html)
    return text

def feed_extraction(url): #extracts news rss entries
    feed = feedparser.parse(url)
    return feed.entries



