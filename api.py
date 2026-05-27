import database_read as db_r
from fastapi import FastAPI, HTTPException

from fastapi.middleware.cors import CORSMiddleware #for testing

app = FastAPI()
app.add_middleware( #for testing
    CORSMiddleware,
    allow_origins=["*"],      # Allows any local file to send requests
    allow_credentials=True,
    allow_methods=["*"],      # Allows all standard methods (GET, POST, etc.)
    allow_headers=["*"],      # Allows all headers
)

@app.get("/articles/random")
def random_article():
    try:
        data = db_r.get_random_recent_article()
        if isinstance(data, dict) and "error" in data:
            raise HTTPException(status_code=404, detail=data["error"])
        return {"status": "success", "data": data}
    except HTTPException as http_e:
        raise http_e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/articles/{article_id}")
def article(article_id: int):
    try:
        data = db_r.get_article(article_id)
        if isinstance(data, dict) and "error" in data:
            raise HTTPException(status_code=404, detail=data["error"])
        return {"status": "success", "data": data}
    except HTTPException as http_e:
        raise http_e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/articles/{article_id}/related")
def related_articles(article_id: int):
    try:
        articles = db_r.get_related_articles(article_id)
        print(articles)
        if isinstance(articles, dict) and "error" in articles:
            return {"status": "no_matches", "message": articles["error"], "data": []}
        if not articles:
            return {"status": "no_matches", "message": "No articles found to be sufficiently related.", "data": []}
        return {"status": "success", "data": articles}
    except HTTPException as http_e:
        raise http_e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

#fastapi dev api.py --host 0.0.0.0

