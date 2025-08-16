from __future__ import annotations
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class RankRequest(BaseModel):
    job_id: int
    top_k: int = 20

class RankResponseItem(BaseModel):
    cand_id: str
    score: float
    reasons: Dict[str, Any]

class JobSearchRequest(BaseModel):
    cand_id: Optional[str] = None
    keyword: Optional[str] = None
    top_k: int = 20

class JobSearchResponseItem(BaseModel):
    job_id: int
    score: float
    reasons: Dict[str, Any]
    title: str = ""
    description: str = ""
    company_norm: str = ""
    location_norm: str = ""
    experience_level: str = ""
    job_type: str = ""
    industry: str = ""
    skills_norm: List[str] = []
    salary_min_vnd: Optional[float] = None
    salary_max_vnd: Optional[float] = None
    salary_currency: str = "VND"
    date_posted: Optional[str] = None
    external_link: Optional[str] = None

class CandidateInfo(BaseModel):
    cand_id: str
    name: str
    emails: List[str] = []
    phones: List[str] = []
    locations: List[str] = []
    skills_norm: List[str] = []
    exp_years: float = 0
    experience_entries: List[str] = []
    education_entries: List[str] = []

class UploadResponse(BaseModel):
    success: bool
    message: str
    candidate: Optional[CandidateInfo] = None
    error: Optional[str] = None

class JobDetails(BaseModel):
    job_id: int
    title: str
    description: str
    company_norm: str
    location_norm: str
    experience_level: str
    job_type: str
    industry: str
    skills_norm: List[str]
    salary_min_vnd: Optional[float] = None
    salary_max_vnd: Optional[float] = None
    salary_currency: str = "VND"
    date_posted: Optional[str] = None
    external_link: Optional[str] = None
    job_url: Optional[str] = None
