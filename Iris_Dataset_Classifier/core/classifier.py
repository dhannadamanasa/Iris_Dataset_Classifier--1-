from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
import numpy as np

FEATURES = ["sepal_length", "sepal_width", "petal_length", "petal_width"]
DISPLAY_FEATURES = ["Sepal length", "Sepal width", "Petal length", "Petal width"]

class IrisClassifier:
    def __init__(self):
        dataset = load_iris()
        self.feature_names = FEATURES
        self.species = [str(x).title() for x in dataset.target_names]
        self.X = dataset.data
        self.y = dataset.target
        self.model = RandomForestClassifier(n_estimators=180, random_state=42, class_weight="balanced")
        self.model.fit(self.X, self.y)
        self.accuracy = float(cross_val_score(
            RandomForestClassifier(n_estimators=120, random_state=42),
            self.X, self.y, cv=5
        ).mean())
        self.ranges = {
            name: (float(self.X[:, i].min()), float(self.X[:, i].max()))
            for i, name in enumerate(FEATURES)
        }

    def predict(self, values):
        arr = np.array([values], dtype=float)
        prediction = int(self.model.predict(arr)[0])
        probabilities = self.model.predict_proba(arr)[0]
        return {
            "species": self.species[prediction],
            "confidence": float(probabilities[prediction]),
            "probabilities": {self.species[i]: float(p) for i, p in enumerate(probabilities)}
        }
