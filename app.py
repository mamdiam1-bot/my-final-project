import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True, silent=True) or request.form
    user_message = data.get("message") or data.get("text") or data.get("msg")
    
    if not user_message:
        return jsonify({"reply": "לא התקבלה הודעה תקינה."})

    API_KEY = os.getenv("GOOGLE_API_KEY")
    # ה-URL שעובד הכי טוב בשרתי ענן
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": user_message}]}]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        res_json = response.json()
        
        if response.status_code == 200:
            reply = res_json['candidates'][0]['content']['parts'][0]['text']
            return jsonify({"reply": reply})
        else:
            return jsonify({"reply": f"שגיאת מודל: {res_json.get('error', {}).get('message', 'תקלה כללית')}"})
    except Exception as e:
        return jsonify({"reply": f"שגיאת תקשורת: {str(e)}"})

if __name__ == "__main__":
    # התיקון הקריטי: Render מחייב שימוש במשתנה הסביבה PORT
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)