from flask import Flask, render_template
import os
from documents import documents_bp
from chat_module import chat_bp

app = Flask(__name__, template_folder='.')

# Đăng ký các Blueprint
app.register_blueprint(documents_bp)
app.register_blueprint(chat_bp)

@app.route('/')
def home():
    return render_template('dashboard.html')

@app.route('/notebook.html')
def notebook():
    return render_template('notebook.html')

@app.route('/upload.html')
def upload():
    return render_template('upload.html')

@app.route('/analytics.html')
def analytics():
    return render_template('analytics.html')

@app.route('/profile.html')
def profile():
    return render_template('profile.html')

@app.route('/dashboard.html')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)