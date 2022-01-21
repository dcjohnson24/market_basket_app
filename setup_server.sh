#! /bin/sh
# Things to do on server:
# clone market_basket_app repo
# Access server with ssh -i ~/.ssh/market-basket-app ubuntu@<ip-address> -A
# Things to install on server: supervisor, nginx, redis, virtualenv
# Things to copy to certain destinations: copy nginx config of repo to sites-available
# copy supervisor config of repo to /etc/supervisor/conf.d/
# make a directory for the celery logs /var/log/supervisor/
# change permissions on /var/log/supervisor directory to 777
LIST_OF_APPS="virtualenv supervisor nginx redis-server"
echo "--> Installing packages $LIST_OF_APPS"
sudo apt-get update -y && sudo apt-get install -y $LIST_OF_APPS

echo "--> Copying nginx and supervisor configs"
sudo cp deployment/nginx/market_basket_app /etc/nginx/sites-available/
sudo cp deployment/supervisor/configs/conf.d/* /etc/supervisor/conf.d/

echo "--> Creating log folder for supervisor"
sudo mkdir -p /var/log/supervisor
sudo chmod 777 /var/log/supervisor

echo "-- > Creating log folder for celery"
sudo mkdir -p /var/log/celery
sudo chmod 777 /var/log/celery

echo "--> Installing docker"
sudo apt-get update
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

curl \
    -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io

echo "--> Check that docker is running"
sudo systemctl status docker

echo "--> Run docker without sudo"
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
docker run hello-world