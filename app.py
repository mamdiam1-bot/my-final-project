import os
import requests
import base64
import logging
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from cs50 import SQL

logging.getLogger("urllib3").setLevel(logging.WARNING)

load_dotenv(override=True)
app = Flask(__name__)

connection_string = "postgresql://postgres.yimsexytrswzamnslgcd:MaAm%40036355972@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres?sslmode=require"
db = SQL(connection_string)

API_KEY = os.getenv("GOOGLE_API_KEY")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    # פתרון לשגיאת ה-415: מאלץ קריאת JSON גם אם ה-Header חסר
    try:
        data = request.get_json(force=True, silent=True)
        if not data or "message" not in data:
            return jsonify({"reply": "לא התקבלה הודעה תקינה בצד השרת."})
        user_message = data["message"]
    except Exception as e:
        return jsonify({"reply": f"שגיאה בעיבוד הבקשה: {str(e)}"})

    API_KEY = os.getenv("GOOGLE_API_KEY")
    # ה-URL המדויק שעובד ב-Render (גרסת בטא עם מודל יציב)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{
                "text": f"אתה מורה מומחה לגיאוגרפיה והיסטוריה. ענה על השאלה הבאה: {user_message}"
            }]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()
        
        if response.status_code == 200:
            if 'candidates' in response_data and response_data['candidates']:
                reply = response_data['candidates'][0]['content']['parts'][0]['text']
                return jsonify({"reply": reply})
            else:
                return jsonify({"reply": "גוגל החזירה תשובה ריקה."})
        else:
            # הדפסה ללוג למקרה של תקלה ב-API
            print(f"Google API Error: {response_data}")
            return jsonify({"reply": "המודל לא הגיב לבקשה."})
            
    except Exception as e:
        return jsonify({"reply": f"שגיאת תקשורת: {str(e)}"})
@app.route("/history")
def history():
    chats = db.execute("SELECT * FROM chats ORDER BY id DESC")
    return render_template("history.html", chats=chats)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
