# Hosting Linux-API with systemd (as a Service)

This guide explains how to run Linux-API as a systemd service for production use on Linux.

## Prerequisites
- Linux system with systemd
- Python 3.11+ and all dependencies installed
- Linux-API installed (see pip-hosting guide)


## Example systemd Service Files

You can run Linux-API as a service in two ways:

### 1. Using the provided shell script (`start.sh`)
Create a file `/etc/systemd/system/linux-api.service` with the following content:

```ini
[Unit]
Description=Linux-API Server (with start.sh)
After=network.target

[Service]
Type=simple
User=linuxapi
WorkingDirectory=/path/to/Linux-API
ExecStart=/bin/bash ./start.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### 2. Using the full Python command
Create a file `/etc/systemd/system/linux-api.service` with the following content:

```ini
[Unit]
Description=Linux-API Server (direct command)
After=network.target

[Service]
Type=simple
User=linuxapi
WorkingDirectory=/path/to/Linux-API
ExecStart=/usr/bin/python3 -m uvicorn linux_api.server:app --host 0.0.0.0 --port 8000
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

- Replace `/path/to/Linux-API` with your actual project path.
- Set `User=` to a dedicated user (recommended for security).


## Steps
1. **Reload systemd:**
   ```bash
   sudo systemctl daemon-reload
   ```
2. **Enable the service:**
   ```bash
   sudo systemctl enable linux-api
   ```
3. **Start the service:**
   ```bash
   sudo systemctl start linux-api
   ```
4. **Check status:**
   ```bash
   sudo systemctl status linux-api
   ```

## Notes
- Logs are available via `journalctl -u linux-api`.
- The admin API key is printed to the service log on first start.
