import pandas as pd
import numpy as np
from db.data_base import get_recent_interactions,get_recent_searches,get_top_interaction
import os
from huggingface_hub import InferenceClient

# ---------------- LOAD DATA ----------------
final_df = pd.read_csv("data/event_data.csv",keep_default_na=False)


embeddings = np.load("data/event_embeddings2.npy").astype(np.float32)
#embeddings= np.load("data/event_embeddings.npy") 

assert len(final_df) == embeddings.shape[0], "Mismatch between CSV and embeddings"

#model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

# ------------------ HF CLIENT ------------------
client = InferenceClient(
    model="sentence-transformers/all-mpnet-base-v2",
    token=os.getenv("HF_TOKEN")
)


# helper functions-----------------------------------------------------------------------------------------------

# ------------------ COSINE SIMILARITY ------------------
def cosine_similarity(a, b):
    a_norm = np.linalg.norm(a, axis=1, keepdims=True)
    b_norm = np.linalg.norm(b, axis=1)
    return np.dot(a, b.T) / (a_norm * b_norm + 1e-10)

def remove_duplicate_interactions(interactions):
    seen = set()
    unique_interactions = []
    for interaction in interactions:
        if interaction['event_id'] not in seen:
            unique_interactions.append(interaction)
            seen.add(interaction['event_id'])
    return unique_interactions

def remove_duplicate_searches(searches):
    seen = set()
    unique_searches = []
    for search in searches:
        if search['query'] not in seen:
            unique_searches.append(search)
            seen.add(search['query'])
    return unique_searches

hash={}
def get_embedding(text):
    if text in hash:
        return hash[text]

    emb = client.feature_extraction(text)

    # Handle nested output
    emb = emb[0] if isinstance(emb[0], list) else emb

    hash[text] = emb
    return emb

def interaction_vector(uid):
    interactions = get_recent_interactions(uid)
    interactions = remove_duplicate_interactions(interactions)
    vec = np.zeros(embeddings.shape[1])  # same dimension as embedding
    divi=0
    for i,interaction in enumerate(interactions):
        idx = final_df.index[final_df['id'] == int(interaction['event_id'])]
        if len(idx) == 0:
            continue
        event_index = idx[0]
        val=embeddings[event_index]
        if(interaction['action']=='click'):
            weight=0.7
        else:
            weight=0.3
        recency_weight = 1 / (i + 1)
        vec+=val*weight*(recency_weight)
        divi+=(weight*recency_weight)
    if divi==0: return vec
    return vec/divi

def search_vector(uid):
    searches = get_recent_searches(uid)
    searches = remove_duplicate_searches(searches)
    vec = np.zeros(embeddings.shape[1])  # same dimension as embedding
    divi = 0
    for i, search in enumerate(searches):
        query_emb = np.array(get_embedding(search['query'])).reshape(1, -1)
        query_emb = query_emb.squeeze()
        recency_weight = 1 / (i + 1)
        vec += query_emb * recency_weight
        divi += recency_weight
    if divi==0: return vec
    return vec / divi

#recommendation functions--------------------------------------------------------------------------------------

def recommend_by_query(query, top_k=100):
    query_emb = np.array(get_embedding(query)).reshape(1, -1)
    sims = cosine_similarity(query_emb, embeddings)[0]

    top_idx = np.argsort(sims)[::-1][:top_k]
    results = final_df.iloc[top_idx][['id','title','mode','price_type','clean_desc','city']].copy()

    return results.to_dict(orient="records")

#print(recommend_by_query("ai workshop", top_k=5))

def recommend_similar_event(event_index, top_k=10):
    idx = final_df.index[final_df['id'] == int(event_index)]
    if len(idx) == 0:
        return []
    event_index = idx[0]
    event_emb = embeddings[event_index].reshape(1, -1)
    sims = cosine_similarity(event_emb, embeddings)[0]

    top_idx = sims.argsort()[::-1][1:top_k+1]
    results= final_df.iloc[top_idx][['id','title','mode','price_type','clean_desc','city']]
    results['score']=((sims[top_idx]+1)/2).round(2)
    results['source']='similar_events'
    return results.to_dict(orient="records")

def recommend_based_on_user_interaction(uid,top_k=10):
    seen_event_ids = {int(i['event_id']) for i in get_recent_interactions(uid)}

    inter_vec = interaction_vector(uid)
    search_vec = search_vector(uid)

    if np.linalg.norm(inter_vec) == 0:
        return []
    if np.linalg.norm(search_vec) == 0:
        search_cosine = 0
    else:
        search_cosine = cosine_similarity(search_vec.reshape(1, -1), embeddings)[0]

    score = (
        0.7 * cosine_similarity(inter_vec.reshape(1, -1), embeddings)[0]
        + 0.3 * search_cosine
    )

    seen_mask = final_df['id'].isin(seen_event_ids).values
    score[seen_mask] = -1

    top_idx = np.argpartition(score, -top_k)[-top_k:]
    top_idx = top_idx[np.argsort(score[top_idx])[::-1]]

    results = final_df.iloc[top_idx][['id','title','mode','price_type','clean_desc','city']]
    results['score']=((score[top_idx]+1)/2).round(2)
    results['source']='interaction'
    return results.to_dict(orient="records") 


def recommend_based_on_prevSearches(uid,top_k=10):
    search_vec=search_vector(uid)
    if np.linalg.norm(search_vec) == 0:
        return []
    
    score=cosine_similarity(search_vec.reshape(1,-1),embeddings)[0]

    top_idx = np.argpartition(score, -top_k)[-top_k:]
    top_idx = top_idx[np.argsort(score[top_idx])[::-1]]


    interactions = get_recent_interactions(uid)
    seen_event_ids = set(int(i['event_id']) for i in interactions if i['action']=='click')

    seen_mask = final_df['id'].isin(seen_event_ids).values
    score[seen_mask] = -1

    top_idx = score.argsort()[::-1][:10]
    results= final_df.iloc[top_idx][['id','title','mode','price_type','clean_desc','city']]
    results['score']=((score[top_idx]+1)/2).round(2)
    results['source']='search'
    return results.to_dict(orient="records")

def popular_event_list(top=10):
    top_events = get_top_interaction(top)
    #print(top_events)
    ids = [int(e["_id"]) for e in top_events]

    df = final_df.set_index("id").loc[ids].reset_index()

    results = []
    for rank, row in enumerate(df.to_dict(orient="records")):
        results.append({
            **row,
            "score": round(1 / (rank + 1), 3),   # rank-based score
            "source": "popular"
        })

    return results


#print(popular_event_list(5))


#print(recommend_based_on_user_interaction("naran2"))

def build_user_profile(event_indices):
    return embeddings[event_indices].mean(axis=0).reshape(1, -1)


def recommend_personalized(user_interest):
    user_profile = build_user_profile(user_interest)

    scores = cosine_similarity(user_profile, embeddings)[0]
    top_idx = scores.argsort()[::-1][:5]

    return final_df.iloc[top_idx][["title", "datetime", "url"]]






