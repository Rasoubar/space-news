from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import trafilatura


def test_article_matching():
    # 1. Load the model (PyTorch will automatically try to use your GPU)
    print("Loading the BAAI/bge-m3 model (this might take a minute the first time to download)...")
    model = SentenceTransformer("BAAI/bge-m3")

    # 2. Simulate our "database" of previously downloaded space news

    u1 = "https://www.theregister.com/2026/04/22/nasa_artemis_ii_heat_shield/"
    u2 = "https://www.space.com/space-exploration/artemis/artemis-2s-heat-shield-seems-to-have-aced-its-trial-by-fire"
    dt1 = trafilatura.fetch_url(u1)
    t1 = trafilatura.extract(dt1)
    dt2 = trafilatura.fetch_url(u2)
    t2 = trafilatura.extract(dt2)
    database_articles = [t1,t2]

    # 3. Simulate a brand new article we just pulled from an RSS feed
    new_article = t2

    # 4. Generate the embeddings (converting text to 1024-dimension arrays)
    print("Generating vector embeddings...\n")
    db_embeddings = model.encode(database_articles)
    new_embedding = model.encode([new_article])

    # 5. Calculate the mathematical distance (Cosine Similarity)
    # This compares our 1 new article against all 5 database articles instantly
    similarities = cosine_similarity(new_embedding, db_embeddings)[0]

    # 6. Print the results
    print("==================================================")
    print(f"NEW ARTICLE: '{new_article}'")
    print("==================================================\n")

    print("SIMILARITY SCORES (Higher % means more similar):")
    for i in range(len(database_articles)):
        score = similarities[i] * 100
        print(f"[{score:>5.1f}%] - {database_articles[i]}")

