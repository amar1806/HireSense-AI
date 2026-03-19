import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

data = {
    "resume": [
        "python machine learning data science",
        "java spring backend developer",
        "html css javascript web developer",
        "deep learning python tensorflow",
        "accounting finance excel"
    ],
    "label":[1,0,0,1,0]
}

df = pd.DataFrame(data)

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df["resume"])
y = df["label"]

model = LogisticRegression()
model.fit(X,y)

pickle.dump(model,open("model.pkl","wb"))
pickle.dump(vectorizer,open("vectorizer.pkl","wb"))

print("Model trained successfully")