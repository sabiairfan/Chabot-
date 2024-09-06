from flask import Flask, render_template, request 

import openai 
import os 
from dotenv import load_dotenv 

load_dotenv()
openai.api_key = os.environ["OPEN_AI_KEY"]

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads/"

app.config["SECRET_KEY"] = "oauh"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chatbot", methods=["POST"])
def chatbot():
    user_input = request.form.get("message")
    
    file = request.files.get('file')

    file_content = ""

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
        except UnicodeDecodeError:
        # Fallback to 'latin-1' encoding if 'utf-8' fails
            with open(file_path, 'r', encoding='latin-1') as f:
                file_content = f.read()
    
    file_content = file_content[:3000]

    chat_history = []

    response = openai.ChatCompletion.create(  # <<< This line must be updated to:
        model="gpt-3.5-turbo",  
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_input},
            {"role": "system", "content": f"Here is some information from a file: {file_content}"},
        ],
        temperature=0.5,
        max_tokens=60,
        top_p=1,
        frequency_penalty=0,
        stop=["\nUser: ", "\nChatbot: "]
    )

    bot_response = response.choices[0].message['content'].strip()

    chat_history.append(f"User: {user_input}\nChatbot: {bot_response}")

    return render_template("chatbot.html", user_input=user_input, bot_response=bot_response)


if __name__ == '__main__':
    app.run(debug=True)