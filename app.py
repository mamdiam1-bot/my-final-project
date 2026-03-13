import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    # קבלת הודעה בצורה הכי בטוחה
    data = request.get_json(force=True, silent=True) or request.form
    user_message = data.get("message") or data.get("text") or data.get("msg")
    
    if not user_message:
        return jsonify({"reply": "לא התקבלה הודעה תקינה."})

    API_KEY = os.getenv("GOOGLE_API_KEY")
    # הכתובת הסטנדרטית ביותר - v1beta עם gemini-1.5-flash
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": user_message}]}]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        res_json = response.json()
        
        if response.status_code == 200:
            reply = res_json['candidates'][0]['content']['parts'][0]['text']
            return jsonify({"reply": reply})
        else:
            # הדפסת השגיאה המדויקת מגוגל ללוג של Render
            print(f"GOOGLE ERROR: {res_json}")
            return jsonify({"reply": f"שגיאת מודל: {res_json.get('error', {}).get('message', 'תקלה כללית')}"})
    except Exception as e:
        return jsonify({"reply": f"שגיאת שרת: {str(e)}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)