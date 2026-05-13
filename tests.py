import engine as e
import scraper as s
import config

def test_date():
    for source,url in config.feeds.items():
        print(url)
        for entry in s.feed_extraction(url):
            print(e.read_rss_entry(entry,source)["date_string"])


