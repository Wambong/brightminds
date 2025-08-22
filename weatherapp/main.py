from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from routes.weather import router as WeatherRouter
from routes.weather_stats import router as WeatherStatsRouter


load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],   
    allow_headers=["*"],   
)



app.include_router(WeatherRouter)
app.include_router(WeatherStatsRouter)


@app.get("/")
def read_root():
    return {"Ohh": f"Nothing here..."}
