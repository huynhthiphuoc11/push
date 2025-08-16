import os
from typing import List, Dict
from contextlib import asynccontextmanager
import re

from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

from app.services.summarizer import BartSummarizer
from app.inference import RankerService
from app.schemas import (
    RankRequest, RankResponseItem,
    JobSearchRequest, JobSearchResponseItem,
    JobDetails,
)
from app.upload import router as upload_router

# ------------ Skill groups (cho /analyze/keywords) ------------
TECH_GROUP = {
    "python","java","javascript","typescript","c#","cpp","php","go",
    "html","css","react","vue","node.js","django","flask","spring",
    "sql","nosql","aws","gcp","azure","docker","kubernetes","spark","hadoop"
}
SOFT_GROUP = {"communication","teamwork","problem-solving"}
BUZZWORDS = {"agile","scrum","devops","cloud","ai","ml","data science","big data","microservices","blockchain"}

# ------------ Service instance (inject tài nguyên trong lifespan) ------------
svc = RankerService()
svc.ready = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Config
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    mongo_db  = os.getenv("MONGO_DB",  "matching_db")
    sbert_id  = os.getenv("SBERT_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    bart_id   = os.getenv("BART_MODEL",  "facebook/bart-base")

    # Mongo
    mcli = MongoClient(mongo_uri)
    db = mcli[mongo_db]
    existing = set(db.list_collection_names())
    if "candidates" not in existing: db.create_collection("candidates")
    if "jobs" not in existing: db.create_collection("jobs")

    # SBERT
    try:
        sbert = SentenceTransformer(sbert_id)
    except Exception:
        sbert = None  # fallback semantic = 0

    # BART (fallback nếu lỗi)
    try:
        summarizer = BartSummarizer(model_id=bart_id)
    except Exception:
        class _NoopSum:
            def summarize(self, text: str) -> str:
                return (text or "")[:1200]
        summarizer = _NoopSum()

    # Expose vào app.state và inject vào service
    app.state.db = db
    app.state.sbert_model = sbert
    app.state.bart_summarizer = summarizer

    svc.db = db
    svc.sbert_model = sbert
    svc.summarizer = summarizer
    svc.ready = True
    app.state.svc = svc

    try:
        yield
    finally:
        svc.ready = False
        # mcli.close()  # tùy bạn

# ------------ FastAPI app ------------
app = FastAPI(title="JD/CV Matching API", version="1.0", lifespan=lifespan)

# ------------ CORS ------------
origins_env = os.getenv("CORS_ORIGINS", "*")
origins = [o.strip() for o in origins_env.split(",")] if origins_env else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if origins == ["*"] else origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------ Routers (/candidates/*: upload + upload-and-match + summary + matches) ------------
app.include_router(upload_router)

# ------------ Health ------------
@app.get("/health")
def health():
    return {"status": "ok", "ready": bool(getattr(svc, "ready", False))}

# ------------ Ranking / Search ------------
@app.post("/rank/candidates", response_model=list[RankResponseItem], tags=["ranking"])
def rank_candidates(req: RankRequest):
    if not getattr(svc, "ready", False):
        raise HTTPException(status_code=503, detail="Service not ready")
    return svc.rank_candidates_for_job(req.job_id, req.top_k)

@app.post("/search/jobs", tags=["ranking"])
def search_jobs(req: JobSearchRequest):
    if not getattr(svc, "ready", False):
        raise HTTPException(status_code=503, detail="Service not ready")
    return svc.search_jobs_for_candidate(req.cand_id, req.keyword, req.top_k)

# ------------ Keyword grouping ------------
def group_keywords(skills: List[str]) -> Dict[str, List[str]]:
    tech = [s for s in skills if s.lower() in TECH_GROUP]
    soft = [s for s in skills if s.lower() in SOFT_GROUP]
    buzz = [s for s in skills if s.lower() in BUZZWORDS]
    other = [s for s in skills if s.lower() not in (TECH_GROUP | SOFT_GROUP | BUZZWORDS)]
    return {"technical": tech, "soft": soft, "buzzwords": buzz, "other": other}

@app.post("/analyze/keywords", tags=["utils"])
def analyze_keywords(keywords: List[str] = Body(..., embed=True)):
    return group_keywords(keywords)

# ------------ Jobs ------------
@app.get("/jobs", response_model=list[Dict], tags=["jobs"])
def get_jobs():
    db = app.state.db
    jobs = [map_job_fields(job) for job in db["jobs"].find({}, {"_id": 0})]
    return jobs

@app.get("/jobs/{job_id}", response_model=JobDetails, tags=["jobs"])
def get_job_details(job_id: int):
    db = app.state.db
    job = db["jobs"].find_one({"job_id": int(job_id)}, {"_id": 0})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobDetails(
        job_id=job.get("job_id", 0),
        title=job.get("title", ""),
        description=job.get("description", ""),
        company_norm=job.get("company_norm", ""),
        location_norm=job.get("location_norm", ""),
        experience_level=job.get("experience_level", ""),
        job_type=job.get("job_type", ""),
        industry=job.get("industry", ""),
        skills_norm=job.get("skills_norm", []),
        salary_min_vnd=job.get("salary_min_vnd"),
        salary_max_vnd=job.get("salary_max_vnd"),
        salary_currency=job.get("salary_currency", "VND"),
        date_posted=job.get("date_posted"),
        external_link=job.get("external_link", ""),
        job_url=job.get("job_url", job.get("external_link", ""))
    )

# ------------ Candidates (read-only) ------------
@app.get("/candidates", response_model=list[Dict], tags=["candidates"])
def get_candidates():
    db = app.state.db
    return list(db["candidates"].find({}, {"_id": 0}))

@app.get("/candidates/{cand_id}", response_model=Dict, tags=["candidates"])
def get_candidate_details(cand_id: str):  # UUID string
    db = app.state.db
    candidate = db["candidates"].find_one({"cand_id": cand_id}, {"_id": 0})
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate

load_dotenv()  # Tự động đọc file .env trong thư mục dự án
@app.get("/debug/deps")
def debug_deps():
    return {
        "db": bool(getattr(app.state, "db", None)),
        "sbert": bool(getattr(app.state, "sbert_model", None)),
        "bart": bool(getattr(app.state, "bart_summarizer", None)),
        "svc_ready": bool(getattr(app.state, "svc", None) and getattr(app.state.svc, "ready", False)),
    }

def parse_salary_range(salary_str):
    # Ví dụ: "35M VND/month - 41M VND/month"
    matches = re.findall(r"(\d+)[Mm]", salary_str)
    if len(matches) == 2:
        min_salary = int(matches[0]) * 1000000
        max_salary = int(matches[1]) * 1000000
        return min_salary, max_salary
    return None, None

def map_job_fields(job):
    min_salary, max_salary = parse_salary_range(job.get("Salary Range", ""))
    return {
        "job_id": job.get("JobID", 0),
        "title": job.get("Job Title", ""),
        "description": job.get("Job Description", ""),
        "company_norm": job.get("Company", ""),
        "location_norm": job.get("Location", ""),
        "experience_level": job.get("Experience Level", ""),
        "job_type": job.get("Job Type", ""),
        "industry": job.get("Industry", ""),
        "skills_norm": [s.strip() for s in job.get("Required Skills", "").split(",")],
        "salary_min_vnd": min_salary,
        "salary_max_vnd": max_salary,
        "salary_currency": "VND",
        "date_posted": job.get("Date Posted", ""),
        "external_link": job.get("externalApplyLink", "") or job.get("url", ""),
        "job_url": job.get("url", ""),
    }
