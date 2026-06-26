import time
from bs4 import BeautifulSoup
import re
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

#from scraper import feed_extraction


def log_error(string):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    with open("error_log.txt", "a", encoding="utf-8") as f:
        f.write(string + " | " + timestamp)

def clean_html(raw_html):
    raw_html = str(raw_html).replace("&nbsp;", " ").replace("\xa0", " ")
    clean_text = BeautifulSoup(raw_html, "html.parser").get_text(separator = " ", strip=True)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    return clean_text

def blob_vector(vector):
    blobbed_vector = vector.tobytes()
    return blobbed_vector

def unblob_vector(vector):
    unblobed_vector = np.frombuffer(vector, dtype=np.float32)
    return unblobed_vector

def vectorize_texts(texts): #uses a list
    model = SentenceTransformer('BAAI/bge-m3', local_files_only=True)
    output = model.encode(texts,batch_size=8, show_progress_bar=True)
    return output
    #os._exit(0) seems to be needed to end the process atm after using this, local files seems to have fixed it


def calc_similarity(vector1, vectors): #does what it says, returns a list
    similarity = cosine_similarity([vector1], vectors)[0]
    return similarity

#purpose is filtering while not losing matching indexation. rn is ordered, that could be improved
def closest_vectors(o_results, t=0.70): #returns 2 lists, 1 with id, 1 with score. same index for matching. receives list of vectors.
    results = np.array(o_results).flatten()
    valid_indices = np.where(results > t)[0]
    valid_scores = results[valid_indices]
    sort_order = np.argsort(-valid_scores)
    best_ids = valid_indices[sort_order].tolist()
    best_scores = valid_scores[sort_order].tolist()
    return best_ids, best_scores

def exclude_entertainment(entry): #excludes "entertainment" categories (rn for space.com only)
    tags = entry.get('tags')
    if tags and isinstance(tags, list):
        for tag in tags:
            term = tag.get('term', '')
            if term and term.lower().strip() == 'entertainment':
                return True
    return False

def exclude_author(entry):
    deal_authors = {"paul brett", "harry bennet", "harry bennett", "chris mcmullen", "tantse walter", "jase parnell-brookes"}
    return entry.author.strip().lower() in deal_authors

def exclude_by_link(entry):
    link = entry.get('link')
    exclusions = ["https://www.space.com/space-exploration/launches-spacecraft"]
    link_cleaned = link.strip().lower()
    return any(forbidden.lower() in link_cleaned for forbidden in exclusions)