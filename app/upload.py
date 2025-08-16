# app/upload.py
import os
import logging, traceback
from io import BytesIO
from typing import List, Dict, Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request, status
from pymongo.database import Database
from sentence_transformers import SentenceTransformer
import PyPDF2
import docx
    # (Removed stray indented block causing syntax error)

from app.schemas import UploadResponse, CandidateInfo, JobSearchResponseItem
from app.services.summarizer import BartSummarizer
from scripts.parse_cv import parse_cv_file  # đảm bảo path đúng

router = APIRouter(prefix="/candidates", tags=["candidates"])
logger = logging.getLogger("upload")

# ---------- Dependencies ----------
def get_database(request: Request) -> Database:
    db: Optional[Database] = getattr(request.app.state, "db", None)
    if db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return db

def get_sbert(request: Request) -> Optional[SentenceTransformer]:
    return getattr(request.app.state, "sbert_model", None)

def get_summarizer(request: Request) -> Optional[BartSummarizer]:
    return getattr(request.app.state, "bart_summarizer", None)

def get_ranker(request: Request):
    svc = getattr(request.app.state, "svc", None)
    if svc is None or not getattr(svc, "ready", False):
        raise HTTPException(status_code=503, detail="Ranker service not ready")
    return svc

# ---------- File extract helpers ----------
def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        reader = PyPDF2.PdfReader(BytesIO(file_bytes))
        texts = []
        for page in reader.pages:
            texts.append((page.extract_text() or ""))
        return "\n".join(texts).strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

def extract_text_from_docx(file_bytes: bytes) -> str:
    try:
        d = docx.Document(BytesIO(file_bytes))
        return "\n".join(p.text for p in d.paragraphs).strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading DOCX: {str(e)}")

def extract_text_from_file(filename: str, file_bytes: bytes) -> str:
    name = (filename or "").lower()
    if name.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    if name.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    if name.endswith(".txt"):
        for enc in ("utf-8", "latin-1"):
            try:
                return file_bytes.decode(enc)
            except UnicodeDecodeError:
                continue
        raise HTTPException(status_code=400, detail="Unable to decode text file (utf-8/latin-1).")
    if name.endswith(".doc"):
        raise HTTPException(status_code=400, detail="Legacy .doc is not supported. Please upload PDF/DOCX/TXT.")
    raise HTTPException(status_code=400, detail="Unsupported file type. Please upload PDF, DOCX, or TXT.")

# ---------- Safe helpers ----------
def safe_summarize(bart_summarizer: Optional[BartSummarizer], text: str) -> str:
    try:
        if bart_summarizer is None:
            return (text or "")[:1200]
        return bart_summarizer.summarize(text) or ""
    except Exception as e:
        logger.warning("BART summarize failed: %s", e)
        return (text or "")[:1200]

def safe_encode(sbert_model: Optional[SentenceTransformer], text: str):
    try:
        if sbert_model is None:
            return None
        return sbert_model.encode([text], normalize_embeddings=True)[0].tolist()
    except Exception as e:
        logger.warning("SBERT encode failed: %s", e)
        return None

# ---------- Upsert ----------
def upsert_candidate(db: Database, parsed_data: Dict) -> str:
    import uuid
    emails = parsed_data.get("emails") or []
    if isinstance(emails, str):
        emails = [emails]
    parsed_data["emails"] = emails
    if not parsed_data.get("cand_id"):
        parsed_data["cand_id"] = str(uuid.uuid4())

    coll = db["candidates"]
    existing = coll.find_one({"emails": {"$in": emails}}) if emails else None
    if existing:
        print(f"[MongoDB] Candidate với email {emails} đã tồn tại, cập nhật thông tin.")
        coll.update_one({"_id": existing["_id"]}, {"$set": parsed_data})
        return existing.get("cand_id", parsed_data["cand_id"])
    print(f"[MongoDB] Thêm ứng viên mới với email {emails} vào collection candidates.")
    coll.insert_one(parsed_data)
    return parsed_data["cand_id"]

# ---------- POST /candidates/upload ----------
@router.post("/upload", response_model=UploadResponse)
async def upload_cv(
    file: UploadFile = File(...),
    db: Database = Depends(get_database),
    sbert_model: Optional[SentenceTransformer] = Depends(get_sbert),
    bart_summarizer: Optional[BartSummarizer] = Depends(get_summarizer),
):
    try:
        # 0) Content-type whitelist (nới lỏng 1 số loại thường gặp)
        allowed = {
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword",       # .doc cũ (sẽ báo 400 ở extract_text_from_file)
            "text/plain",
            "application/octet-stream", # nhiều FE gửi kiểu này
        }
        logger.info(f"[UPLOAD] Step 0: file={file.filename}, content_type={file.content_type}")
        if file.content_type not in allowed:
            n = (file.filename or "").lower()
            logger.warning(f"[UPLOAD] Step 0: Unsupported file type: {file.content_type}, filename={file.filename}")
            if not (n.endswith(".pdf") or n.endswith(".docx") or n.endswith(".txt") or n.endswith(".doc")):
                raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

        # 1) Read file
        content = await file.read()
        logger.info(f"[UPLOAD] Step 1: Read file, size={len(content) if content else 0}")
        if not content:
            logger.warning(f"[UPLOAD] Step 1: Empty file.")
            raise HTTPException(status_code=400, detail="Empty file.")
        if len(content) > 10 * 1024 * 1024:
            logger.warning(f"[UPLOAD] Step 1: File too large: {len(content)} bytes")
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")

        logger.info("[UPLOAD] Step 1: filename=%s content_type=%s size=%d", file.filename, file.content_type, len(content))

        # 2) Extract text (bọc lỗi để trả 400 thay vì 500)
        try:
            logger.info(f"[UPLOAD] Step 2: Extracting text from file {file.filename}")
            cv_text = extract_text_from_file(file.filename, content)
            logger.info(f"[UPLOAD] Step 2: Extracted text length={len(cv_text) if cv_text else 0}")
        except HTTPException:
            logger.error(f"[UPLOAD] Step 2: HTTPException during extract_text_from_file")
            raise
        except Exception as e:
            logger.error("[UPLOAD] Step 2: FILE_PARSE_ERROR: %s\n%s", e, traceback.format_exc())
            raise HTTPException(status_code=400, detail=f"FILE_PARSE_ERROR: {type(e).__name__}: {e}")

        if not cv_text or len(cv_text.strip()) < 50:
            logger.warning(f"[UPLOAD] Step 2: CV text too short or empty. Length={len(cv_text) if cv_text else 0}")
            raise HTTPException(status_code=400, detail="CV text is too short or empty. Please upload a valid CV.")

        # 3) Summarize (best-effort)
        logger.info(f"[UPLOAD] Step 3: Summarizing CV text")
        resume_summary = safe_summarize(bart_summarizer, cv_text)
        logger.info(f"[UPLOAD] Step 3: Summary length={len(resume_summary) if resume_summary else 0}")

        # 4) Parse CV (bọc riêng để khỏi rơi 500)
        filename_wo = os.path.splitext(file.filename)[0] if file.filename else "unknown"
        try:
            logger.info(f"[UPLOAD] Step 4: Parsing CV file")
            parsed_data = parse_cv_file(cv_text, filename_wo) or {}
            logger.info(f"[UPLOAD] Step 4: Parsed data keys={list(parsed_data.keys())}")
        except Exception as e:
            logger.error("[UPLOAD] Step 4: CV_PARSE_ERROR: %s\n%s", e, traceback.format_exc())
            raise HTTPException(status_code=400, detail=f"CV_PARSE_ERROR: {type(e).__name__}: {e}")

        # Guard fields tránh ValidationError
        parsed_data.setdefault("name", "")
        parsed_data.setdefault("emails", [])
        parsed_data.setdefault("phones", [])
        parsed_data.setdefault("locations", [])
        parsed_data.setdefault("skills_norm", [])
        parsed_data.setdefault("exp_years", 0)
        parsed_data.setdefault("experience_entries", [])
        parsed_data.setdefault("education_entries", [])
        parsed_data["resume_summary"] = resume_summary
        parsed_data["resume_text"] = parsed_data.get("resume_text") or cv_text

        # 5) Embedding
        emb_src = resume_summary if resume_summary else parsed_data["resume_text"]
        logger.info(f"[UPLOAD] Step 5: Encoding embedding")
        parsed_data["resume_embedding"] = safe_encode(sbert_model, emb_src)
        logger.info(f"[UPLOAD] Step 5: Embedding type={type(parsed_data['resume_embedding'])}")

        # 6) Upsert
        logger.info(f"[UPLOAD] Step 6: Upserting candidate")
        cand_id = upsert_candidate(db, parsed_data)
        logger.info(f"[UPLOAD] Step 6: Upserted cand_id={cand_id}")

        # 7) Response
        candidate_info = CandidateInfo(
            cand_id=cand_id,
            name=parsed_data.get("name", ""),
            emails=parsed_data.get("emails", []),
            phones=parsed_data.get("phones", []),
            locations=parsed_data.get("locations", []),
            skills_norm=parsed_data.get("skills_norm", []),
            exp_years=float(parsed_data.get("exp_years") or 0),
            experience_entries=[str(x) for x in parsed_data.get("experience_entries", [])],
            education_entries=[str(x) for x in parsed_data.get("education_entries", [])],
        )
        logger.info(f"[UPLOAD] Step 7: Returning response for cand_id={cand_id}")
        return UploadResponse(
            success=True,
            message="CV uploaded and parsed successfully",
            candidate=candidate_info
        )

    except HTTPException as he:
        logger.error(f"[UPLOAD] HTTPException: {he.detail}")
        raise
    except Exception as e:
        logger.error("[UPLOAD] UPLOAD_FAILURE: %s\n%s", e, traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"UPLOAD_FAILURE: {type(e).__name__}: {e}"
        )

# ---------- POST /candidates/upload-and-match ----------
@router.post("/upload-and-match")
async def upload_and_match(
    top_k: int = 10,
    file: UploadFile = File(...),
    db: Database = Depends(get_database),
    sbert_model: Optional[SentenceTransformer] = Depends(get_sbert),
    bart_summarizer: Optional[BartSummarizer] = Depends(get_summarizer),
    ranker = Depends(get_ranker),
):
    from fastapi.responses import JSONResponse
    try:
        upload_resp = await upload_cv(file=file, db=db, sbert_model=sbert_model, bart_summarizer=bart_summarizer)
        cand_id = upload_resp.candidate.cand_id
    except HTTPException as he:
        raise he

    try:
        matches = ranker.search_jobs_for_candidate(cand_id=cand_id, keyword=None, top_k=top_k)
        matches = [m if isinstance(m, dict) else m.dict() for m in matches]
        return {"upload": upload_resp.dict(), "matches": matches}
    except Exception as e:
        logger.error("MATCH_FAILURE: %s\n%s", e, traceback.format_exc())
        return JSONResponse(
            status_code=207,
            content={"upload": upload_resp.dict(), "matching_error": f"MATCH_FAILURE: {type(e).__name__}: {e}"}
        )

# ---------- GET /candidates/{cand_id}/summary ----------
@router.get("/{cand_id}/summary")
def get_candidate_summary(cand_id: str, db: Database = Depends(get_database)):
    doc = db["candidates"].find_one({"cand_id": cand_id}, {"_id": 0, "cand_id": 1, "resume_summary": 1})
    if not doc:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return doc

# ---------- GET /candidates/{cand_id}/matches ----------
@router.get("/{cand_id}/matches", response_model=List[JobSearchResponseItem])
def get_candidate_matches(
    cand_id: str,
    top_k: int = 10,
    keyword: Optional[str] = None,
    ranker = Depends(get_ranker),
):
    return ranker.search_jobs_for_candidate(cand_id=cand_id, keyword=keyword, top_k=top_k)
