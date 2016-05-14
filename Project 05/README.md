# Project 05 - Linux Server Configuration

Project: Set up the Catalog App (Project 03) of Udacity's Full-Stack Web Developer Nanodegree on an secure Linux server.

Author: Thomas Mühlegger

## i.

IP-Address: 52.36.159.226
Port: 2200

## ii.

URL to application: http://ec2-52-36-159-226.us-west-2.compute.amazonaws.com/

## iii.

### Launch your Virtual Machine with your Udacity account. Please note that upon graduation from the program your free Amazon AWS instance will no longer be available.
1. Download Private Key from https://www.udacity.com/account#!/development_environment

2. Move the private key file into the folder ~/.ssh (where ~ is your environment's home directory). So if you downloaded the file to the Downloads folder, just execute the following command in your terminal. 
```bash
mv ~/Downloads/udacity_key.rsa ~/.ssh/
```

3. Open your terminal and type in 
```bash
chmod 600 ~/.ssh/udacity_key.rsa
```

### Follow the instructions provided to SSH into your server
In your terminal, type in
```bash
ssh -i ~/.ssh/udacity_key.rsa root@52.36.159.226
```
    
### Create a new user named grader
```bash
adduser grader
```
Follow the instructions (password: grader)
    
### Give the grader the permission to sudo
```bash
adduser grader sudo
```
    
### Update all currently installed packages
```bash
apt-get update
apt-get upgrade
reboot
```
    
### Change the SSH port from 22 to 2200
```bash
nano /etc/ssh/sshd_config
```
Change line 'Port 22' to 'Port 2200' and save the file (ctrl+o)
```bash
service ssh restart
```
Now to connect, use:
```bash
ssh -i ~/.ssh/udacity_key.rsa root@52.36.159.226 -p 2200
```
    
### Configure the Uncomplicated Firewall (UFW) to only allow incoming connections for SSH (port 2200), HTTP (port 80), and NTP (port 123)
```bash
ufw status
ufw default deny incoming
ufw default allow outgoing
ufw allow 2200/tcp
ufw allow http
ufw allow ntp
ufw enable
ufw status
```
    
### Configure the local timezone to UTC
```bash
dpkg-reconfigure tzdata
```
Select 'None of the above'
Set to 'UTC'
To check the timezone:
```bash
date
```
   
### Install and configure Apache to serve a Python mod_wsgi application
```bash
apt-get install apache2
apt-get install libapache2-mod-wsgi
nano /etc/apache2/sites-enabled/000-default.conf
```
Add line ```WSGIScriptAlias / /var/www/html/myapp.wsgi``` right before the closing ```</VirtualHost>```.
(to save 'ctrl+o')

Create myapp.wsgi (```nano /var/www/html/myapp.wsgi```)
```bash
    def application(environ, start_response):
    status = '200 OK'
    output = 'Hello World!'

    response_headers = [('Content-type', 'text/plain'), ('Content-Length', str(len(output)))]
    start_response(status, response_headers)

    return [output]
```
Restart apache
```bash
apache2ctl restart
```
    
### Install and configure PostgreSQL
```bash
apt-get install postgresql
```
    
#### Do not allow remote connections
This is the current default when installing PostgreSQL from the Ubuntu repositories.
    
#### Create a new user named catalog that has limited permissions to your catalog application database
```bash
nano /etc/postgresql/9.3/main/pg_hba.conf
```
Change following lines (peer -> md5)
```bash
# Database administrative login by Unix domain socket
local   all             postgres                                md5 
# "local" is for Unix domain socket connections only
local   all             all                                     md5
```
Restart postgreSQL
```bash
service postgresql restart
```
Switch to user postgres and run following commands:
(Password of postgres set to postgres)
```bash
su - postgres
psql
\password
create user catalog;
ALTER USER catalog PASSWORD 'catalog';
create database catalog;
```
    
### Install git, clone and setup your Catalog App project (from your GitHub repository from earlier in the Nanodegree program) so that it functions correctly when visiting your server’s IP address in a browser. Remember to set this up appropriately so that your .git directory is not publicly accessible via a browser!

#### Install git and adjust application
```bash
apt-get install git
cd /var/www/
git clone https://github.com/TomMuehlegger/full_stack_web_developer.git
cd full_stack_web_developer/
mv Project\ 03/ ../catalogApp
rm -rf full_stack_web_developer
cd ../catalogApp
```
Create catalogApp.wsgi (```nano catalogApp.wsgi```):
```bash
#!/usr/bin/python
import logging, sys

logging.basicConfig(stream=sys.stderr)

from application import app as application
import config

application.secret_key = config.SECRET_KEY
```

Did some changes to the appication (checked in to project 05 repo):

* Export configuration stuff to config.py (__index__.py needed)
    * Database connection string
    * Secret application key
    
* Change the database connection string to postgreSQL


#### Install application dependencies
```bash
apt-get install python-pip 
pip install Flask
pip install Flask-SQLAlchemy
pip install httplib2
apt-get build-dep python-psycopg2
pip install psycopg2
```
#### Set up the virtual environment:
```bash
pip install virtualenv
virtualenv catalogEnv
nano /etc/apache2/sites-available/catalogApp.conf
```
Content of file catalogApp.conf:
```bash
<VirtualHost *:80>
    ServerName 52.36.159.226
    DocumentRoot /var/www/catalogApp
    WSGIDaemonProcess catalogApp home=/var/www/catalogApp python-path=/var/www/catalogApp:/var/www/catalogApp/$
    WSGIProcessGroup catalogApp
    WSGIPassAuthorization on
    WSGIScriptAlias / /var/www/catalogApp/catalogApp.wsgi
    #DocumentRoot /var/www/catalogApp
    <Directory /var/www/catalogApp>
            Order allow,deny
            Allow from all
    </Directory>
    ErrorLog ${APACHE_LOG_DIR}/catalogApp-error.log
    LogLevel warn
    CustomLog ${APACHE_LOG_DIR}/catalogApp-access.log combined
</VirtualHost>
```
Enable the catalog site:
```bash    
a2ensite catalogApp.conf
```
Disable the defaut page:
```bash
a2dissite 000-default.conf
```
Restart apache:
```bash
source /etc/apache2/envvars
apache2ctl restart
```
#### Update Facebook application domain (on http://developers.facebook.com)
To -> http://ec2-52-36-159-226.us-west-2.compute.amazonaws.com/

## iv.
https://www.udacity.com/account#!/development_environment
http://stackoverflow.com/questions/12720967/how-to-change-postgresql-user-password
University courses: 'Intro to Linux' and 'Realtional databases' ;-)