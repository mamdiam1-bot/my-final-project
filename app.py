import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# הגדרת המפתח
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    # קבלת המידע בצורה גמישה (JSON או Form)
    data = request.get_json(silent=True) or request.form
    user_message = data.get("message") or data.get("text")
    
    if not user_message:
        return jsonify({"reply": "לא קיבלתי הודעה מהצ'אט."})

    try:
        # שימוש בספרייה הרשמית - היא כבר תדע לבד לאיזה URL לפנות
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(user_message)
        
        return jsonify({"reply": response.text})
        
    except Exception as e:
        return jsonify({"reply": f"שגיאה של המורה: {str(e)}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)