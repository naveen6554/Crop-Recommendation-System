import pandas as pd
from sklearn.ensemble import RandomForestClassifier


data = pd.read_csv("C:\\Users\\nk568\\OneDrive\\Desktop\\Project01\\Crop_recommendation\\Crop_recommendation.csv")


X = data.drop(columns=['label'])
y = data['label']


model = RandomForestClassifier()
model.fit(X, y)

def predict_crop(input_data):
    return model.predict([input_data])[0]