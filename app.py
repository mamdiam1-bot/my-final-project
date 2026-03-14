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
    user_message = data.get("message")
    
    if not user_message:
        return jsonify({"reply": "לא התקבלה הודעה."})

    api_key = os.getenv("GOOGLE_API_KEY")
    
    # כתובת v1 יציבה ללא beta - הפורמט המדויק
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": user_message}]}]
    }

    try:
        response = requests.post(url, json=payload)
        result = response.json()
        
        if "candidates" in result:
            bot_reply = result["candidates"][0]["content"]["parts"][0]["text"]
            return jsonify({"reply": bot_reply})
        else:
            error_msg = result.get("error", {}).get("message", "API Error")
            return jsonify({"reply": f"שגיאת גוגל: {error_msg}"})
    except Exception as e:
        return jsonify({"reply": f"תקלה: {str(e)}"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))