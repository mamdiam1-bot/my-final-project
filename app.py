import os
import requests
import base64
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# שליפת המפתח מהגדרות השרת (Environment Variables) - אבטחה מקסימלית
API_KEY = os.environ.get("GEMINI_API_KEY")

# שימוש בכתובת של מודל 1.5 Flash - תומך בטקסט ותמונות
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    # בדיקה שהמפתח הוגדר ב-Render
    if not API_KEY:
        return jsonify({'reply': 'שגיאת מערכת: מפתח ה-API לא הוגדר בשרת.'}), 500

    # קבלת המידע כ-Form Data (תמיכה בקבצים וטקסט)
    user_message = request.form.get('message', '')
    image_file = request.files.get('image')

    # בדיקה שיש לפחות תוכן אחד
    if not user_message and not image_file:
        return jsonify({'reply': 'אנא הקלד הודעה או צלם תמונה.'}), 400

    # בניית ה-Payload (התוכן) לשליחה לגוגל
    contents = []
    parts = []

    # הוצאת קובץ התמונה
    if image_file:
        try:
            image_data = image_file.read()
            # המרת התמונה ל-Base64 כדי לשלוח אותה ב-JSON
            encoded_image = base64.b64encode(image_data).decode('utf-8')
            parts.append({
                "inline_data": {
                    "mime_type": image_file.content_type,
                    "data": encoded_image
                }
            })
        except Exception as e:
            print(f"Error processing image: {e}")
            return jsonify({'reply': 'חלה שגיאה בעיבוד התמונה.'}), 500

    # הוספת הטקסט
    parts.append({"text": user_message})

    # הרכבת ה-Payload הסופי
    contents.append({"parts": parts})
    payload = {"contents": contents}

    try:
        # שליחת הבקשה עם המפתח כפרמטר ב-URL
        response = requests.post(f"{API_URL}?key={API_KEY}", json=payload, timeout=60)
        
        # טיפול ספציפי בחריגה מהמכסה (Error 429)
        if response.status_code == 429:
            return jsonify({'reply': 'הגענו למכסת ההודעות החינמית של גוגל. אנא נסו שוב בעוד דקה.'}), 429
            
        # זריקת שגיאה במידה והסטטוס אינו 200
        response.raise_for_status()
        
        # חילוץ התשובה מה-JSON
        result = response.json()
        
        # וידוי שיש לנו תשובה תקינה
        if 'candidates' in result and result['candidates'][0]['content']['parts'][0]['text']:
            bot_reply = result['candidates'][0]['content']['parts'][0]['text']
            return jsonify({'reply': bot_reply})
        else:
            return jsonify({'reply': 'התקבלה תשובה ריקה מהמודל.'}), 500

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