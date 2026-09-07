import joblib
import pandas as pd
model=joblib.load('RF_tune_pipeline.pkl')
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
app=FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)
from pydantic import BaseModel,Field
from typing import Literal
class StudentInfo(BaseModel):
        Age:                        int=Field(...,ge=10,le=100)
        Gender:                     Literal['Male','Female']
        Country:                    Literal['Other', 'Canada', 'USA', 'India', 'Australia', 'UK', 'Germany']
        Academic_Level:             Literal['Undergraduate', 'Graduate', 'High School']
        Most_Used_Platform:         Literal['Facebook','LinkedIn','Instagram','Snapchat','Twitter', 'YouTube', 'TikTok', 'LINE','KakaoTalk', 'VKontakte', 'WhatsApp','WeChat']
        Purpose_Of_Use:             Literal['Networking' ,'Education' ,'Entertainment', 'News']
        Avg_Daily_Usage_Hours:      float=Field(...,ge=0,le=100)
        Daily_Unlocks:              int=Field(...,ge=0,le=1000)
        Study_Hours:                float=Field(...,ge=0,le=100)
        Physical_Activity_Hours:    float=Field(...,ge=0,le=100)
        Sleep_Hours_Per_Night:      float=Field(...,ge=0,le=100)
        Stress_Level:               Literal['Medium', 'Low' ,'Very High' ,'High']
class PredictionResponse(BaseModel):
     Mental_Health_Score:float
@app.get('/')
def greet():
    return 'Welcome to Girija Homepage.'
@app.post('/predict',response_model=PredictionResponse)
def predict(data:StudentInfo):
    input_DF=pd.DataFrame([{
            'Age':data.Age,
            'Gender':data.Gender,
            'Country':data.Country,
            'Academic_Level':data.Academic_Level,
            'Most_Used_Platform':data.Most_Used_Platform,
            'Purpose_Of_Use':data.Purpose_Of_Use,
            'Avg_Daily_Usage_Hours':data.Avg_Daily_Usage_Hours,
            'Daily_Unlocks':data.Daily_Unlocks,
            'Study_Hours':data.Study_Hours,
            'Physical_Activity_Hours':data.Physical_Activity_Hours,
            'Sleep_Hours_Per_Night':data.Sleep_Hours_Per_Night,
            'Stress_Level':data.Stress_Level 
            }])
    prediction=model.predict(input_DF)[0]
    return PredictionResponse(Mental_Health_Score=round(prediction,2))
      