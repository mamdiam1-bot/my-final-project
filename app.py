import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# הגדרת ה-API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True, silent=True) or request.form
    user_message = data.get("message") or data.get("text") or data.get("msg")
    
    if not user_message:
        return jsonify({"reply": "לא התקבלה הודעה תקינה."})

    # ניסיון ראשון: הגרסה היציבה
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(user_message)
        return jsonify({"reply": response.text})
    except Exception as e:
        # ניסיון שני: אם הראשונה נכשלה, ננסה להגדיר מודל ספציפי יותר
        try:
            model = genai.GenerativeModel('models/gemini-1.5-flash')
            response = model.generate_content(user_message)
            return jsonify({"reply": response.text})
        except Exception as e2:
            print(f"SYSTEM ERROR: {str(e2)}")
            return jsonify({"reply": f"שגיאת מודל סופית: {str(e2)}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)