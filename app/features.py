
# ==== Feature Engineering Functions (from notebook) ====
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple

def normalize_text(s: str) -> str:
    return " ".join(str(s).lower().strip().split())

def jaccard(a: set, b: set) -> float:
    if not a and not b: return 0.0
    return len(a & b) / max(1, len(a | b))

def keyword_overlap(job_terms: set, cv_terms: set) -> float:
    if not job_terms or not cv_terms: return 0.0
    return len(job_terms & cv_terms) / max(1, len(job_terms))

def exp_gap_penalty(required_years: int, cand_years: int) -> float:
    gap = max(0, required_years - cand_years)
    return gap / (required_years + 1e-6)

def group_weighted_skill_score(job_skills: set, cv_skills: set, tech_group=None, soft_group=None) -> float:
    inter = job_skills & cv_skills
    if not inter: return 0.0
    score = 0.0
    for s in inter:
        if tech_group and s in tech_group: score += 1.0
        elif soft_group and s in soft_group: score += 0.3
        else: score += 0.5
    return score / (len(job_skills) + 1e-6)

def location_match(job_location: str, cand_locations: List[str]) -> float:
    job_location = job_location.lower()
    cand_locations = [loc.lower() for loc in cand_locations]
    return 1.0 if any(loc in job_location for loc in cand_locations) else 0.0

# BM25-lite implementation
class BM25OkapiLite:
    def __init__(self, corpus_tokens, k1=1.5, b=0.75):
        self.k1 = k1; self.b = b
        self.corpus = corpus_tokens
        self.doc_freq = {}
        self.doc_len = [len(d) for d in corpus_tokens]
        self.avgdl = np.mean(self.doc_len) if self.doc_len else 0.0
        for doc in corpus_tokens:
            for w in set(doc):
                self.doc_freq[w] = self.doc_freq.get(w, 0) + 1
        self.N = len(corpus_tokens)
    def idf(self, term):
        n_qi = self.doc_freq.get(term, 0) + 0.5
        return np.log((self.N - n_qi + 0.5) / n_qi + 1.0)
    def score(self, query_tokens, index):
        score = 0.0; doc = self.corpus[index]; dl = len(doc) or 1
        for t in query_tokens:
            f = doc.count(t)
            if f == 0: continue
            idf = self.idf(t)
            denom = f + self.k1*(1 - self.b + self.b*dl/(self.avgdl + 1e-9))
            score += idf * (f*(self.k1+1)) / denom
        return score
    def get_scores(self, query_tokens):
        return np.array([self.score(query_tokens, i) for i in range(self.N)])

def tokenize_simple(s: str): return normalize_text(s).split()

# FAISS retrieval (assume index built outside)
def faiss_retrieve(query_emb, faiss_index, top_k=100):
    if faiss_index is None: return []
    D, I = faiss_index.search(np.asarray([query_emb], dtype="float32"), top_k)
    return I[0].tolist()

# ==== Feature Matrix Builder ====
def build_features_for_pairs(job_doc: dict, cand_docs: List[dict], sbert=None, bm25=None, faiss_index=None, tech_group=None, soft_group=None) -> Tuple[np.ndarray, 'pd.DataFrame']:
    features = []
    meta_data = []
    job_skills = set(job_doc.get('skills_norm', []))
    job_location = job_doc.get('location', '')
    job_exp = job_doc.get('required_exp', 0)
    job_terms = set(tokenize_simple(job_doc.get('description', '')))
    job_embed = None
    if sbert:
        job_embed = sbert.encode([job_doc.get('description', '')], normalize_embeddings=True)[0]
    for cand_doc in cand_docs:
        cand_skills = set(cand_doc.get('skills_norm', []))
        cand_locations = cand_doc.get('locations', [])
        cand_exp = cand_doc.get('exp_years', 0)
        cand_terms = set(tokenize_simple(cand_doc.get('resume_text', '')))
        cand_embed = None
        if sbert:
            cand_embed = sbert.encode([cand_doc.get('resume_text', '')], normalize_embeddings=True)[0]
        # Semantic cosine
        sem_cos = float(np.dot(job_embed, cand_embed)) if job_embed is not None and cand_embed is not None else 0.0
        # Keyword overlap
        kw_overlap = keyword_overlap(job_terms, cand_terms)
        # Skill jaccard
        skill_jacc = jaccard(job_skills, cand_skills)
        # Group weighted skill
        group_skill = group_weighted_skill_score(job_skills, cand_skills, tech_group, soft_group)
        # Exp gap penalty
        exp_penalty = exp_gap_penalty(job_exp, cand_exp)
        # Location match
        loc_match = location_match(job_location, cand_locations)
        # BM25 score
        bm25_score = 0.0
        if bm25:
            bm25_score = bm25.get_scores(tokenize_simple(job_doc.get('description', '')))[0]
        # FAISS retrieval (optional)
        faiss_score = 0.0
        if faiss_index and cand_embed is not None:
            faiss_ids = faiss_retrieve(job_embed, faiss_index, top_k=100)
            faiss_score = 1.0 if cand_doc.get('cand_id', '') in faiss_ids else 0.0
        feature_vector = [sem_cos, kw_overlap, skill_jacc, group_skill, exp_penalty, loc_match, bm25_score, faiss_score]
        features.append(feature_vector)
        meta_data.append({
            'job_id': job_doc.get('job_id', ''),
            'cand_id': cand_doc.get('cand_id', ''),
            'doc': cand_doc
        })
    X = np.array(features)
    meta_df = None
    try:
        import pandas as pd
        meta_df = pd.DataFrame(meta_data)
    except ImportError:
        meta_df = meta_data
    return X, meta_df

def build_features_for_pairs(job_doc: dict = None, cand_docs: List[dict] = None, 
                           bm25_scores: Dict[str, float] = None,
                           use_summary: bool = True, sbert = None, skill_w: Dict = None,
                           reverse: bool = False, fixed_cand: dict = None) -> Tuple[np.ndarray, pd.DataFrame]:
    """
    Build feature matrix for job-candidate pairs
    """
    if reverse and fixed_cand:
        # Candidate searching for jobs
        features = []
        meta_data = []
        
        for job_doc in cand_docs:  # Actually job docs in reverse mode
            job_id = str(job_doc.get('job_id', ''))
            
            # Basic features
            bm25_score = bm25_scores.get(job_id, 0.0)
            
            # Skills overlap
            cand_skills = set(fixed_cand.get('skills_norm', []))
            job_skills = set(job_doc.get('skills_norm', []))
            skills_overlap = len(cand_skills.intersection(job_skills))
            skills_union = len(cand_skills.union(job_skills))
            skills_jaccard = skills_overlap / skills_union if skills_union > 0 else 0.0
            
            # Experience match
            cand_exp = fixed_cand.get('exp_years', 0)
            job_exp_level = job_doc.get('experience_level', '').lower()
            exp_match = 0.5  # Default neutral
            if 'junior' in job_exp_level and cand_exp <= 2:
                exp_match = 1.0
            elif 'senior' in job_exp_level and cand_exp >= 5:
                exp_match = 1.0
            elif 'mid' in job_exp_level and 2 < cand_exp < 5:
                exp_match = 1.0
            
            # Location match
            cand_locations = [loc.lower() for loc in fixed_cand.get('locations', [])]
            job_location = job_doc.get('location_norm', '').lower()
            location_match = 1.0 if any(loc in job_location for loc in cand_locations) else 0.0
            
            # Feature vector: [bm25, sbert_placeholder, skills_jaccard, exp_match, location_match]
            feature_vector = [bm25_score, bm25_score * 0.8, skills_jaccard, exp_match, location_match]
            features.append(feature_vector)
            
            meta_data.append({
                'job_id': job_id,
                'cand_id': fixed_cand.get('cand_id', ''),
                'doc': job_doc
            })
    else:
        # Job searching for candidates
        features = []
        meta_data = []
        
        for cand_doc in cand_docs:
            cand_id = str(cand_doc.get('cand_id', ''))
            
            # Basic features
            bm25_score = bm25_scores.get(cand_id, 0.0)
            
            # Skills overlap
            job_skills = set(job_doc.get('skills_norm', []))
            cand_skills = set(cand_doc.get('skills_norm', []))
            skills_overlap = len(job_skills.intersection(cand_skills))
            skills_union = len(job_skills.union(cand_skills))
            skills_jaccard = skills_overlap / skills_union if skills_union > 0 else 0.0
            
            # Experience match
            cand_exp = cand_doc.get('exp_years', 0)
            job_exp_level = job_doc.get('experience_level', '').lower()
            exp_match = 0.5  # Default neutral
            if 'junior' in job_exp_level and cand_exp <= 2:
                exp_match = 1.0
            elif 'senior' in job_exp_level and cand_exp >= 5:
                exp_match = 1.0
            elif 'mid' in job_exp_level and 2 < cand_exp < 5:
                exp_match = 1.0
            
            # Location match
            cand_locations = [loc.lower() for loc in cand_doc.get('locations', [])]
            job_location = job_doc.get('location_norm', '').lower()
            location_match = 1.0 if any(loc in job_location for loc in cand_locations) else 0.0
            
            # Feature vector: [bm25, sbert_placeholder, skills_jaccard, exp_match, location_match]
            feature_vector = [bm25_score, bm25_score * 0.8, skills_jaccard, exp_match, location_match]
            features.append(feature_vector)
            
            meta_data.append({
                'job_id': job_doc.get('job_id', ''),
                'cand_id': cand_id,
                'doc': cand_doc
            })
    
    X = np.array(features)
    meta_df = pd.DataFrame(meta_data)
    
    return X, meta_df

def explain_reasons(job_doc: dict, cand_doc: dict, score: float, reverse: bool = False) -> Dict[str, Any]:
    """
    Generate explanation for matching score
    """
    if reverse:
        # Explaining why job matches candidate
        job_skills = set(job_doc.get('skills_norm', []))
        cand_skills = set(cand_doc.get('skills_norm', []))
        
        matching_skills = list(job_skills.intersection(cand_skills))
        missing_skills = list(job_skills - cand_skills)
        
        return {
            "score": float(score),
            "matching_skills": matching_skills,
            "missing_skills": missing_skills,
            "experience_match": _check_experience_match(job_doc, cand_doc),
            "location_match": _check_location_match(job_doc, cand_doc)
        }
    else:
        # Explaining why candidate matches job
        job_skills = set(job_doc.get('skills_norm', []))
        cand_skills = set(cand_doc.get('skills_norm', []))
        
        matching_skills = list(job_skills.intersection(cand_skills))
        missing_skills = list(job_skills - cand_skills)
        extra_skills = list(cand_skills - job_skills)
        
        return {
            "score": float(score),
            "matching_skills": matching_skills,
            "missing_skills": missing_skills,
            "extra_skills": extra_skills,
            "experience_match": _check_experience_match(job_doc, cand_doc),
            "location_match": _check_location_match(job_doc, cand_doc)
        }

def _check_experience_match(job_doc: dict, cand_doc: dict) -> Dict[str, Any]:
    """Check if candidate experience matches job requirements"""
    cand_exp = cand_doc.get('exp_years', 0)
    job_exp_level = job_doc.get('experience_level', '').lower()
    
    if 'junior' in job_exp_level:
        required_exp = "0-2 years"
        match = cand_exp <= 2
    elif 'senior' in job_exp_level:
        required_exp = "5+ years"
        match = cand_exp >= 5
    elif 'mid' in job_exp_level:
        required_exp = "2-5 years"
        match = 2 <= cand_exp <= 5
    else:
        required_exp = "Not specified"
        match = True
    
    return {
        "candidate_experience": f"{cand_exp} years",
        "required_experience": required_exp,
        "match": match
    }

def _check_location_match(job_doc: dict, cand_doc: dict) -> Dict[str, Any]:
    """Check if candidate location matches job location"""
    cand_locations = [loc.lower() for loc in cand_doc.get('locations', [])]
    job_location = job_doc.get('location_norm', '').lower()
    
    match = any(loc in job_location for loc in cand_locations) if cand_locations else False
    
    return {
        "candidate_locations": cand_doc.get('locations', []),
        "job_location": job_doc.get('location_norm', ''),
        "match": match
    }
