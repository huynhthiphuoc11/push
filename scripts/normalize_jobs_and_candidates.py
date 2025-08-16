import re
from pymongo import MongoClient

def normalize_skills(skills):
    if isinstance(skills, str):
        return [s.strip().lower() for s in re.split(r',|;', skills) if s.strip()]
    if isinstance(skills, list):
        return [str(s).strip().lower() for s in skills if str(s).strip()]
    return []

def normalize_location(loc):
    if isinstance(loc, str):
        return loc.strip().lower()
    if isinstance(loc, list):
        return [str(l).strip().lower() for l in loc if str(l).strip()]
    return loc

def normalize_experience_level(exp):
    if not exp:
        return ""
    s = str(exp).strip().lower()
    # Chuyển các dạng "mid-level", "junior", "senior", "lead" về chuẩn
    for key in ["junior", "mid", "senior", "lead"]:
        if key in s:
            return key
    # Nếu là số năm: "2 years", "3-5 years"
    import re
    m = re.findall(r"(\d+)", s)
    if m:
        return f"{m[0]} years"
    return s

def normalize_job(doc):
    doc["skills_norm"] = normalize_skills(doc.get("skills_norm", doc.get("skills", [])))
    doc["location_norm"] = normalize_location(doc.get("location_norm", doc.get("location", "")))
    doc["experience_level"] = normalize_experience_level(doc.get("experience_level", doc.get("experience", "")))
    doc["job_type"] = str(doc.get("job_type", "")).strip().lower()
    doc["industry"] = str(doc.get("industry", "")).strip().lower()
    doc["company_norm"] = str(doc.get("company_norm", doc.get("company", ""))).strip().lower()
    return doc

def normalize_candidate(doc):
    doc["skills_norm"] = normalize_skills(doc.get("skills_norm", doc.get("skills", [])))
    doc["locations"] = normalize_location(doc.get("locations", []))
    doc["exp_years"] = float(doc.get("exp_years", 0))
    name = str(doc.get("name", "")).strip()
    doc["name"] = name.upper() if name else ""
    return doc

if __name__ == "__main__":
    client = MongoClient('mongodb://localhost:27017')
    db = client['matching_db']
    jobs = db['jobs']
    candidates = db['candidates']
    # Chuẩn hóa jobs
    count_job = 0
    for doc in jobs.find():
        norm = normalize_job(doc)
        jobs.update_one({'_id': doc['_id']}, {'$set': norm})
        count_job += 1
    print(f"Normalized {count_job} jobs.")
    # Chuẩn hóa candidates
    count_cand = 0
    for doc in candidates.find():
        norm = normalize_candidate(doc)
        candidates.update_one({'_id': doc['_id']}, {'$set': norm})
        count_cand += 1
    print(f"Normalized {count_cand} candidates.")
