from flask import Flask, render_template, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def hello_world():
    """
    Main route that displays the Hello World message.
    Implements US-001 from issue #43.
    """
    return render_template('index.html')

@app.route('/health')
def health_check():
    """
    Health check endpoint to verify application status.
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'message': 'HelloWorld application is running'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
