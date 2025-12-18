"""
HelloWorld Application

A simple web application that displays "Hello World" message.
Implements Story 1: Display Hello World Message from issue #39
"""

from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

# Application version
VERSION = "1.0.0"

# Track application start time for uptime calculation
import time
START_TIME = time.time()


@app.route('/')
def hello_world():
    """
    Main endpoint that serves the HelloWorld page.

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
        <title>HelloWorld App</title>
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

            /* Responsive breakpoints */
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
        - status: "healthy" or "unhealthy"
        - timestamp: current time in ISO 8601 format
        - version: application version
        - uptime: seconds since application started
    """
    uptime_seconds = int(time.time() - START_TIME)

    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": VERSION,
        "uptime": uptime_seconds
    }

    return jsonify(health_status), 200


if __name__ == '__main__':
    # Run the Flask development server
    # For production, use a WSGI server like gunicorn or uwsgi
    app.run(host='0.0.0.0', port=5000, debug=True)
