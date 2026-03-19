def skill_gap_analysis(job_desc, skills):

    job_skills = [
    "python","machine learning","sql",
    "django","react","data science"
    ]

    gaps = []

    jd = job_desc.lower()

    for skill in job_skills:

        if skill in jd and skill not in skills:
            gaps.append(skill)

    return gaps