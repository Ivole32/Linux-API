
# Manual setup for Linux-API

This guide provides step-by-step commands and concise explanations for installing and running Linux-API on an Ubuntu server. The project was developed and tested on an Ubuntu 25 system; the steps should work on other recent Ubuntu releases as well.

## Prerequisites

- A machine running Ubuntu with a user that has `sudo` privileges.
- Internet access to download packages and container images.

## 1. Install system dependencies

Update package lists and upgrade installed packages:

```bash
sudo apt update
sudo apt upgrade -y
```

Install required packages (Python tooling, git, curl, GPG, and PostgreSQL client/dev files):

```bash
sudo apt install -y python3-venv python3-pip git ca-certificates curl gnupg libpq-dev postgresql-client
```

## 2. Install and configure Docker and PostgreSQL apt repositories

### 2.1 Add Docker apt repository

Create a directory for apt keyrings, download Docker's GPG key, and add the Docker repository:

```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### 2.2 Add PostgreSQL apt repository

Create the directory for the PostgreSQL key, download the key, and add the repository:

```bash
sudo install -d /usr/share/postgresql-common/pgdg
curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo gpg --dearmor -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.gpg
echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.gpg] http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" | sudo tee /etc/apt/sources.list.d/pgdg.list
```

Refresh package lists to include the new repositories:

```bash
sudo apt update
```

Install Docker and the PostgreSQL client (example: v18):

```bash
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin postgresql-client-18
```

Test Docker with a simple container:

```bash
sudo docker run hello-world
```

Optional: allow your user to run Docker without `sudo`:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

Note: logging out and back in also applies the group change.

## 3. Clone and prepare the Linux-API project

Clone the repository and enter the project directory:

```bash
git clone https://github.com/Ivole32/Linux-API
cd Linux-API
```

Create and activate a Python virtual environment, then install Python dependencies:

```bash
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

## 4. Configure environment and application settings

Create the environment file from the example and generate a secure API Secret for password hashing:

```bash
cp example.env .env
openssl rand -hex 32
```

Open `.env` in your preferred editor and set `API_KEY_SECRET` to the generated value. Fill in other variables (database credentials, hostnames, etc.) according to `example.env`. Keep `.env` secret.

Update a couple of paths in `./api/config/config.py` so the application can find them reliably. From the repository root, you can set `NEW_BASE` to the project root and run the replacements:

```bash
NEW_BASE="$(pwd)"
sed -i "s|DATABASE_BACKUP_DIR = .*|DATABASE_BACKUP_DIR = r\"$NEW_BASE/backup\"|" ./api/config/config.py
sed -i "s|ALEMBIC_INI_FILE = .*|ALEMBIC_INI_FILE = r\"$NEW_BASE/alembic.ini\"|" ./api/config/config.py
```

The first command sets the backup directory used by the app; the second points Alembic to the correct ini file.

## 5. Start database services with Docker Compose

Start the database and related containers using the `docker` compose definitions. From the repository root:

```bash
cd docker
docker compose --env-file ../.env up -d
cd ..
```

If services fail to start immediately, re-run the `docker compose` command once more. Verify containers are running with `docker ps` — you should see entries such as `linux_api-postgres` and `linux_api-pgpool`.

## 6. Run the API server (development)

Run the application using Uvicorn:

```bash
python3 -m uvicorn api.server:app --host 0.0.0.0 --port 8080 --log-level debug
```

If the server reports user creation errors at startup, stop and restart the server.

## Support

- Issues: https://github.com/Ivole32/Linux-API/issues
- Support the project: https://ko-fi.com/ivole32

---

Made with ❤️ by Ivole32 — https://github.com/Ivole32