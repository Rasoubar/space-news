import trafilatura

url = "https://www.theregister.com/2026/04/22/nasa_artemis_ii_heat_shield/"

# Download the webpage
downloaded_html = trafilatura.fetch_url(url)

# Extract only the main article text
article_text = trafilatura.extract(downloaded_html)

print(article_text)