import re
from pymongo import MongoClient
from datetime import datetime

# MongoDB connection
client = MongoClient('mongodb://localhost:27017')
db = client['matching_db']
jobs = db['jobs']

# Helper functions

def normalize_skills(skills):
    if isinstance(skills, str):
        return [s.strip().lower() for s in re.split(r',|;', skills) if s.strip()]
    if isinstance(skills, list):
        return [str(s).strip().lower() for s in skills if str(s).strip()]
    return []

def normalize_salary(salary):
    # Example: "35M VND/month - 41M VND/month"
    min_vnd, max_vnd, currency = None, None, "VND"
    if isinstance(salary, str):
        match = re.findall(r'(\d+)[Mm]', salary)
        if match:
            min_vnd = int(match[0]) * 1000000
            if len(match) > 1:
                max_vnd = int(match[1]) * 1000000
        if 'usd' in salary.lower():
            currency = 'USD'
    return min_vnd, max_vnd, currency

def normalize_date(date_str):
    # Try to parse DD/MM/YYYY or YYYY-MM-DD
    for fmt in ('%d/%m/%Y', '%Y-%m-%d'):
        try:
            return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
        except Exception:
            continue
    return date_str

def normalize_job(doc):
    min_vnd, max_vnd, currency = normalize_salary(doc.get('salary', ''))
    return {
        'title': doc.get('title', ''),
        'description': doc.get('description', ''),
        'skills_norm': normalize_skills(doc.get('skills', '')), 
        'salary_min_vnd': min_vnd,
        'salary_max_vnd': max_vnd,
        'salary_currency': currency,
        'experience_level': str(doc.get('experience', '')).lower().replace('-level', '').replace(' ', ''),
        'industry': doc.get('industry', ''),
        'date_posted': normalize_date(doc.get('date_posted', '')),
        'location_norm': str(doc.get('location', '')).lower(),
        'company_norm': str(doc.get('company', '')).lower(),
        'job_type': str(doc.get('job_type', '')).lower().replace('-', '').replace(' ', ''),
        'external_link': doc.get('externalApplyLink', doc.get('external_link', '')),
        'job_url': doc.get('url', doc.get('job_url', '')),
    }

if __name__ == "__main__":
    count = 0
    for doc in jobs.find():
        norm = normalize_job(doc)
        jobs.update_one({'_id': doc['_id']}, {'$set': norm})
        count += 1
    print(f"Normalized {count} jobs.")
