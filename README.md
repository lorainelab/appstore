This is a Loraine Lab fork of the Cytoscape App Store code, with some changes.

* The Cytoscape App code branch `wip` (work-in-progress) branch is our `master` branch
* The Cytoscape App code branch `master` branch is our `master-old` branch

We are using this repository to develop an IGB App Store, working from the Cytoscape code base. 

We hope our changes can be incorporated into the Cytoscape App Store code, which is hosted [here](https://github.com/cytoscape/appstore):

[Link to Instructions for CytoScape setup](https://github.com/cytoscape/appstore/wiki/Steps-to-Setup-Cytoscape-Appstore-on-VM)

## Steps to set up on EC-2:

Login to the ec2 instance using the pem file. Find more [here](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/putty.html)
(For Ubuntu AMI, The username is 'ubuntu')
Once logged in, follow the steps below:

### Use virtualenv to install dependencies. `sudo pip3 install virtualenv` [usage info](https://virtualenv.pypa.io/en/latest/userguide/#usage)
1. Use `sudo apt-get update` to update the package lists.
2. cd to your home directory. `cd ~`
	Fork this repo, and then clone the repo from your own bitbucket using `git clone git@bitbucket.org:<username>/appstore.git CyAppStore`
	First, we need to enable ssh into your bitbucket. Follow the instructions [here](https://confluence.atlassian.com/bitbucket/set-up-an-ssh-key-728138079.html#SetupanSSHkey-ssh2) to create a public and private ssh keys and add it to the bitbucket account.  
	Then clone the repository.
3. cd into CyAppStore `cd CyAppStore` and add logs directory: `mkdir logs`
4. `sudo chgrp -R www-data *` and `sudo chgrp -R www-data .git*`
5. use `./installDependencies.sh` to install all the dependencies required by the Appstore. you may need to give permission to execute the file using chmod command

6. Install Xapian (**Optional for now**)
	Detailed steps [here](https://xapian.org/docs/install.html)
	`curl -O https://oligarchy.co.uk/xapian/1.4.7/xapian-core-1.4.7.tar.xz`
	`curl -O https://oligarchy.co.uk/xapian/1.4.7/xapian-omega-1.4.7.tar.xz`
	`curl -O https://oligarchy.co.uk/xapian/1.4.7/xapian-bindings-1.4.7.tar.xz`
	
	`tar xf xapian-core-1.4.7.tar.xz`
	`tar xf xapian-omega-1.4.7.tar.xz`
	`tar xf xapian-bindings-1.4.7.tar.xz`
	
	Xapian Core:
	`cd xapian-core-1.4.7` then `./configure` then `make` followed by `sudo make install`
	
	Xapian Omega:
	`sudo apt-get install libmagic-dev`
	`sudo apt-get update`
	`sudo apt-get install libpcre3 libpcre3-dev`
	
	`cd ../xapian-omega-1.4.7` then `./configure` then `make` followed by `sudo make install`
	
	Xapian bindings:
	`cd ../xapian-bindings-1.4.7` then `./configure` then `make` followed by `sudo make install`

#### GeoIP: (**Optional for now**)

1. `cd ~/CyAppStore/download/geolite directory`, and then  `make`.
2. `apt-cache search geoip`
3. `sudo apt-get install libgeoip-dev -y`
4. Copy all the files with ‘-template.py’ end with their names after removing ‘-template’ part (dbs-template.py, apikeys-template.py, geoip-template.py, mvn-template.py, emails-template.py) Eg. ‘cp dbs-template.py dbs.py’
5. cd `~/CyAppStore/` and then `cp maven-app-repo-settings-template.xml maven-app-repo-settings.xml`

#### Set-up MySQL-server:
1. make sure mysql-server is installed.
2. Set up mysql security settings like root password using `sudo mysql_secure_installation`
3. To see if the mysql server is running, use `sudo systemctl status mysql.service`
	refer [this link](https://www.digitalocean.com/community/tutorials/how-to-install-the-latest-mysql-on-ubuntu-16-04#step-2-%E2%80%94-installing-mysql) for more information 

4. Create a database in mysql. You can enter MySQL client using `mysql -u <username> -p`  
	However, root user needs to use sudo to enter databse.
	query for creting new database (named testdjango) is: `create database testdjango`
5. Create new user in mysql, other than root, which we will be used by django app to accesst the db:   
	a. enter mysql with root: `sudo mysql -u root -p`  
	b. `create user 'igbuser'@'localhost' identified by 'Igb@1234';`  
	c. `grant usage on *.* to 'igbuser'@'localhost';`  
	d. `grant all privileges on testdjango.* to 'igbuser'@'localhost';`  
6. Update the settings.py file in the home folder of the appstore repo to include the database settings:   
	---settings.py:---  
change the database settings:  
		DATABASES = {  
	    'default': {  
	        'ENGINE': 'django.db.backends.mysql',  
	        'NAME': 'testdjango',  
	        'USER': '<username-of-mysql-user>',  
	        'PASSWORD': '<password-of-mysql-user>',  
	        'HOST': 'localhost',   # Or an IP Address that your DB is hosted on  
	        'PORT': '3306',  
			  }  
	   }  

### Setting up Apache

1. install mod_wsgi using the instructions from [this link](https://modwsgi.readthedocs.io/en/develop/user-guides/quick-installation-guide.html)
2. create a new file CyAppStore.conf in `~/CyAppStore/apache/`. and add following apache config to the file in order to host django app on apache.   

```python
	#note- give the path to site-packages directory (where django is installed) in the virtual enviornment ('appstoreEnv' here). doesnt work without virtual environment.   
	WSGIDaemonProcess cyappstore python-path= /home/<username>/CyAppStore/appstoreEnv)/lib/python3.6/site-packages   

	WSGIProcessGroup cyappstore   
	Alias /static /home/<username>/CyAppStore/static   

	#path to wsgi config for the django app to be hosted   
	WSGIScriptAlias / /home/<username>/CyAppStore/django.wsgi   

	#Give access to static files like css   
	<Directory /home/<username>/CyAppStore/static>   
	   Require all granted   
	</Directory>   

	#give access to django.wsgi   
	<Directory /home/<username>/CyAppStore >   
		<Files django.wsgi>   
			Order deny,allow   
			Require all granted   
		</Files>   
	</Directory>  
```

	**Note: Change '/home/<username>/CyAppStore' according to your username**

Include this config in apache using Include directive:
	add following line in the /etc/apache/sites-available/000-default.conf
	Include ~/CyAppStore/apache/CyAppStore.conf
	
#### Changes to CyAppStore/django.wsgi:

1. Change path of SITE_PARENT_DIR to point to the parent directory of the project CyAppStore. i.e. `SITE_PARENT_DIR = ~`
2. Change the DJANGO_SETTINGS_MODULE i.e. `os.environ['DJANGO_SETTINGS_MODULE'] = 'CyAppStore.settings'`


#### Changes to CyAppStore/settings.py:
1. Change SITE_DIR to give absolute path to the CyAppStore directory i.e. `SITE_DIR = ~/CyAppStore`
2. Find and comment the line starting with- `STATIC_ROOT = SITE_DIR + "/Static/"`
3. Find comment the line starting with-  `filejoin(Site_dir, '/home/jeff`

### Starting the app:
1. Run `python3 manage.py makemigrations`
2. Run `python3 manage.py migrate`
3. Run `python3 manage.py runserver 8080` This will host the app on localhost:8080  


To run on apache, make sure you performed the steps mentioned above for ** setting up apache ** then restart apache using `sudo service apache2 restart`  
Any logs for apache are generated in Ubuntu at- /var/log/apache2



