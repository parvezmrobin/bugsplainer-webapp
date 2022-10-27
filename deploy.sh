pkill gunicorn
./venv/bin/gunicorn -w=2 --bind=0.0.0.0:5002 --daemon --error-logfile=error.log server:app

sudo apt install nginx -y
yarn build
sudo mkdir -p /var/www/bugsplainer-webapp
sudo cp -r dist/* /var/www/bugsplainer-webapp/ --verbose
sudo service nginx restart
