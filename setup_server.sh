#! /bin/sh
# Things to do on server:
# clone market_basket_app repo
# Access server with ssh -i ~/.ssh/market-basket-app ubuntu@<ip-address> -A
# Things to install on server: supervisor, nginx, redis, virtualenv
# Things to copy to certain destinations: copy nginx config of repo to sites-available
# copy supervisor config of repo to /etc/supervisor/conf.d/
# make a directory for the celery logs /var/log/supervisor/
# change permissions on /var/log/supervisor directory to 777
LIST_OF_APPS = "virtualenv supervisor nginx redis-server"
echo "Installing packages $LIST_OF_APPS"
sudo apt-get update -y && sudo apt-get install -y $LIST_OF_APPS

echo "Copying nginx and supervisor configs"
sudo cp deployment/nginx/market_basket_app /etc/nginx/sites-available/
sudo cp deployment/supervisor/configs/conf.d/* /etc/supervisor/conf.d/

echo "Creating log folders for supervisor"
sudo mkdir -p /var/log/supervisor
sudo chmod 777 /var/log/supervisor

