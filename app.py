import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    # קבלת ההודעה מהמשתמש
    data = request.get_json(force=True, silent=True) or request.form
    user_message = data.get("message") or data.get("text") or data.get("msg")
    
    if not user_message:
        return jsonify({"reply": "לא התקבלה הודעה."})

    # משיכת המפתח מהגדרות ה-Environment ב-Render
    api_key = os.getenv("GOOGLE_API_KEY")
    
    # השורה המעודכנת שביקשת (פנייה ישירה ל-v1)
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-Pro:generateContent?key={api_key}"
    
    # מבנה הנתונים שגוגל מצפה לקבל
    payload = {
        "contents": [
            {
                "parts": [{"text": user_message}]
            }
        ]
    }

    try:
        # שליחת הבקשה לגוגל
        response = requests.post(url, json=payload)
        result = response.json()
        
        # חילוץ התשובה מהמבנה של Gemini
        if "candidates" in result:
            bot_reply = result["candidates"][0]["content"]["parts"][0]["text"]
            return jsonify({"reply": bot_reply})
        else:
            # במקרה שגוגל מחזירה שגיאה (כמו מפתח לא תקין)
            error_message = result.get("error", {}).get("message", "שגיאה לא ידועה ב-API")
            return jsonify({"reply": f"שגיאת גוגל: {error_message}"})
            
    except Exception as e:
        return jsonify({"reply": f"תקלה בחיבור לשרת: {str(e)}"})

if __name__ == "__main__":
    # הגדרת הפורט עבור Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)