# CV Matching System

AI-powered CV parsing and job matching system with Next.js frontend and FastAPI backend.

## Features

- **CV Upload & Parsing**: Upload PDF/DOCX/TXT files and extract structured information
- **AI-Powered Matching**: SBERT embeddings + LightGBM ranking for accurate job-candidate matching
- **Search & Filter**: Advanced search with location, experience level, and skill filters
- **Real-time Results**: Instant matching scores with detailed explanations

## Quick Start

### 1. Prerequisites

- Python 3.8+
- Node.js 16+
- MongoDB
- Elasticsearch

### 2. Setup with Your Data

\`\`\`bash
# Clone and setup
git clone <your-repo>
cd cv-matching-system

# Setup database with your CSV files
bash scripts/run_setup.sh /path/to/jobs_clean.csv /path/to/candidates_parsed.csv

# Start the system
bash scripts/start_system.sh
\`\`\`

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## CSV Data Format

### Jobs CSV (jobs_clean.csv)
Required columns: `job_id`, `title`, `description`, `required_skills`, `salary_text`, `location_raw`, `company_raw`, `experience_level_raw`, `industry`, `job_type_raw`, `date_posted_raw`, `external_link`, `job_url`, `skills_norm`, `salary_currency`, `salary_period`, `salary_min_vnd`, `salary_max_vnd`, `location_norm`, `company_norm`, `experience_level`, `job_type`, `date_posted`, `posting_age_days`, `source_domain`, `external_valid`, `job_hash`

### Candidates CSV (candidates_parsed.csv)
Required columns: `cand_id`, `name`, `language`, `emails`, `phones`, `links`, `locations`, `skills_norm`, `exp_months`, `exp_years`, `exp_spans`, `experience_entries`, `education_entries`, `certs`, `resume_text`

## API Endpoints

- `POST /candidates/upload` - Upload and parse CV
- `POST /rank/candidates` - Rank candidates for a job
- `POST /search/jobs` - Search jobs for a candidate
- `GET /jobs` - List jobs with filters
- `GET /candidates` - List candidates

## Environment Configuration

Copy `.env.example` to `.env` and configure:

\`\`\`env
MONGO_URI=mongodb://localhost:27017
ES_HOST=http://localhost:9200
MODEL_DIR=./models
\`\`\`

## Development

\`\`\`bash
# Backend development
uvicorn app.main:app --reload

# Frontend development  
npm run dev
