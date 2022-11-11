pkill gunicorn
./venv/bin/gunicorn -w=2 --bind=localhost:5000 --daemon --error-logfile=error.log server:app

sudo apt install nginx -y
yarn build
sudo mkdir -p /var/www/bugsplainer-webapp
sudo cp -r dist/* /var/www/bugsplainer-webapp/ --verbose
sudo service nginx restart
