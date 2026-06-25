import config as c
import scraper as s
import utils as u
import time
import database_admin as db

def new_article_list():
    new_articles = []
    for source,url in c.feeds.items():
        print("Parsing RSS feed for " + source)
        for entry in s.feed_extraction(url):
            if source == "Space.com" and (u.exclude_entertainment(entry) or u.exclude_author(entry) or u.exclude_by_link(entry)):
                continue
            try:
                article_data = read_rss_entry(entry, source)
                if article_data.get('link'):
                    new_articles.append(article_data)
                else:
                    u.log_error(f'RSS Feed error, no link. Entry {entry}')
            except Exception as e:
                u.log_error(f'Error: {e}, on entry {entry}')
        print(source + " parsed")
    return new_articles

def read_rss_entry(entry,source): #extracts what we need from the rss entry
    utc_date = time.strftime('%Y-%m-%d %H:%M:%S', entry.published_parsed)
    return {
        "title": u.clean_html(entry.title),
        "source": source,
        "link": entry.link,
        "summary": u.clean_html(entry.summary),
        "text": s.extract_text(entry.link),
        "date_string": utc_date,
        "date_parsed": entry.published_parsed #for sorting later
    }

def entries_to_add():
    candidates = new_article_list()
    urls = [entry["link"] for entry in candidates]
    new_entries = set(db.new_entries(urls))
    to_add = [entry for entry in candidates if entry["link"] in new_entries]
    return to_add

def add_entries():
        entries_raw = entries_to_add()
        entries = [entry for entry in entries_raw if entry['text'] is not None]
        print(f'{len(entries)} entries selected')
        if len(entries)>0:
            entries = sorted(entries, key=lambda x: x["date_parsed"])
            texts = [entry["text"] for entry in entries]
            vectors = u.vectorize_texts(texts)
            relations = multiple_related_articles(vectors)
            for i in range(len(vectors)):
                entries[i]['vector'] = vectors[i]
                entries[i]['related_vectors'], entries[i]['similarities'] = relations[i][0], relations[i][1]
            last_id = db.save_articles(entries)
            new_article_relations_add(vectors, last_id)


def multiple_related_articles(vector_list):
    ids, vectors = db.extract_vectors()
    relations = []
    for vector in vector_list:
        related_ids, scores = related_articles(vector, ids, vectors)
        relations.append((related_ids,scores))
    return relations


def related_articles(vector,ids,vectors): # takes 1 vector, compares to all DB vectors, returns 1 list with article id, 1 with score. index to match
    sims = u.calc_similarity(vector, vectors)
    t_id_index, t_score = u.closest_vectors(sims)
    id_return = []
    for i in t_id_index: #converts u.closest_vectors ids to article ids. is needed! Might only work if comparing to full db, unsure atm. Tbh I could just reverse the list, I expect it to be better
        id_return.append(ids[i])
    return id_return, t_score

def new_article_relations_add(vectors, last_id):
    ids = list(range(last_id-len(vectors)+1, last_id+1))
    new_relations= []
    for i in range(len(vectors)):
        sims = u.calc_similarity(vectors[i], vectors)
        t_id_index, t_score = u.closest_vectors(sims)
        targets=[]
        similarities=[]
        for n in range(len(t_id_index)):
            if t_id_index[n] < i:
                targets.append(ids[t_id_index[n]])
                similarities.append(t_score[n])
        if len(targets)>0:
            new_relation={"id": ids[i],"targets": targets,"similarities": similarities}
            new_relations.append(new_relation)
    db.new_related_articles(new_relations)


def test_vectors():
    ids, lista = db.extract_vectors()
    for i in range(len(lista)):
        print(ids[i])
        print(multiple_related_articles(lista[i]))

#def update_all_vectors(): #used in early stage, move eventually
#    ids, lista = db.extract_vectors()
#    for i in range(len(lista)):
#        targets, similarities = (related_articles(lista[i]))
#        db.set_related_vectors(ids[i], targets, similarities)


add_entries()
#test_vectors()
#update_all_vectors()
