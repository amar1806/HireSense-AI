import re

# -------------------------------
# Extract keywords from job desc
# -------------------------------
def extract_keywords(job_desc):
    words = re.findall(r'\b\w+\b', job_desc.lower())

    # remove common words
    stopwords = ["the", "and", "is", "in", "to", "of", "for", "with", "on", "a"]

    keywords = [w for w in words if w not in stopwords and len(w) > 2]

    return list(set(keywords))


# -------------------------------
# Calculate ATS score
# -------------------------------
def calculate_ats_score(resume_text, job_desc):

    resume_text = resume_text.lower()
    keywords = extract_keywords(job_desc)

    match_count = 0

    for word in keywords:
        if word in resume_text:
            match_count += 1

    if len(keywords) == 0:
        return 50

    score = (match_count / len(keywords)) * 100

    return round(score)


# -------------------------------
# Match Score (skill similarity)
# -------------------------------
def calculate_match_score(resume_text, job_desc):

    resume_words = set(resume_text.lower().split())
    job_words = set(job_desc.lower().split())

    common = resume_words.intersection(job_words)

    if len(job_words) == 0:
        return 50

    score = (len(common) / len(job_words)) * 100

    return round(score)


# -------------------------------
# Missing Skills
# -------------------------------
def find_missing_skills(resume_text, job_desc):

    resume_words = set(resume_text.lower().split())
    job_words = set(job_desc.lower().split())

    missing = job_words - resume_words

    return list(missing)[:10]


# -------------------------------
# Suggestions generator
# -------------------------------
def generate_suggestions(resume_text):

    suggestions = []

    if "project" not in resume_text.lower():
        suggestions.append("Add project section")

    if "experience" not in resume_text.lower():
        suggestions.append("Add work experience")

    if "%" not in resume_text:
        suggestions.append("Add measurable achievements (e.g. improved performance by 30%)")

    if len(resume_text.split()) < 300:
        suggestions.append("Resume content is too short")

    return suggestions