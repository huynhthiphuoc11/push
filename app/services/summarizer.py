from __future__ import annotations
import re
from typing import List, Optional

try:
    from transformers import pipeline
except Exception:
    pipeline = None

def _split_words(txt: str, max_words: int = 350) -> List[str]:
    w = (txt or "").split()
    if not w: return []
    return [" ".join(w[i:i+max_words]) for i in range(0, len(w), max_words)]

class BartSummarizer:
    """
    Tóm tắt bằng BART (nếu transformers khả dụng). Nếu không, raise để caller fallback.
    """
    def __init__(
        self,
        model_id: str = "facebook/bart-base",
        min_len: int = 60,
        max_len: int = 220,
        chunk_words: int = 350,
        second_pass: bool = True,
    ):
        if pipeline is None:
            raise RuntimeError("transformers not available")
        self.min_len = min_len
        self.max_len = max_len
        self.chunk_words = chunk_words
        self.second_pass = second_pass
        self.pipe = pipeline("summarization", model=model_id, device_map="auto")

    def summarize(self, text: str) -> str:
        text = (text or "").strip()
        if not text:
            return ""
        if len(text.split()) <= self.chunk_words:
            out = self.pipe(text, min_length=self.min_len, max_length=self.max_len, truncation=True)[0]["summary_text"]
            return out.strip()

        parts = _split_words(text, self.chunk_words)
        partial = []
        for p in parts[:8]:
            s = self.pipe(p, min_length=self.min_len, max_length=self.max_len, truncation=True)[0]["summary_text"]
            partial.append(s.strip())

        merged = " ".join(partial)
        if self.second_pass and len(merged.split()) > self.chunk_words:
            merged = self.pipe(merged, min_length=self.min_len, max_length=self.max_len, truncation=True)[0]["summary_text"]

        merged = re.sub(r"\s+", " ", merged).strip()
        return merged
