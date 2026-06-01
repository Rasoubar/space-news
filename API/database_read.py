from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import libsql

load_dotenv()
TURSO_URL = os.getenv("TURSO_DB")
TURSO_TOKEN = os.getenv("TURSO_READ_TOKEN")

def get_connection():
    conn = libsql.connect(
        database = TURSO_URL,
        auth_token = TURSO_TOKEN)
    return conn

def get_random_recent_article():
    cutoff_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    conn = get_connection()

    query = """
        SELECT id, title, url, summary, source
        FROM articles 
        WHERE date >= ? 
        ORDER BY RANDOM() 
        LIMIT 1;
    """

    # 3. Execute and return
    result = conn.execute(query, (cutoff_date,))
    article = result.fetchone()
    if article is None:
        return {"error": "No articles from the last 24 hours in database."}
    return {
    "id": article[0],
    "title": article[1],
    "url": article[2],
    "summary": article[3],
    "source": article[4]
    }

def get_related_articles(article_id):
    conn = get_connection()
    query = """
            SELECT 
                CASE 
                    WHEN source_id = ?1 THEN target_id 
                    ELSE source_id 
                END AS related_id
            FROM related_articles 
            WHERE source_id = ?1 OR target_id = ?1
            ORDER BY score DESC
            LIMIT 6;
        """
    result = conn.execute(query, (article_id,))
    articles_raw = result.fetchall()
    articles = get_multiple_articles([a[0] for a in articles_raw])
    if articles is None:
        return {"error": "No related articles found."}
    return articles

def get_article(article_id):
    conn = get_connection()
    query = """
    SELECT id, title, url, summary, source
    FROM articles 
    WHERE id = ?
    LIMIT 1;
    """
    result = conn.execute(query, (article_id,))
    article = result.fetchone()
    if article is None:
        return {"error": "Article not found."}
    return {
        "id": article[0],
        "title": article[1],
        "url": article[2],
        "summary": article[3],
        "source": article[4]
    }

def get_multiple_articles(article_ids):
    conn = get_connection()
    placeholders = ",".join(["?"] * len(article_ids))
    query = f"SELECT id, title, url, summary, source FROM articles WHERE id IN ({placeholders})"
    result = conn.execute(query, article_ids)
    articles_raw = result.fetchall()
    return [{"id": a[0], "title": a[1], "url": a[2], "summary": a[3], "source": a[4]} for a in articles_raw]


#print(get_random_recent_article())
#print(get_related_articles(333))
