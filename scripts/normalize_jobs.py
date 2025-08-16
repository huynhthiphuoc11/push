"""
Script to normalize job documents in MongoDB for CV Matching System
- Converts non-standard field names to backend schema: title, description, skills, location, company, salary, requirements, etc.
- Run: python scripts/normalize_jobs.py
"""
from pymongo import MongoClient

# MongoDB connection
client = MongoClient('mongodb://localhost:27017')
db = client['matching_db']
jobs = db['jobs']

# Field mapping: old field name -> new field name
FIELD_MAP = {
    'Job Title': 'title',
    'Description': 'description',
    'Job Description': 'description',
    'Skills': 'skills',
    'Required Skills': 'skills',
    'Location': 'location',
    'Company': 'company',
    'Salary': 'salary',
    'Salary Range': 'salary',
    'Requirements': 'requirements',
    'Benefits': 'benefits',
    'Job Type': 'job_type',
    'Experience': 'experience',
    'Experience Level': 'experience',
    'Industry': 'industry',
    'Date Posted': 'date_posted',
    # Add more mappings as needed
}

def normalize_job(doc):
    new_doc = {}
    for old, new in FIELD_MAP.items():
        if old in doc and doc[old] not in [None, '', 0]:
            new_doc[new] = doc[old]
    # Preserve _id
    new_doc['_id'] = doc['_id']
    # Copy other fields if needed, but skip unwanted fields
    skip_fields = set(list(FIELD_MAP.keys()) + ['JobID', 'Job Description\t', 'All'])
    for k in doc:
        if k not in skip_fields and k != '_id':
            new_doc[k] = doc[k]
    return new_doc

def main():
    count = 0
    for doc in jobs.find():
        new_doc = normalize_job(doc)
        jobs.replace_one({'_id': doc['_id']}, new_doc)
        count += 1
    print(f'Normalized {count} job documents.')

if __name__ == '__main__':
    main()
