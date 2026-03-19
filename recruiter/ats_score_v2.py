import re
from collections import Counter

# Small stopword list to reduce noise in keyword extraction.
STOPWORDS = {
    "a", "an", "and", "the", "to", "for", "in", "on", "with", "of",
    "is", "are", "was", "be", "by", "as", "at", "from", "that",
    "this", "it", "or", "will", "can", "have", "has", "had",
    "but", "about", "which", "you", "your", "our", "we", "they",
    "their", "them", "these", "those", "i", "me", "my", "so", "if"
}

SECTION_KEYWORDS = {
    "experience": ["experience", "worked", "employment", "professional"],
    "education": ["education", "degree", "bachelor", "master", "phd"],
    "projects": ["project", "projects", "built", "developed", "created"],
    "skills": ["skills", "technologies", "tools", "proficient"],
    "summary": ["summary", "profile", "overview", "objective"]
}


def _clean_text(text: str) -> str:
    """Normalize text by removing punctuation and lowercasing."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", re.sub(r"[^A-Za-z0-9 ]+", " ", text.lower())).strip()


def _tokenize(text: str):
    return [t for t in _clean_text(text).split() if t and t not in STOPWORDS]


def _top_keywords(tokens, n=30):
    if not tokens:
        return []
    counts = Counter(tokens)
    return [t for t, _ in counts.most_common(n)]


def calculate_ats_score(resume_text: str, job_desc: str, skills: list[str]) -> int:
    """Compute an ATS-style score (0-100) based on keyword similarity, skills, structure, and length."""

    resume_text = resume_text or ""
    job_desc = job_desc or ""

    # Keywords (40 pts)
    jd_tokens = _tokenize(job_desc)
    resume_tokens = _tokenize(resume_text)

    jd_keywords = set(_top_keywords(jd_tokens, n=40))
    keyword_score = 0
    if jd_keywords:
        matched = len(jd_keywords.intersection(resume_tokens))
        keyword_score = min(40, int(40 * (matched / len(jd_keywords))))

    # Skills (30 pts)
    resume_skills = set([s.lower() for s in (skills or [])])
    job_skills = set(_top_keywords(jd_tokens, n=20))

    matched_skills = len(resume_skills.intersection(job_skills))
    total_skills = max(1, len(job_skills))
    skill_score = min(30, int(30 * (matched_skills / total_skills)))

    # Structure / sections (20 pts)
    section_score = 0
    resume_lower = resume_text.lower()
    for keywords in SECTION_KEYWORDS.values():
        if any(k in resume_lower for k in keywords):
            section_score += 4

    # Length + relevance (10 pts)
    word_count = len(resume_tokens)
    length_score = 0
    if word_count >= 800:
        length_score = 10
    elif word_count >= 500:
        length_score = 8
    elif word_count >= 300:
        length_score = 6
    elif word_count >= 200:
        length_score = 3

    if "github" in resume_lower:
        length_score += 1
    if "linkedin" in resume_lower:
        length_score += 1

    final_score = keyword_score + skill_score + section_score + length_score
    return min(100, max(0, final_score))
