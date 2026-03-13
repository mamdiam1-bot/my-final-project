import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# הגדרת ה-API בצורה פשוטה וישירה
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    # קבלת הנתונים בצורה בטוחה
    data = request.get_json(force=True, silent=True) or request.form
    user_message = data.get("message") or data.get("text") or data.get("msg")
    
    if not user_message:
        return jsonify({"reply": "לא התקבלה הודעה תקינה בשרת."})

    try:
        # שימוש במודל הפלאש 1.5
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(user_message)
        
        if response and response.text:
            return jsonify({"reply": response.text})
        else:
            return jsonify({"reply": "גוגל החזירה תשובה ריקה. וודא שהמפתח תקין."})
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return jsonify({"reply": f"שגיאת תקשורת: {str(e)}"})

if __name__ == "__main__":
    # הגדרת פורט שמתאימה ל-Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)