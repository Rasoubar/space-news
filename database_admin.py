import sqlite3
import utils as u
from database_core import get_connection


def setup_db():
    conn = get_connection()
    cursor = conn.cursor()
    #blob because speed and space
    cursor.execute('''  
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            summary TEXT,
            url TEXT UNIQUE,
            title TEXT,
            date DATETIME DEFAULT CURRENT_TIMESTAMP,
            raw_text TEXT,
            embedding BLOB 
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS related_articles (
            source_id INTEGER,
            target_id INTEGER,
            score REAL,
            UNIQUE(source_id, target_id)
        );
    ''')

    conn.commit()
    conn.close()

def save_articles(articles):
    conn = get_connection()
    cursor = conn.cursor()
    article_id = None
    for i in range(len(articles)):
        article_id = save_article_entry(articles[i],conn,cursor)
        set_related_vectors(article_id, articles[i]['related_vectors'], articles[i]['similarities'],conn,cursor)
    conn.close()
    return article_id

def save_article_entry(article,conn,cursor):
    embedding_blob = u.blob_vector(article["vector"])
    try:  # play it safe
        cursor.execute('''
                    INSERT INTO articles (source, url, title, summary, raw_text, embedding, date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (article["source"], article["link"], article["title"], article["summary"], article["text"],
                      embedding_blob, article["date_string"]))
        conn.commit()
    except sqlite3.IntegrityError:
        u.log_error("SQL fail on link" + article.link)
        pass
    return cursor.lastrowid

def new_entries(urls):
    conn = get_connection()
    cursor = conn.cursor()
    placeholders = ",".join(["?"] * len(urls))
    query = f"SELECT url FROM articles WHERE url IN ({placeholders})"
    cursor.execute(query, urls)
    existing_urls = {row[0] for row in cursor.fetchall()}
    conn.close()
    new_urls = [url for url in urls if url not in existing_urls]
    return new_urls

def is_entry_new(url):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT 1 from articles WHERE url = ?', (url,))
    result = cursor.fetchone()
    conn.close()
    if result is None:
        return True
    else:
        return False

def extract_vectors(limit=10000): #returns 2 lists, one with id, one with vector. Same index to match
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''SELECT id, embedding FROM articles ORDER BY date DESC LIMIT ? ''', (limit,))
    pairs = cursor.fetchall()
    article_ids=[]
    vectors=[]
    for i in pairs:
        article_ids.append(i[0])
        vectors.append(i[1])
    conn.close()
    unblobbed_vectors = [u.unblob_vector(blob) for blob in vectors]
    return article_ids,unblobbed_vectors

def new_related_articles(vectors):
    conn = get_connection()
    cursor = conn.cursor()
    for vector in vectors:
        set_related_vectors(vector["id"], vector["targets"], vector["similarities"],conn,cursor)
    conn.close()

def set_related_vectors(article,targets,similarities,conn,cursor):
    for i in range(len(targets)):
        cursor.execute('''
                        INSERT INTO related_articles (source_id, target_id, score)
                        VALUES (?, ?, ?)
                    ''', (article, targets[i], similarities[i]))
    conn.commit()

def clean_related(): #used in early stage
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''DELETE FROM related_articles WHERE source_id <= target_id''')
    conn.commit()
    conn.close()

def clean_all_titles(): #some formating was wrong, needed to clean all of them
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, title FROM articles")
    rows = cursor.fetchall()
    updated_count = 0

    for row in rows:
        article_id, old_title = row
        new_title = u.clean_html(old_title)

        if new_title != old_title:
            cursor.execute(
                "UPDATE articles SET title = ? WHERE id = ?",
                (new_title, article_id)
            )
            updated_count += 1

    conn.commit()
    conn.close()
    print(f"Cleaned {updated_count} titles.")

