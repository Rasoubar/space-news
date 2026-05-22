from database_core import get_connection
from datetime import datetime, timedelta


def get_random_recent_article():
    cutoff_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    conn = get_connection()

    query = """
        SELECT id, title, url 
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
    "url": article[2]
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
            LIMIT 3;
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
    SELECT id, title, url 
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
        "url": article[2]
    }

def get_multiple_articles(article_ids):
    conn = get_connection()
    placeholders = ",".join(["?"] * len(article_ids))
    query = f"SELECT id, title, url FROM articles WHERE id IN ({placeholders})"
    result = conn.execute(query, article_ids)
    articles_raw = result.fetchall()
    return [{"id": a[0], "title": a[1], "url": a[2]} for a in articles_raw]


#print(get_random_recent_article())
#print(get_related_articles(333))
