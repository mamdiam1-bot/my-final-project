import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# שליפת המפתח מהגדרות השרת (Environment Variables) - אבטחה מקסימלית
API_KEY = os.environ.get("GEMINI_API_KEY")

# שימוש בכתובת של מודל 1.5 Flash - יציב יותר עם מכסות רחבות
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    # קבלת ההודעה מהלקוח (JavaScript)
    data = request.json
    if not data or 'message' not in data:
        return jsonify({'reply': 'הודעה ריקה.'}), 400
        
    user_message = data.get('message')
    
    # בדיקה שהמפתח הוגדר ב-Render
    if not API_KEY:
        return jsonify({'reply': 'שגיאת מערכת: מפתח ה-API לא הוגדר בשרת.'}), 500

    # בניית ה-Payload לפי הפורמט של גוגל
    payload = {
        "contents": [{"parts": [{"text": user_message}]}]
    }
    
    try:
        # שליחת הבקשה עם המפתח כפרמטר ב-URL
        response = requests.post(f"{API_URL}?key={API_KEY}", json=payload, timeout=30)
        
        # טיפול ספציפי בחריגה מהמכסה (Error 429)
        if response.status_code == 429:
            return jsonify({'reply': 'הגענו למכסת ההודעות החינמית של גוגל. אנא נסו שוב בעוד דקה.'}), 429
            
        # זריקת שגיאה במידה והסטטוס אינו 200
        response.raise_for_status()
        
        # חילוץ התשובה מה-JSON
        result = response.json()
        bot_reply = result['candidates'][0]['content']['parts'][0]['text']
        
        return jsonify({'reply': bot_reply})

    except requests.exceptions.RequestException as e:
        print(f"API Connection Error: {e}")
        return jsonify({'reply': 'חלה שגיאה בתקשורת עם שרתי המודל.'}), 500
    except (KeyError, IndexError, TypeError) as e:
        print(f"Parsing Error: {e}")
        return jsonify({'reply': 'התקבלה תשובה לא תקינה מהשרת.'}), 500

if __name__ == '__main__':
    # התאמה לפורט של Render (חשוב מאוד להרצה בענן)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)