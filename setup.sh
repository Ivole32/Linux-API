#!/usr/bin/env bash

set -e

REPO_URL="https://github.com/Ivole32/Linux-API"
PROJECT_DIR="./Linux-API"

ask() {
    while true; do
        read -rp "$1 (y/n): " yn
        case $yn in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "Please answer yes or no." ;;
        esac
    done 
}

echo "Linux-API interactive setup"
echo "================================"

# System update
if ask "Update system packages?"; then
    sudo apt update && sudo apt upgrade -y
fi

# Install dependencies
if ask "Install required system packages"; then
    sudo apt install -y python3-venv python3-pip git ca-certificates curl gnupg libpq-dev postgresql-client
fi

# Docker repository
if ask "Add docker repository?"; then
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
        https://download.docker.com/linux/ubuntu \
        $(. /etc/os-release && echo $VERSION_CODENAME) stable" \
        | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
fi

# PostgreSQL repository
if ask "Add PostgreSQL repository?"; then
    sudo install -d /usr/share/postgresql-common/pgdg
    curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc \
        | sudo gpg --dearmor -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.gpg
    echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.gpg] \
    http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" \
        | sudo tee /etc/apt/sources.list.d/pgdg.list
fi

if ask "Refresh package lists?"; then
    sudo apt update
fi

# Install docker
if ask "Install Docker & Compose"; then
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
fi

if ask "Test Docker installation?"; then
    sudo docker run hello-world
fi

if ask "Allow current user to run Docker without sudo?"; then
  sudo usermod -aG docker $USER
  echo "Log out and back in for group changes to apply."
fi

# Clone repo
if ask "Clone Linux-API repository?"; then
    git clone "$REPO_URL"
fi

cd "$PROJECT_DIR"

# Python enviornement
if ask "Create python venv?"; then
    python3 -m venv venv
fi

if ask "Activate venv and install dependencies?"; then
    source ./venv/bin/activate
    pip install -r ./requirements.txt
fi

# .env config
if ask "Create .env file from example?"; then
    cp example.env .env
    echo "Generated secret:"
    openssl rand -hex 32
    echo "Past this into API_KEY_SECRET inside .env"
    echo -e "\033[33mWarning:\033[0m You need to configure .env manually. Check the docs or comments inside the file." >&2
fi

# Configure project paths
if ask "Update config paths automatically?"; then
    NEW_BASE="$(pwd)"
    sed -i "s|DATABASE_BACKUP_DIR = .*|DATABASE_BACKUP_DIR = r\"$NEW_BASE/backup\"|" ./api/config/config.py
    sed -i "s|ALEMBIC_INI_FILE = .*|ALEMBIC_INI_FILE = r\"$NEW_BASE/alembic.ini\"|" ./api/config/config.py
fi

if ask "Start database containers?"; then
    cd docker
    docker compose --env-file ../.env up -d
    echo -e "\033[33mWarning:\033[0m You may need to run 'docker compose --env-file ../.env up -d' inside ./docker again..." >&2
    cd ..
fi

echo "It is recommendet to edit config values in ./api/config/config.py. Take a look."
echo "Run start.sh to start the server"
echo
echo "Setup finished!"