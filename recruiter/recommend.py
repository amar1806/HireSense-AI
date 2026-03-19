def recommend_skills(gaps):

    recommendations = []

    for skill in gaps:

        if skill == "python":
            recommendations.append("Add Python based projects")

        elif skill == "machine learning":
            recommendations.append("Build ML models using Scikit-learn")

        elif skill == "sql":
            recommendations.append("Include database experience")

        elif skill == "django":
            recommendations.append("Develop web apps using Django")

        else:
            recommendations.append("Gain experience in " + skill)

    return recommendations