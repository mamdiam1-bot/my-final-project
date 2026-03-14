import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    # פתרון מחוץ לקופסה: בודקים את כל האפשרויות שבהן המידע יכול להגיע
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    
    # מחפשים את ההודעה בכל מפתח אפשרי (message או text)
    user_message = data.get("message") or data.get("text") or data.get("msg")
    
    if not user_message:
        return jsonify({"reply": "לא התקבלה הודעה תקינה מהדפדפן."})

    api_key = os.environ.get("GOOGLE_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": user_message}]}]
    }

    try:
        response = requests.post(url, json=payload)
        response_data = response.json()
        
        if "candidates" in response_data:
            bot_reply = response_data["candidates"][0]["content"]["parts"][0]["text"]
            return jsonify({"reply": bot_reply})
        else:
            return jsonify({"reply": f"שגיאת גוגל: {response_data.get('error', {}).get('message', 'בעיה במפתח')}"})
            
    except Exception as e:
        return jsonify({"reply": f"שגיאה טכנית: {str(e)}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)