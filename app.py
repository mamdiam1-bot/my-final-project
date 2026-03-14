import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "")
        api_key = os.environ.get("GOOGLE_API_KEY")
        
        # כתובת ישירה ל-Gemini 1.5 Flash
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        payload = {
            "contents": [{"parts": [{"text": user_message}]}]
        }
        
        response = requests.post(url, json=payload)
        response_data = response.json()
        
        if "candidates" in response_data:
            return jsonify({"reply": response_data["candidates"][0]["content"]["parts"][0]["text"]})
        else:
            return jsonify({"reply": "שגיאת API: " + str(response_data)})
            
    except Exception as e:
        return jsonify({"reply": "שגיאת קוד: " + str(e)})

if __name__ == "__main__":
    # זה החלק שגורם ל-Render לעלות או לקרוס
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)