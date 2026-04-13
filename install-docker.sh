#!/usr/bin/env bash
set -euo pipefail

echo "==> Installing Docker Engine on Ubuntu 24.04 (WSL2)"

# 1. Dependencies
apt-get update -qq
apt-get install -y -qq ca-certificates curl

# 2. Docker GPG key + apt repo
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
     -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  | tee /etc/apt/sources.list.d/docker.list > /dev/null

# 3. Install Docker Engine + Compose plugin
apt-get update -qq
apt-get install -y docker-ce docker-ce-cli containerd.io \
                   docker-buildx-plugin docker-compose-plugin

# 4. Enable + start daemon
systemctl enable docker
systemctl start docker

# 5. Allow current user to run docker without sudo
CURRENT_USER="${SUDO_USER:-$(logname 2>/dev/null || whoami)}"
usermod -aG docker "$CURRENT_USER"

echo ""
echo "==> Done. Docker $(docker --version)"
echo "==> NOTE: open a new terminal (or run 'newgrp docker') for group changes to take effect."
