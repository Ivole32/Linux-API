# Manual Hosting of Linux-API

This guide explains how to manually run the Linux-API server on your machine.

## Prerequisites
- Python 3.11 or newer
- All dependencies installed (see `requirements.txt`)

## Steps
1. **Clone the repository:**
   ```bash
   git clone https://github.com/Ivole32/Linux-API.git
   cd Linux-API
   ```
2. **Install dependencies:**
   ```bash
   pip install -r linux_api/requirements.txt
   ```
3. **Start the server:**
   ```bash
   python -m uvicorn linux_api.server:app --host 0.0.0.0 --port 8000
   ```
4. **Access the API docs:**
   Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser.

## Notes
- The admin API key is printed to the console on first startup. Save it securely.
- For development, you can use `--reload` with uvicorn for auto-reload on code changes.
