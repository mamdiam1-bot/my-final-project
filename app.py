import os
import requests
import base64
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# שליפת המפתח מהגדרות Render (הגדרנו שם GEMINI_API_KEY)
API_KEY = os.environ.get("GEMINI_API_KEY")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.form.get("message", "")
    image_file = request.files.get("image")

    if not API_KEY:
        return jsonify({"reply": "שגיאת מערכת: מפתח ה-API לא הוגדר בשרת."}), 500

    # הכתובת שעבדה לך ב-Studio (עם Gemini 1.5 Flash)
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"

    parts = [{"text": f"ענה כמורה לגיאוגרפיה והיסטוריה בעברית. {user_input}"}]

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
            return jsonify({"reply": reply})
        else:
            print(f"Google API Error: {response.text}")
            return jsonify({"reply": f"שגיאה {response.status_code}: המודל לא הגיב."})

    except Exception as e:
        return jsonify({"reply": f"שגיאת תקשורת: {str(e)}"})

if __name__ == "__main__":
    # Render דורש שהשרת יאזין לפורט שהם מגדירים
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)