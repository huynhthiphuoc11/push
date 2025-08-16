import os
import json
import pandas as pd
import numpy as np
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import argparse
from datetime import datetime

def load_env_config():
    """Load environment configuration"""
    load_dotenv()
    return {
        'MONGO_URI': os.getenv('MONGO_URI', 'mongodb://localhost:27017'),
        'MONGO_DB': os.getenv('MONGO_DB', 'matching'),
        'MODEL_DIR': os.getenv('MODEL_DIR', './models'),
        'SBERT_MODEL': os.getenv('SBERT_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
    }

def setup_mongodb_collections(db):
    """Setup MongoDB collections with proper indexes"""
    
    # Jobs collection
    jobs_collection = db['jobs']
    
    # Create indexes for jobs
    jobs_collection.create_index('job_id', unique=True)
    jobs_collection.create_index('title')
    jobs_collection.create_index('skills_norm')
    jobs_collection.create_index('location_norm')
    jobs_collection.create_index('company_norm')
    jobs_collection.create_index('date_posted')
    
    # Candidates collection
    candidates_collection = db['candidates']
    
    # Create indexes for candidates
    candidates_collection.create_index('cand_id', unique=True)
    candidates_collection.create_index('name')
    candidates_collection.create_index('emails')
    candidates_collection.create_index('skills_norm')
    candidates_collection.create_index('locations')
    candidates_collection.create_index('exp_years')
    
    print("MongoDB collections and indexes created successfully")

    # Elasticsearch setup removed

def safe_json_loads(value):
    """Safely parse JSON strings, return empty list if invalid"""
    if pd.isna(value) or value == '' or value is None:
        return []
    
    if isinstance(value, list):
        return value
    
    if isinstance(value, str):
        try:
            if value.startswith('[') and value.endswith(']'):
                return json.loads(value)
            else:
                # Try to split by comma if it's a comma-separated string
                return [item.strip() for item in value.split(',') if item.strip()]
        except json.JSONDecodeError:
            # If JSON parsing fails, try splitting by common delimiters
            return [item.strip() for item in value.replace(';', ',').split(',') if item.strip()]
    
    return []

def import_jobs_data(jobs_csv_path, db, es, sbert_model, config):
    """Import jobs data from CSV to MongoDB and Elasticsearch"""
    
    print(f"Loading jobs data from {jobs_csv_path}")
    jobs_df = pd.read_csv(jobs_csv_path)
    
    jobs_collection = db['jobs']
    # jobs_index removed
    
    imported_count = 0
    
    for idx, row in jobs_df.iterrows():
        try:
            # Parse skills_norm
            skills_norm = safe_json_loads(row.get('skills_norm', '[]'))
            
            # Create job document
            job_doc = {
                'job_id': int(row.get('job_id', idx)),
                'title': str(row.get('title', '')).strip(),
                'description': str(row.get('description', '')).strip(),
                'required_skills': str(row.get('required_skills', '')).strip(),
                'skills_norm': skills_norm,
                'salary_text': str(row.get('salary_text', '')).strip(),
                'salary_currency': str(row.get('salary_currency', '')).strip(),
                'salary_period': str(row.get('salary_period', '')).strip(),
                'salary_min_vnd': float(row.get('salary_min_vnd', 0)) if pd.notna(row.get('salary_min_vnd')) else None,
                'salary_max_vnd': float(row.get('salary_max_vnd', 0)) if pd.notna(row.get('salary_max_vnd')) else None,
                'location_raw': str(row.get('location_raw', '')).strip(),
                'location_norm': str(row.get('location_norm', '')).strip(),
                'company_raw': str(row.get('company_raw', '')).strip(),
                'company_norm': str(row.get('company_norm', '')).strip(),
                'experience_level_raw': str(row.get('experience_level_raw', '')).strip(),
                'experience_level': str(row.get('experience_level', '')).strip(),
                'industry': str(row.get('industry', '')).strip(),
                'job_type_raw': str(row.get('job_type_raw', '')).strip(),
                'job_type': str(row.get('job_type', '')).strip(),
                'date_posted_raw': str(row.get('date_posted_raw', '')).strip(),
                'date_posted': row.get('date_posted') if pd.notna(row.get('date_posted')) else None,
                'posting_age_days': int(row.get('posting_age_days', 0)) if pd.notna(row.get('posting_age_days')) else None,
                'external_link': str(row.get('external_link', '')).strip(),
                'job_url': str(row.get('job_url', '')).strip(),
                'source_domain': str(row.get('source_domain', '')).strip(),
                'external_valid': bool(row.get('external_valid', False)) if pd.notna(row.get('external_valid')) else False,
                'job_hash': str(row.get('job_hash', '')).strip(),
                'imported_at': datetime.now().isoformat()
            }
            
            # Create text for embedding
            job_text = f"{job_doc['title']} {job_doc['description']} {' '.join(skills_norm)}"
            job_doc['job_text_orig'] = job_text
            
            # Generate embedding
            embedding = sbert_model.encode([job_text], normalize_embeddings=True)[0].tolist()
            job_doc['embedding'] = embedding
            
            # Insert/update in MongoDB
            jobs_collection.update_one(
                {'job_id': job_doc['job_id']},
                {'$set': job_doc},
                upsert=True
            )
            
            # Index in Elasticsearch
            es_doc = {
                'job_id': job_doc['job_id'],
                'title': job_doc['title'],
                'description': job_doc['description'],
                'text_orig': job_text,
                'text_sum': job_text,  # Could add summarization later
                'skills_norm': skills_norm,
                'location_norm': job_doc['location_norm'],
                'company_norm': job_doc['company_norm'],
                'experience_level': job_doc['experience_level'],
                'job_type': job_doc['job_type'],
                'industry': job_doc['industry'],
                'salary_min_vnd': job_doc['salary_min_vnd'],
                'salary_max_vnd': job_doc['salary_max_vnd'],
                'date_posted': job_doc['date_posted'],
                'embedding': embedding
            }
            
            # Elasticsearch indexing removed
            
            imported_count += 1
            
            if imported_count % 100 == 0:
                print(f"Imported {imported_count} jobs...")
                
        except Exception as e:
            print(f"Error importing job {idx}: {str(e)}")
            continue
    
    print(f"Successfully imported {imported_count} jobs")

def import_candidates_data(candidates_csv_path, db, es, sbert_model, config):
    """Import candidates data from CSV to MongoDB and Elasticsearch"""
    
    print(f"Loading candidates data from {candidates_csv_path}")
    candidates_df = pd.read_csv(candidates_csv_path)
    
    candidates_collection = db['candidates']
    # cands_index removed
    
    imported_count = 0
    
    for idx, row in candidates_df.iterrows():
        try:
            # Parse JSON fields
            skills_norm = safe_json_loads(row.get('skills_norm', '[]'))
            locations = safe_json_loads(row.get('locations', '[]'))
            emails = safe_json_loads(row.get('emails', '[]'))
            phones = safe_json_loads(row.get('phones', '[]'))
            links = safe_json_loads(row.get('links', '[]'))
            experience_entries = safe_json_loads(row.get('experience_entries', '[]'))
            education_entries = safe_json_loads(row.get('education_entries', '[]'))
            certs = safe_json_loads(row.get('certs', '[]'))
            
            # Create candidate document
            candidate_doc = {
                'cand_id': str(row.get('cand_id', f'candidate_{idx}')),
                'name': str(row.get('name', '')).strip(),
                'language': str(row.get('language', 'en')).strip(),
                'emails': emails,
                'phones': phones,
                'links': links,
                'locations': locations,
                'skills_norm': skills_norm,
                'exp_months': int(row.get('exp_months', 0)) if pd.notna(row.get('exp_months')) else 0,
                'exp_years': float(row.get('exp_years', 0)) if pd.notna(row.get('exp_years')) else 0,
                'exp_spans': str(row.get('exp_spans', '')).strip(),
                'experience_entries': experience_entries,
                'education_entries': education_entries,
                'certs': certs,
                'resume_text': str(row.get('resume_text', '')).strip(),
                'imported_at': datetime.now().isoformat()
            }
            
            # Create text for embedding
            candidate_text = f"{candidate_doc['resume_text']} {' '.join(skills_norm)}"
            candidate_doc['cand_text_orig'] = candidate_text
            
            # Generate embedding
            embedding = sbert_model.encode([candidate_text], normalize_embeddings=True)[0].tolist()
            candidate_doc['embedding'] = embedding
            
            # Insert/update in MongoDB
            candidates_collection.update_one(
                {'cand_id': candidate_doc['cand_id']},
                {'$set': candidate_doc},
                upsert=True
            )
            
            # Index in Elasticsearch
            es_doc = {
                'cand_id': candidate_doc['cand_id'],
                'name': candidate_doc['name'],
                'text_orig': candidate_text,
                'text_sum': candidate_text,  # Could add summarization later
                'skills_norm': skills_norm,
                'locations': locations,
                'exp_years': candidate_doc['exp_years'],
                'exp_months': candidate_doc['exp_months'],
                'language': candidate_doc['language'],
                'embedding': embedding
            }
            
            # Elasticsearch indexing removed
            
            imported_count += 1
            
            if imported_count % 100 == 0:
                print(f"Imported {imported_count} candidates...")
                
        except Exception as e:
            print(f"Error importing candidate {idx}: {str(e)}")
            continue
    
    print(f"Successfully imported {imported_count} candidates")

def main():
    parser = argparse.ArgumentParser(description='Setup MongoDB and import data')
    parser.add_argument('--jobs_csv', required=True, help='Path to jobs_clean.csv')
    parser.add_argument('--candidates_csv', required=True, help='Path to candidates_parsed.csv')
    parser.add_argument('--setup_only', action='store_true', help='Only setup database, skip data import')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_env_config()
    
    # Connect to MongoDB
    print("Connecting to MongoDB...")
    mongo_client = MongoClient(config['MONGO_URI'])
    db = mongo_client[config['MONGO_DB']]
    
    # Elasticsearch connection removed
    
    # Load SBERT model
    print("Loading SBERT model...")
    sbert_model = SentenceTransformer(config['SBERT_MODEL'])
    
    # Setup database collections and indices
    print("Setting up MongoDB collections...")
    setup_mongodb_collections(db)
    
    # Elasticsearch setup removed
    
    if not args.setup_only:
        # Import data
        if os.path.exists(args.jobs_csv):
            import_jobs_data(args.jobs_csv, db, None, sbert_model, config)
        else:
            print(f"Jobs CSV file not found: {args.jobs_csv}")
        
        if os.path.exists(args.candidates_csv):
            import_candidates_data(args.candidates_csv, db, None, sbert_model, config)
        else:
            print(f"Candidates CSV file not found: {args.candidates_csv}")
    
    print("Database setup completed successfully!")

if __name__ == "__main__":
    main()
