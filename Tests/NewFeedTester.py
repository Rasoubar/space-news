import feedparser

def main():
    urls= ["https://www.nasa.gov/rss/dyn/breaking_news.rss","http://www.esa.int/rssfeed/Our_Activities/Space_Science","https://www.universetoday.com/feed","https://skyandtelescope.org/astronomy-news/feed/"]
    for url in urls:
        feed = feedparser.parse(url)
        c=0
        for entry in feed.entries:
            print(entry.published)
            print(entry.title)

