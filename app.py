import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# הגדרת ה-API בצורה הרשמית
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    # קבלת הודעה בצורה גמישה
    data = request.get_json(force=True, silent=True) or request.form
    user_message = data.get("message") or data.get("text") or data.get("msg")
    
    if not user_message:
        return jsonify({"reply": "לא התקבלה הודעה תקינה בצד השרת."})

    try:
        # יצירת המודל וייצור תשובה
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(user_message)
        
        if response and response.text:
            return jsonify({"reply": response.text})
        else:
            return jsonify({"reply": "גוגל החזירה תשובה ריקה."})
            
    except Exception as e:
        print(f"SYSTEM ERROR: {str(e)}")
        return jsonify({"reply": f"שגיאת מערכת גוגל: {str(e)}"})

if __name__ == "__main__":
    # הגדרת פורט קריטית עבור Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)