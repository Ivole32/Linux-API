**Note:** This automated installer is provided for convenience. It can be faster than manual setup but may be less flexible and may require adjustments on some systems. If you are comfortable configuring services manually, prefer the manual instructions.

## Prerequisites

- A machine running Ubuntu (24/25 recommended) with a user that has `sudo` privileges.
- Internet access to download packages and container images.
- Git installed. On Ubuntu install with:

```bash
sudo apt update
sudo apt install -y git wget curl
```

## 1. Download the setup script

Download the installer script from the repository. Review it before running if you prefer:

```bash
wget https://raw.githubusercontent.com/Ivole32/Linux-API/main/setup.sh -O setup.sh
# or view it first
less setup.sh
```

## 2. Make the script executable and run it

Make the script executable and run it. Run it inside a terminal you can monitor.

```bash
chmod +x ./setup.sh
sudo ./setup.sh
```

Notee: The script may prompt for confirmation. If you trust the script, accepting defaults is usually fine; otherwise inspect the script and re-run only the parts you need.

## 3. Configure environment and application settings

The installer will create a `.env` file in the repository root containing a generated `API_KEY_SECRET` and placeholders for other variables. Edit `.env` to add database credentials, hostnames, and any other settings shown in `example.env`.

Recommended steps:

```bash
cp example.env .env          # if the script didn't create .env
# open .env in your editor and paste the printed API_KEY_SECRET value
# then fill other variables (DB credentials, host, etc.)
```

After editing `.env`, verify application-specific settings in `api/config/config.py` and update values there if needed.

Keep `.env` secret.

## Support

- Issues: https://github.com/Ivole32/Linux-API/issues
- Support the project: https://ko-fi.com/ivole32

---

Made with ❤️ by Ivole32 — https://github.com/Ivole32