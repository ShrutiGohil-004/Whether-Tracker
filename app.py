from flask import Flask, render_template, request
import requests
import csv
from datetime import datetime

app = Flask(__name__)

BASE_URL = "https://wttr.in"


def get_weather(city):
    url = f"{BASE_URL}/{city}?format=j1"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None

        data = response.json()
        current = data["current_condition"][0]

        return {
            "city": city.capitalize(),
            "temp": current["temp_C"],
            "condition": current["weatherDesc"][0]["value"],
        }
    except:
        return None


def save_to_csv(data):
    filename = "weather_history.csv"
    file_exists = False

    try:
        with open(filename, "r"):
            file_exists = True
    except FileNotFoundError:
        pass

    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "City", "Temperature (°C)", "Condition"])

        writer.writerow(
            [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                data["city"],
                data["temp"],
                data["condition"],
            ]
        )


@app.route("/", methods=["GET", "POST"])
def index():
    weather = None
    error = None

    if request.method == "POST":
        city = request.form.get("city").strip()
        if not city:
            error = "Please enter a city name."
        else:
            weather = get_weather(city)
            if weather:
                save_to_csv(weather)
            else:
                error = "Could not fetch weather data."

    return render_template("index.html", weather=weather, error=error)


if __name__ == "__main__":
    app.run(debug=True)
