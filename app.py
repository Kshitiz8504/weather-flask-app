import os
import logging
from datetime import datetime
from flask import Flask, render_template, request
import requests
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

OWM_API_KEY = os.getenv("OWM_API_KEY")
CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

def get_current_weather(city: str):
    params = {"q": city, "appid": OWM_API_KEY, "units": "metric"}
    try:
        r = requests.get(CURRENT_URL, params=params, timeout=6)
        if not r.ok:
            return None
        d = r.json()
        return {
            "name": d.get("name"),
            "country": d.get("sys", {}).get("country"),
            "temp": round(d.get("main", {}).get("temp")) if d.get("main") else None,
            "feels_like": round(d.get("main", {}).get("feels_like")) if d.get("main") else None,
            "min": round(d.get("main", {}).get("temp_min")) if d.get("main") else None,
            "max": round(d.get("main", {}).get("temp_max")) if d.get("main") else None,
            "description": d.get("weather", [{}])[0].get("description", "").title(),
            "icon": d.get("weather", [{}])[0].get("icon"),
            "humidity": d.get("main", {}).get("humidity"),
            "wind": d.get("wind", {}).get("speed"),
        }
    except requests.RequestException:
        return None

def get_forecast(city: str, days=5):
    params = {"q": city, "appid": OWM_API_KEY, "units": "metric"}
    try:
        r = requests.get(FORECAST_URL, params=params, timeout=6)
        if not r.ok:
            return None

        j = r.json()
        items = j.get("list", [])
        noon_items = [it for it in items if it.get("dt_txt", "").endswith("12:00:00")]

        forecast = []
        source = noon_items if noon_items else items

        if noon_items:
            take = noon_items[:days]
        else:
            take = [items[i] for i in range(0, min(len(items), days * 8), 8)]

        for item in take:
            dt = datetime.strptime(item["dt_txt"], "%Y-%m-%d %H:%M:%S")
            forecast.append({
                "date": dt.strftime("%a"),
                "temp": round(item["main"]["temp"]),
                "min": round(item["main"].get("temp_min")),
                "max": round(item["main"].get("temp_max")),
                "feels_like": round(item["main"].get("feels_like")),
                "humidity": item["main"].get("humidity"),
                "wind": item["wind"].get("speed") if item.get("wind") else None,
                "description": item["weather"][0]["description"].title(),
                "icon": item["weather"][0]["icon"],
            })

        return forecast
    except requests.RequestException:
        return None

def get_locations(city: str):
    GEOCODE_URL = "http://api.openweathermap.org/geo/1.0/direct"
    params = {"q": city, "limit": 5, "appid": OWM_API_KEY}
    try:
        r = requests.get(GEOCODE_URL, params=params, timeout=6)
        if not r.ok:
            return None
        locations = r.json()
        if locations:
            return locations
        return None
    except requests.RequestException:
        return None

def get_current_weather_by_coords(lat, lon):
    params = {"lat": lat, "lon": lon, "appid": OWM_API_KEY, "units": "metric"}
    try:
        r = requests.get(CURRENT_URL, params=params, timeout=6)
        if not r.ok:
            return None
        d = r.json()
        return {
            "name": d.get("name"),
            "country": d.get("sys", {}).get("country"),
            "temp": round(d.get("main", {}).get("temp")) if d.get("main") else None,
            "feels_like": round(d.get("main", {}).get("feels_like")) if d.get("main") else None,
            "min": round(d.get("main", {}).get("temp_min")) if d.get("main") else None,
            "max": round(d.get("main", {}).get("temp_max")) if d.get("main") else None,
            "description": d.get("weather", [{}])[0].get("description", "").title(),
            "icon": d.get("weather", [{}])[0].get("icon"),
            "humidity": d.get("main", {}).get("humidity"),
            "wind": d.get("wind", {}).get("speed"),
        }
    except requests.RequestException:
        return None

def get_forecast_by_coords(lat, lon, days=5):
    params = {"lat": lat, "lon": lon, "appid": OWM_API_KEY, "units": "metric"}
    try:
        r = requests.get(FORECAST_URL, params=params, timeout=6)
        if not r.ok:
            return None

        j = r.json()
        items = j.get("list", [])
        noon_items = [it for it in items if it.get("dt_txt", "").endswith("12:00:00")]

        forecast = []
        source = noon_items if noon_items else items

        if noon_items:
            take = noon_items[:days]
        else:
            take = [items[i] for i in range(0, min(len(items), days * 8), 8)]

        for item in take:
            dt = datetime.strptime(item["dt_txt"], "%Y-%m-%d %H:%M:%S")
            forecast.append({
                "date": dt.strftime("%a"),
                "temp": round(item["main"]["temp"]),
                "min": round(item["main"].get("temp_min")),
                "max": round(item["main"].get("temp_max")),
                "feels_like": round(item["main"].get("feels_like")),
                "humidity": item["main"].get("humidity"),
                "wind": item["wind"].get("speed") if item.get("wind") else None,
                "description": item["weather"][0]["description"].title(),
                "icon": item["weather"][0]["icon"],
            })

        return forecast
    except requests.RequestException:
        return None

@app.route("/", methods=["GET", "POST"])
def home():
    error = None
    current = None
    forecast = None
    locations = None

    if request.method == "POST":
        lat = request.form.get("lat")
        lon = request.form.get("lon")

        if lat and lon:
            current = get_current_weather_by_coords(lat, lon)
            forecast = get_forecast_by_coords(lat, lon)
        else:
            city = request.form.get("city", "").strip()
            if not city:
                error = "Please enter a city name."
            else:
                locations = get_locations(city)
                if not locations:
                    error = "No matching locations found."

    return render_template(
        "index.html",
        error=error,
        current=current,
        forecast=forecast,
        locations=locations
    )


if __name__ == "__main__":
    app.run(debug=True)