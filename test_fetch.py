from qfzz.library.fetcher import ContentFetcher
import logging

logging.basicConfig(level=logging.INFO)

fetcher = ContentFetcher()
url = "https://files.freemusicarchive.org/storage-freemusicarchive-org/music/ccCommunity/Kai_Engel/Satin/Kai_Engel_-_04_-_Sentinel.mp3"
print(f"Testing URL: {url}")
res = fetcher.fetch_from_url(url)
print(f"Result: {res}")
