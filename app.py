import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# הגדרת המפתח
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

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
        # פנייה למודל הכי חדש בגרסת ייצור (Production)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(user_message)
        
        if response.text:
            return jsonify({"reply": response.text})
        return jsonify({"reply": "גוגל לא החזירה תשובה טקסטואלית."})
            
    except Exception as e:
        return jsonify({"reply": f"שגיאה: {str(e)}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)