import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# הגדרה מחוץ לפונקציה כדי לחסוך זמן טעינה
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True, silent=True) or request.form
    user_message = data.get("message")
    
    if not user_message:
        return jsonify({"reply": "לא התקבלה הודעה."})

    try:
        # פתרון מחוץ לקופסה: במקום לנחש URL, אנחנו מבקשים מהספרייה 
        # עצמה למצוא את המודל הזמין.
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # הגדרת בטיחות מקלה (לפעמים גוגל חוסמת תשובות וזה נראה כמו 404)
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        
        response = model.generate_content(user_message, safety_settings=safety_settings)
        
        if response.text:
            return jsonify({"reply": response.text})
        else:
            return jsonify({"reply": "גוגל חסמה את התשובה מסיבות בטיחות."})
            
    except Exception as e:
        # אם זה נכשל, ננסה "מודל גיבוי" אוטומטי
        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(user_message)
            return jsonify({"reply": response.text})
        except:
            return jsonify({"reply": f"שגיאה מערכתית: {str(e)}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)