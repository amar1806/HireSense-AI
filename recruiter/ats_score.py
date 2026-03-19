def calculate_ats_score(resume_text, job_desc, skills):

    score = 0

    jd_words = job_desc.lower().split()
    resume_words = resume_text.lower().split()

    keyword_match = len(set(jd_words) & set(resume_words))

    score += min(keyword_match * 4,40)

    score += min(len(skills) * 6,30)

    if len(resume_words) > 300:
        score += 20
    else:
        score += 10

    if "project" in resume_text.lower():
        score += 5

    if "experience" in resume_text.lower():
        score += 5

    return min(score,100)