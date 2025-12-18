"""
HelloWorld Application

A simple web application that displays "Hello World" message.
Implements US-001: Display Hello World Message from issue #41
"""

from flask import Flask, jsonify
from datetime import datetime
import time

app = Flask(__name__)

# Application version
VERSION = "1.0.0"

# Track application start time for uptime calculation
START_TIME = time.time()


@app.route('/')
def hello_world():
    """
    Main endpoint that serves the HelloWorld page.

    Implements:
    - US-001: Display Hello World Message
    - AC-001: Hello World message displayed prominently
    - AC-004: Mobile responsiveness

    Returns:
        HTML page with "Hello World" message displayed
        centered on the screen with responsive design.
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Hello World</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI',
                             'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell',
                             'Fira Sans', 'Droid Sans', 'Helvetica Neue',
                             sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #ffffff;
            }

            main {
                text-align: center;
                padding: 20px;
            }

            h1 {
                font-size: 48px;
                font-weight: 700;
                animation: fadeIn 1s ease-in;
            }

            @keyframes fadeIn {
                from {
                    opacity: 0;
                    transform: translateY(-20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            /* Responsive breakpoints for AC-004 */
            @media (max-width: 768px) {
                h1 {
                    font-size: 36px;
                }
            }

            @media (min-width: 769px) and (max-width: 1024px) {
                h1 {
                    font-size: 42px;
                }
            }

            @media (min-width: 1025px) {
                h1 {
                    font-size: 48px;
                }
            }
        </style>
    </head>
    <body>
        <main>
            <h1>Hello World</h1>
        </main>
    </body>
    </html>
    """
    return html_content, 200, {'Content-Type': 'text/html'}


@app.route('/health')
def health_check():
    """
    Health check endpoint for monitoring application status.

    Returns:
        JSON response with:
        - status: "healthy" indicating service is running
        - message: Confirmation message
        - timestamp: Current time in ISO 8601 format
        - uptime: Seconds since application started
        - version: Application version number
    """
    uptime_seconds = int(time.time() - START_TIME)

    health_status = {
        "status": "healthy",
        "message": "HelloWorld service is running",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "uptime": uptime_seconds,
        "version": VERSION
    }

    return jsonify(health_status), 200


if __name__ == '__main__':
    # Run the Flask development server
    # For production, use a WSGI server like gunicorn or uwsgi
    app.run(host='0.0.0.0', port=5000, debug=True)
