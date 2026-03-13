import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# הגדרות ה-API
API_KEY = os.getenv("GOOGLE_API_KEY")
# שימוש בגרסת v1 היציבה ולא ב-v1beta
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
        response = requests.post(API_URL, json=payload)
        result = response.json()
        
        # חילוץ התשובה מהמבנה של גוגל
        if "candidates" in result:
            bot_reply = result["candidates"][0]["content"]["parts"][0]["text"]
            return jsonify({"reply": bot_reply})
        else:
            error_msg = result.get("error", {}).get("message", "שגיאה לא ידועה")
            return jsonify({"reply": f"גוגל החזירה שגיאה: {error_msg}"})
            
    except Exception as e:
        return jsonify({"reply": f"תקלה בתקשורת: {str(e)}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)