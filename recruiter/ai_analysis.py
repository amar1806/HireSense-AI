def analyze_resume_negatives(resume_text, job_desc):

    negatives = []

    text = resume_text.lower()
    jd = job_desc.lower()

    if len(resume_text.split()) < 200:
        negatives.append("Resume is too short. Add more details about projects and experience.")

    if "project" not in text:
        negatives.append("Projects section missing. Add at least 2 technical projects.")

    if "experience" not in text:
        negatives.append("No experience section found.")

    if "github" not in text:
        negatives.append("GitHub portfolio link missing.")

    if "python" in jd and "python" not in text:
        negatives.append("Python skill required for this role but missing in resume.")

    if "machine learning" in jd and "machine learning" not in text:
        negatives.append("Machine learning experience missing.")

    return negatives