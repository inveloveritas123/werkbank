"""GP06 — Mini-RAG über interne Dokumente mit PII-Filter (stdlib-only, kein LLM).

Deterministisches Keyword-Retrieval. Die Antwort ist ein WÖRTLICHER Satz aus dem belegten
Dokument (keine Generierung -> keine Halluzination); ohne passende Quelle wird die Antwort
verweigert. Vor der Ausgabe werden PII maskiert (keine unnötige PII-Ausgabe).
"""
import re
from dataclasses import dataclass
from typing import Optional

import pii_filter

STOPWORDS = {
    "der", "die", "das", "den", "dem", "ein", "eine", "einen", "einem", "einer",
    "ist", "sind", "war", "wird", "werden", "hat", "haben", "und", "oder", "aber",
    "wie", "was", "wer", "wo", "wann", "warum", "welche", "welcher", "welches",
    "fuer", "für", "von", "mit", "auf", "aus", "bei", "zum", "zur", "ueber", "über",
    "im", "in", "an", "ab", "zu", "es", "sie", "er", "ich", "wir", "ihr", "man",
    "lange", "viel", "viele", "diese", "dieser", "dieses", "kann", "soll",
}


def _tokens(text):
    return {t for t in re.findall(r"[A-Za-zÄÖÜäöüß]{4,}", text.lower()) if t not in STOPWORDS}


def _sentences(text):
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p.strip()]


@dataclass
class Answer:
    text: str
    source: Optional[str]
    grounded: bool


class RagIndex:
    def __init__(self):
        self._docs = {}   # id -> {"text","source","tokens"}

    def add(self, doc_id, text, source):
        self._docs[doc_id] = {"text": text, "source": source, "tokens": _tokens(text)}

    def delete(self, doc_id):
        return self._docs.pop(doc_id, None) is not None

    def _retrieve(self, question):
        q = _tokens(question)
        if not q:
            return None
        best, best_score = None, 0
        for doc_id, d in self._docs.items():
            score = len(q & d["tokens"])
            if score > best_score:
                best, best_score = d, score
        # Anti-Halluzination: nicht nur 1 zufälliges gemeinsames Wort — mind. die Hälfte der
        # Fragebegriffe müssen belegt sein, sonst keine belegte Antwort.
        if best_score >= 1 and best_score / len(q) >= 0.5:
            return best
        return None

    def answer(self, question):
        doc = self._retrieve(question)
        if doc is None:
            return Answer("Keine belegte Antwort im Index gefunden.", None, False)
        q = _tokens(question)
        # belegter Satz mit der höchsten Überlappung — wörtlich, nicht generiert
        best_sentence = max(_sentences(doc["text"]),
                            key=lambda s: len(q & _tokens(s)), default=doc["text"])
        # PII auch in der Quellenangabe maskieren
        return Answer(pii_filter.redact(best_sentence), pii_filter.redact(doc["source"]), True)
