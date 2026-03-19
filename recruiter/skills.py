skills_db = [
"python","java","machine learning","deep learning",
"sql","django","html","css","javascript",
"data science","react"
]

def extract_skills(text):

    found = []

    text = text.lower()

    for skill in skills_db:
        if skill in text:
            found.append(skill)

    return found