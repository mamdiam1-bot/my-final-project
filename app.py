import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# הגדרת המפתח והכתובת היציבה (v1)
API_KEY = os.getenv("GOOGLE_API_KEY")
# שים לב לשימוש ב-v1 במקום v1beta
API_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True, silent=True) or request.form
    user_message = data.get("message") or data.get("text") or data.get("msg")
    
    if not user_message:
        return jsonify({"reply": "לא התקבלה הודעה."})

    payload = {
        "contents": [{"parts": [{"text": user_message}]}]
    }

    try:
        # שליחת בקשה ישירה לגוגל
        response = requests.post(API_URL, json=payload)
        result = response.json()
        
        # חילוץ התשובה
        if "candidates" in result:
            bot_reply = result["candidates"][0]["content"]["parts"][0]["text"]
            return jsonify({"reply": bot_reply})
        else:
            error_info = result.get("error", {}).get("message", "שגיאה פנימית בגוגל")
            return jsonify({"reply": f"שגיאת מודל: {error_info}"})
            
    except Exception as e:
        return jsonify({"reply": f"תקלה בתקשורת: {str(e)}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)