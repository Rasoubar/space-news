import config as c
import scraper as s
import utils as u
import time
import database as db

def new_article_list():
    new_articles = []
    for source,url in c.feeds.items():
        print("Parsing RSS feed for " + source)
        for entry in s.feed_extraction(url):
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
        "title": entry.title,
        "source": source,
        "link": entry.link,
        "summary": u.clean_html(entry.summary),
        "text": s.extract_text(entry.link),
        "date_string": utc_date,
        "date_parsed": entry.published_parsed #for sorting later
    }

def entries_to_add():
    to_add=[]
    for entry in new_article_list():
        if db.is_entry_new(entry["link"]):
            to_add.append(entry)
    return to_add

def add_entries():
        entries = entries_to_add()
        print(f'{len(entries)} entries selected')
        if len(entries)>0:
            entries = sorted(entries, key=lambda x: x["date_parsed"])
            texts=[]
            for entry in entries:
                texts.append(entry["text"])
            vectors = u.vectorize_texts(texts)
            new_vectors = []
            for i in range(len(vectors)):
                entries[i]['vector'] = vectors[i]
                entries[i]['related_vectors'], entries[i]['similarities'] = related_articles(vectors[i])
                new_vectors.append(i)
            last_id = db.save_articles(entries)
            new_article_relations_add(vectors, last_id)



def related_articles(vector): # takes 1 vector, compares to all DB vectors, returns 1 list with article id, 1 with score. index to match
    ids, vectors = db.extract_vectors()
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
        print(related_articles(lista[i]))

#def update_all_vectors(): #used in early stage, move eventually
#    ids, lista = db.extract_vectors()
#    for i in range(len(lista)):
#        targets, similarities = (related_articles(lista[i]))
#        db.set_related_vectors(ids[i], targets, similarities)



add_entries()
#test_vectors()
#update_all_vectors()
