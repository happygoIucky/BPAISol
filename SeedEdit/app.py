from flask import Flask, render_template, request
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        result = subprocess.run(['python', 'edit.py'], capture_output=True, text=True)
        return {'success': True, 'url': result.stdout.strip()}
    except Exception as e:
        return {'success': False, 'error': str(e)}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')