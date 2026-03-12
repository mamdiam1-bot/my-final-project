import os
import requests
import base64
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from cs50 import SQL

load_dotenv(override=True)
app = Flask(__name__)

connection_string = "postgresql://postgres:MaAm%40036355972@db.yimsexytrswzamnslgcd.supabase.co:6543/postgres?sslmode=disable"
db = SQL(connection_string)

API_KEY = os.getenv("GOOGLE_API_KEY")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.form.get("message", "")
    image_file = request.files.get("image")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={API_KEY}"
    parts = [{"text": f"ענה כמורה לגיאוגרפיה והיסטוריה בעברית. אל תשלח פקודות חיצוניות, רק טקסט: {user_input}"}]

    if image_file:
        try:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
            parts.append({
                "inline_data": {
                    "mime_type": image_file.content_type,
                    "data": image_data
                }
            })
        except Exception as e:
            print(f"DEBUG: טעות בעיבוד התמונה: {e}")

    payload = {"contents": [{"parts": parts}]}
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()

        if response.status_code == 200:
            reply = response_data['candidates'][0]['content']['parts'][0]['text']

            db("INSERT INTO chats (user_msg, bot_res, lang) VALUES (:u, :r, :l)",
               u=user_input, r=reply, l="Hebrew")

            return jsonify({"reply": reply})
        else:
            print(f"Google API Error: {response.text}")
            return jsonify({"reply": "שגיאה (404/403): המודל לא הגיב."})

    except Exception as e:
        return jsonify({"reply": f"שגיאת תקשורת: {str(e)}"})

@app.route("/history")
def history():
    chats = db("SELECT * FROM chats ORDER BY id DESC")
    return render_template("history.html", chats=chats)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
