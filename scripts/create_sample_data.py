import json
import pandas as pd
from datetime import datetime, timedelta
import random

def create_sample_jobs():
    """Create sample jobs data for testing"""
    
    sample_jobs = [
        {
            'job_id': 1,
            'title': 'Senior Python Developer',
            'description': 'We are looking for a Senior Python Developer with experience in Django, FastAPI, and PostgreSQL. The ideal candidate should have 3+ years of experience in web development.',
            'required_skills': 'Python, Django, FastAPI, PostgreSQL, REST API',
            'skills_norm': ['python', 'django', 'fastapi', 'postgresql', 'rest api'],
            'salary_text': '25-35 million VND',
            'salary_currency': 'VND',
            'salary_period': 'monthly',
            'salary_min_vnd': 25000000,
            'salary_max_vnd': 35000000,
            'location_raw': 'Ho Chi Minh City',
            'location_norm': 'ho chi minh city',
            'company_raw': 'Tech Solutions Ltd',
            'company_norm': 'tech solutions ltd',
            'experience_level_raw': 'Senior',
            'experience_level': 'senior',
            'industry': 'Information Technology',
            'job_type_raw': 'Full-time',
            'job_type': 'full-time',
            'date_posted_raw': '2024-01-15',
            'date_posted': '2024-01-15',
            'posting_age_days': 30,
            'external_link': 'https://example.com/job/1',
            'job_url': 'https://example.com/job/1',
            'source_domain': 'example.com',
            'external_valid': True,
            'job_hash': 'hash1'
        },
        {
            'job_id': 2,
            'title': 'Frontend React Developer',
            'description': 'Join our team as a Frontend Developer specializing in React.js. You will work on modern web applications using React, TypeScript, and Tailwind CSS.',
            'required_skills': 'React, JavaScript, TypeScript, HTML, CSS, Tailwind',
            'skills_norm': ['react', 'javascript', 'typescript', 'html', 'css', 'tailwind'],
            'salary_text': '20-30 million VND',
            'salary_currency': 'VND',
            'salary_period': 'monthly',
            'salary_min_vnd': 20000000,
            'salary_max_vnd': 30000000,
            'location_raw': 'Hanoi',
            'location_norm': 'hanoi',
            'company_raw': 'Digital Agency Co',
            'company_norm': 'digital agency co',
            'experience_level_raw': 'Mid-level',
            'experience_level': 'mid',
            'industry': 'Information Technology',
            'job_type_raw': 'Full-time',
            'job_type': 'full-time',
            'date_posted_raw': '2024-01-20',
            'date_posted': '2024-01-20',
            'posting_age_days': 25,
            'external_link': 'https://example.com/job/2',
            'job_url': 'https://example.com/job/2',
            'source_domain': 'example.com',
            'external_valid': True,
            'job_hash': 'hash2'
        }
    ]
    
    df = pd.DataFrame(sample_jobs)
    df.to_csv('sample_jobs.csv', index=False)
    print("Created sample_jobs.csv")

def create_sample_candidates():
    """Create sample candidates data for testing"""
    
    sample_candidates = [
        {
            'cand_id': 'candidate_001',
            'name': 'Nguyen Van A',
            'language': 'en',
            'emails': ['nguyenvana@email.com'],
            'phones': ['+84901234567'],
            'links': ['https://linkedin.com/in/nguyenvana'],
            'locations': ['ho chi minh city'],
            'skills_norm': ['python', 'django', 'postgresql', 'react', 'javascript'],
            'exp_months': 36,
            'exp_years': 3,
            'exp_spans': '3 years',
            'experience_entries': ['Software Developer at ABC Company (2021-2024)', 'Junior Developer at XYZ Corp (2020-2021)'],
            'education_entries': ['Bachelor of Computer Science, University of Technology'],
            'certs': ['AWS Certified Developer'],
            'resume_text': 'Experienced software developer with 3 years of experience in Python, Django, and web development. Skilled in React.js, PostgreSQL, and cloud technologies.'
        },
        {
            'cand_id': 'candidate_002',
            'name': 'Tran Thi B',
            'language': 'en',
            'emails': ['tranthib@email.com'],
            'phones': ['+84987654321'],
            'links': ['https://github.com/tranthib'],
            'locations': ['hanoi'],
            'skills_norm': ['react', 'javascript', 'typescript', 'html', 'css', 'nodejs'],
            'exp_months': 24,
            'exp_years': 2,
            'exp_spans': '2 years',
            'experience_entries': ['Frontend Developer at Tech Startup (2022-2024)', 'Intern Developer at Software House (2021-2022)'],
            'education_entries': ['Bachelor of Information Technology, Hanoi University'],
            'certs': [],
            'resume_text': 'Frontend developer specializing in React.js and modern JavaScript. Experience with TypeScript, HTML5, CSS3, and responsive web design.'
        }
    ]
    
    # Convert lists to JSON strings for CSV compatibility
    for candidate in sample_candidates:
        for field in ['emails', 'phones', 'links', 'locations', 'skills_norm', 'experience_entries', 'education_entries', 'certs']:
            candidate[field] = json.dumps(candidate[field])
    
    df = pd.DataFrame(sample_candidates)
    df.to_csv('sample_candidates.csv', index=False)
    print("Created sample_candidates.csv")

if __name__ == "__main__":
    create_sample_jobs()
    create_sample_candidates()
