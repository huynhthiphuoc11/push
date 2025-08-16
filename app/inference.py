from __future__ import annotations
from typing import List, Dict, Any, Optional
import math

def _safe_lower_list(xs):
    if not xs: return []
    return [str(x).lower() for x in xs if isinstance(x, (str, int, float)) or x]

def _jaccard(a: set, b: set) -> float:
    if not a and not b: return 0.0
    return len(a & b) / max(1, len(a | b))

def _dot(a, b) -> float:
    if a is None or b is None: return 0.0
    # assume already normalized if created by encode(normalize_embeddings=True)
    return float(sum(x*y for x, y in zip(a, b))) if len(a) == len(b) else 0.0

class RankerService:
    """
    Service nhẹ nhàng: dùng Mongo + SBERT (nếu có) để tính điểm ngữ nghĩa + Jaccard skill + khớp location/industry.
    Tài nguyên được inject ở app.main: self.db, self.sbert_model, self.summarizer, self.ready
    """
    def __init__(self):
        self.ready = False
        self.db = None
        self.sbert_model = None
        self.summarizer = None

    # ---------- encode helper ----------
    def _encode(self, text: str) -> Optional[List[float]]:
        try:
            if self.sbert_model is None:
                return None
            return self.sbert_model.encode([text], normalize_embeddings=True)[0].tolist()
        except Exception:
            return None

    # ---------- scoring ----------
    def _score_job_cand(self, job: Dict[str, Any], cand: Dict[str, Any]) -> Dict[str, Any]:
        job_text = " ".join([
            str(job.get("title", "")),
            str(job.get("description", "")),
            " ".join(job.get("skills_norm", []) or [])
        ]).strip()

        cand_text = (cand.get("resume_summary") or cand.get("resume_text") or "").strip()

        job_vec = self._encode(job_text)
        cand_vec = cand.get("resume_embedding")
        if not cand_vec:
            cand_vec = self._encode(cand_text)

        semantic = _dot(job_vec, cand_vec)

        s_job = set(_safe_lower_list(job.get("skills_norm")))
        s_cand = set(_safe_lower_list(cand.get("skills_norm")))
        jacc = _jaccard(s_job, s_cand)
        overlap_skills = sorted(list(s_job & s_cand))
        missing_skills = sorted(list(s_job - s_cand))

        # Chuẩn hóa location: loại bỏ dấu, viết thường, rút gọn tên
        def _normalize_loc(loc):
            import re
            loc = str(loc).lower().strip()
            loc = re.sub(r"[^a-z0-9 ]", "", loc)
            # rút gọn các tên phổ biến
            if "ho chi minh" in loc or "hcm" in loc:
                return "ho chi minh city"
            if "ha noi" in loc or "hanoi" in loc:
                return "hanoi"
            if "da nang" in loc or "danang" in loc:
                return "da nang"
            return loc

        loc_job = _normalize_loc(job.get("location_norm", ""))
        locs_cand = set(_normalize_loc(l) for l in (cand.get("locations") or []))
        loc_match = 1.0 if loc_job and loc_job in locs_cand else 0.0

        def _to_years(x) -> float:
            if x is None: return 0.0
            if isinstance(x, (int, float)): return float(x)
            import re
            m = re.findall(r"(\d+(?:\.\d+)?)", str(x).lower())
            return float(m[-1]) if m else 0.0

        req_years = _to_years(job.get("experience_level"))
        cand_years = float(cand.get("exp_years") or 0.0)
        exp_ok = 1.0 if cand_years >= req_years else 0.0
        exp_gap = max(0.0, req_years - cand_years)

        score = (0.6 * semantic) + (0.3 * jacc) + (0.1 * (0.7*loc_match + 0.3*exp_ok))

        reasons = {
            "semantic": round(semantic, 4),
            "skill_jaccard": round(jacc, 4),
            "overlap_skills": overlap_skills[:12],
            "missing_skills": missing_skills[:12],
            "loc_job": loc_job,
            "loc_cand": list(locs_cand),
            "location_match": bool(loc_match),
            "exp_required_years": req_years,
            "exp_candidate_years": cand_years,
            "exp_gap": exp_gap,
            "score_hint": round(score, 4),
        }
        return {"score": float(score), "reasons": reasons}

    # ---------- public APIs ----------

    def score_jobs_by_keyword(self, keyword: str, top_k: int = 20) -> list:
        """
        Score all jobs in the database by relevance to the given keyword.
        Uses semantic similarity and keyword matching in title/description/skills.
        Returns top_k jobs sorted by score.
        """
        if not self.ready or self.db is None or not keyword:
            return []
        jobs_coll = self.db["jobs"]
        job_docs = list(jobs_coll.find({}, {"_id": 0}))

        keyword_lower = keyword.lower()
        keyword_vec = self._encode(keyword)
        scored = []
        for job in job_docs:
            job_text = " ".join([
                str(job.get("title", "")),
                str(job.get("description", "")),
                " ".join(job.get("skills_norm", []) or [])
            ]).strip()
            job_vec = self._encode(job_text)
            semantic = _dot(keyword_vec, job_vec) if keyword_vec and job_vec else 0.0

            # Keyword match boost
            title_match = keyword_lower in str(job.get("title", "")).lower()
            desc_match = keyword_lower in str(job.get("description", "")).lower()
            skills_match = any(keyword_lower in str(s).lower() for s in job.get("skills_norm", []) or [])
            match_boost = 0.2 * (title_match + desc_match + skills_match)

            score = semantic + match_boost

            job_norm = self._normalize_job_for_fe(job)
            scored.append({
                "job_id": job_norm.get("job_id", 0),
                "score": round(score, 4),
                "reasons": {
                    "semantic": round(semantic, 4),
                    "title_match": bool(title_match),
                    "desc_match": bool(desc_match),
                    "skills_match": bool(skills_match),
                    "match_boost": match_boost,
                },
                "title": job_norm.get("title", ""),
                "description": job_norm.get("description", ""),
                "company_norm": job_norm.get("company_norm", ""),
                "location_norm": job_norm.get("location_norm", ""),
                "experience_level": job_norm.get("experience_level", ""),
                "job_type": job_norm.get("job_type", ""),
                "industry": job_norm.get("industry", ""),
                "skills_norm": job_norm.get("skills_norm", []),
                "salary_min_vnd": job_norm.get("salary_min_vnd"),
                "salary_max_vnd": job_norm.get("salary_max_vnd"),
                "salary_currency": job_norm.get("salary_currency", "VND"),
                "date_posted": job_norm.get("date_posted"),
                "external_link": job_norm.get("external_link", ""),
            })
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:max(1, int(top_k))]
    def rank_candidates_for_job(self, job_id:int, top_k:int=20):
        if not self.ready or self.db is None:
            return []
        job = self.db["jobs"].find_one({"job_id": int(job_id)}, {"_id": 0})
        if not job:
            return []

        cand_docs = list(self.db["candidates"].find({}, {"_id": 0}))
        rows = []
        for c in cand_docs:
            sc = self._score_job_cand(job, c)
            rows.append({
                "cand_id": c.get("cand_id"),
                "score": sc["score"],
                "reasons": sc["reasons"]
            })

        rows.sort(key=lambda x: x["score"], reverse=True)
        return rows[: max(1, int(top_k))]

    def _capitalize_first(self, s):
        if isinstance(s, str) and s:
            return s[0].upper() + s[1:] if len(s) > 1 else s.upper()
        return s

    def _normalize_job_for_fe(self, job: dict) -> dict:
        # Viết hoa đầu dòng cho các trường hiển thị
        job = job.copy()
        for k in ["title", "company_norm", "location_norm", "experience_level", "job_type", "industry"]:
            if k in job and isinstance(job[k], str):
                job[k] = self._capitalize_first(job[k])
        return job

    def search_jobs_for_candidate(self, cand_id: Optional[str], keyword: Optional[str], top_k:int=10, location: Optional[str]=None):
        if not self.ready or self.db is None:
            return []
        jobs_coll = self.db["jobs"]

        # Build query for jobs
        query = {}
        if keyword:
            query["$or"] = [
                {"title": {"$regex": keyword, "$options": "i"}},
                {"description": {"$regex": keyword, "$options": "i"}},
                {"skills_norm": {"$elemMatch": {"$regex": keyword, "$options": "i"}}}
            ]
        if location and location.lower() != "all":
            query["location_norm"] = {"$regex": location, "$options": "i"}

        # Luôn lấy toàn bộ job đã lọc, không giới hạn số lượng
        job_docs = list(jobs_coll.find(query, {"_id": 0}))

        if cand_id:
            cand = self.db["candidates"].find_one({"cand_id": str(cand_id)}, {"_id": 0})
            if not cand:
                return []
            scored = []
            for j in job_docs:
                sc = self._score_job_cand(j, cand)
                job_norm = self._normalize_job_for_fe(j)
                scored.append({
                    "job_id": job_norm.get("job_id", 0),
                    "score": sc["score"],
                    "reasons": sc["reasons"],
                    "title": job_norm.get("title", ""),
                    "description": job_norm.get("description", ""),
                    "company_norm": job_norm.get("company_norm", ""),
                    "location_norm": job_norm.get("location_norm", ""),
                    "experience_level": job_norm.get("experience_level", ""),
                    "job_type": job_norm.get("job_type", ""),
                    "industry": job_norm.get("industry", ""),
                    "skills_norm": job_norm.get("skills_norm", []),
                    "salary_min_vnd": job_norm.get("salary_min_vnd"),
                    "salary_max_vnd": job_norm.get("salary_max_vnd"),
                    "salary_currency": job_norm.get("salary_currency", "VND"),
                    "date_posted": job_norm.get("date_posted"),
                    "external_link": job_norm.get("external_link", ""),
                })
            # Sort toàn bộ job đã lọc theo score, lấy top_k
            scored.sort(key=lambda x: x["score"], reverse=True)
            return scored[:max(1, int(top_k))]
        else:
            jobs_out = []
            for j in job_docs:
                job_norm = self._normalize_job_for_fe(j)
                jobs_out.append({
                    "job_id": job_norm.get("job_id", 0),
                    "score": 0.0,
                    "reasons": {},
                    "title": job_norm.get("title", ""),
                    "description": job_norm.get("description", ""),
                    "company_norm": job_norm.get("company_norm", ""),
                    "location_norm": job_norm.get("location_norm", ""),
                    "experience_level": job_norm.get("experience_level", ""),
                    "job_type": job_norm.get("job_type", ""),
                    "industry": job_norm.get("industry", ""),
                    "skills_norm": job_norm.get("skills_norm", []),
                    "salary_min_vnd": job_norm.get("salary_min_vnd"),
                    "salary_max_vnd": job_norm.get("salary_max_vnd"),
                    "salary_currency": job_norm.get("salary_currency", "VND"),
                    "date_posted": job_norm.get("date_posted"),
                    "external_link": job_norm.get("external_link", ""),
                })
            return jobs_out[:max(1, int(top_k))]
