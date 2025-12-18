# HelloWorld Application

A simple web application that displays "Hello World" message to users.

## Features

- Displays "Hello World" message on the main page
- Responsive design (mobile, tablet, desktop)
- Health check endpoint for monitoring
- WCAG 2.1 AA accessibility compliant

## Implementation Details

Implements User Story US-001 from Issue #43:
- As a visitor, I can see a "Hello World" message when accessing the main page
- Cross-browser compatible
- Mobile responsive
- Page loads within 3 seconds

## Endpoints

- `GET /` - Main page displaying Hello World message
- `GET /health` - Health check endpoint returning application status

## Technology Stack

- Python 3.x
- Flask (Web Framework)
- HTML5, CSS3
