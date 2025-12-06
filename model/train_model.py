
import pandas as pd
from sklearn.linear_model import LogisticRegression
import joblib

df = pd.read_csv("data/telco_churn.csv")
X = df.drop("churn", axis=1)
y = df["churn"]

model = LogisticRegression()
model.fit(X, y)

joblib.dump(model, "model/churn_model.pkl")
print("Model trained successfully!")
