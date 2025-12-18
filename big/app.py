from flask import Flask, send_from_directory
import os

app = Flask(__name__)

@app.route('/')
def show_one():
    """Serve the index.html page that displays '1'."""
    return send_from_directory(os.path.dirname(__file__), 'index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8082)
