import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# הגדרת המפתח
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True, silent=True) or request.form
    user_message = data.get("message") or data.get("text") or data.get("msg")
    
    if not user_message:
        return jsonify({"reply": "לא התקבלה הודעה."})

    # רשימת מודלים לניסוי - גוגל משנה שמות לפעמים
    models_to_try = ['gemini-1.5-flash', 'models/gemini-1.5-flash', 'gemini-pro']
    
    last_error = ""
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(user_message)
            return jsonify({"reply": response.text})
        except Exception as e:
            last_error = str(e)
            continue # מנסה את המודל הבא ברשימה

    # אם הגענו לכאן, כל הניסיונות נכשלו
    print(f"ALL MODELS FAILED. Last error: {last_error}")
    return jsonify({"reply": f"שגיאת תקשורת סופית: {last_error}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)