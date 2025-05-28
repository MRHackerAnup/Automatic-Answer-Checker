# 🧠 Automatic Answer Checker

This project is a Flask-based web application that allows teachers to create questions and automatically check answers using AI (OpenAI). It includes authentication, answer evaluation logic, and a user-friendly dashboard.

---

## 🖥️ VS Code Setup Guide

Follow these steps to set up and run the project in **VS Code**.

---

## 📦 Part 1: Initial Setup

### ✅ Requirements

- [Visual Studio Code](https://code.visualstudio.com/)
- [Python 3.8+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/) (optional)

### 🔌 Recommended VS Code Extensions

Install the following from the Extensions tab (`Ctrl+Shift+X`):

- Python (by Microsoft)
- Python Extension Pack
- SQLite Viewer (optional)
- Thunder Client (optional)

---

## 📁 Part 2: Project Setup

### 📥 1. Download & Open Project

- Clone or download the project
- Extract if needed and open in VS Code:



### 🐍 2. Set Up Python Environment

Open terminal (`Ctrl+``) and run:

python -m venv venv

for windows -
venv\Scripts\activate

for mac/ios -
source venv/bin/activate


 3. Install Python Dependencies

pip install flask flask-login flask-sqlalchemy flask-wtf gunicorn nltk openai psycopg2-binary sqlalchemy werkzeug wtforms email-validator
📚 4. Download NLTK Data

python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
⚙️ Part 3: Configuration
🔐 1. Create .env File
In the project root, create .env and add:

SESSION_SECRET=your_random_secret_key_here
DATABASE_URL=sqlite:///instance/app.db
OPENAI_API_KEY=your_openai_api_key_here
Replace the placeholders accordingly.

🧠 2. Select Python Interpreter
In VS Code:

Press Ctrl+Shift+P

Choose Python: Select Interpreter

Pick the interpreter from venv

🗄️ 3. Initialize Database

python -c "from app import app, db; app.app_context().push(); db.create_all()"
🚀 Part 4: Running the Project
⚙️ 1. Create Launch Configuration
Create .vscode/launch.json:


{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Flask",
      "type": "python",
      "request": "launch",
      "module": "flask",
      "env": {
        "FLASK_APP": "main.py",
        "FLASK_DEBUG": "1"
      },
      "args": [
        "run",
        "--host=0.0.0.0",
        "--port=5000"
      ],
      "jinja": true
    }
  ]
}
▶️ 2. Run the App
Method 1: Using Debugger

Press F5 or go to Run & Debug

Select Flask

Click ▶️

Method 2: Using Terminal

flask --app main run --host=0.0.0.0 --port=5000

🌐 3. Open in Browser
http://127.0.0.1:5000

🧪 Part 5: Development & Debugging
Set Breakpoints: Click beside line numbers in Python files.

View Logs: Open View → Debug Console.

View Database: Use SQLite Viewer to open instance/app.db.

🛠️ Part 6: First-Time Setup
Open the app in browser.

Click Register on the login page.

Choose Teacher role to start creating content.

Log in and use the dashboard.

❗ Troubleshooting
Issue	Solution
❌ Port in Use	Change port in launch.json or stop other services
❌ No module named ...	Activate environment & run pip install <module>
❌ NLTK Errors	Run:
python -c "import nltk, os; nltk_dir = os.path.join(os.getcwd(), 'nltk_data'); nltk.download('punkt', download_dir=nltk_dir); nltk.download('stopwords', download_dir=nltk_dir); nltk.download('wordnet', download_dir=nltk_dir)"
❌ Database Issues	Delete and recreate DB:
rm -f instance/app.db
python -c "from app import app, db; app.app_context().push(); db.create_all()"

📄 License
This project is licensed under the MIT License.

🙋‍♂️ Contributions
Feel free to fork and contribute via pull requests!



