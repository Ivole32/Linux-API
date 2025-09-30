
# Hosting Linux-API via pip Installation

This guide explains how to install and run Linux-API as a Python package using pip.

## Prerequisites
- Python 3.11 or newer
- pip (Python package manager)


## Recommended: Use a Virtual Environment (Linux only)
It is strongly recommended to use a Python virtual environment to avoid dependency conflicts:

```bash
python3 -m venv venv
source venv/bin/activate
```

## Steps
1. **Install the package:**
   In the project root directory, run:
   ```bash
   pip install .
   ```
2. **Run the server:**
   You have several options (Linux only):
   - Run via Python module:
     ```bash
     python3 -m linux_api.server
     ```
   - Or, use the provided shell scripts:
     ```bash
     ./linux_api/start.sh
     # or for development with auto-reload:
     ./linux_api/start_debug.sh
     ```
3. **Access the API docs:**
  Open [http://localhost/docs](http://localhost/docs) in your browser.
Open docs: Open [http://67.207.74.82/docs](http://67.207.74.82/docs) in your browser.


## Notes
- This package is only supported on Linux systems.
- The admin API key is printed to the console on first startup. Save it securely.
- You may need `sudo` rights to bind to ports below 1024 (e.g., port 80 or 443).
- You can uninstall with `pip uninstall linux-api`.