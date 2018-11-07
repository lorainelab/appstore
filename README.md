This is a Loraine Lab fork of the Cytoscape App Store code, with some changes.

* The Cytoscape App code branch `wip` (work-in-progress) branch is our `master` branch
* The Cytoscape App code branch `master` branch is our `master-old` branch

We are using this repository to develop an IGB App Store, working from the Cytoscape code base. 

We hope our changes can be incorporated into the Cytoscape App Store code, which is hosted here: https://github.com/cytoscape/appstore

Link to Instructions for CytoScape setup - https://github.com/cytoscape/appstore/wiki/Steps-to-Setup-Cytoscape-Appstore-on-VM

## Steps to set up on EC-2:

Login to the ec2 instance using the pem file. Find more anout this at: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/putty.html.
(For Ubuntu AMI, The username is 'ubuntu')
Once logged in, follow the steps below:

1. Use `sudo apt-get update` to update the package lists.
2. Download “pip3” for Python3 to facilitate easy installation of Python packages using the command `sudo apt-get install python3-pip`
3. Install Django Version 1.8 using command: `pip3 install django==1.8` (installed at location: /home/<ubuntu>/.local/lib/python3.6/site-packages/django)
4. Install apache using `sudo apt-get install apache2`
5. First, fork from this repo, and then clone the repo from your own bitbucket using `git clone git@bitbucket.org:<username>/appstore.git`
	
	First, we need to enable ssh into your bitbucket. Follow the instructions in the following link to create a public and private ssh keys and add it to the bitbucket account.
	https://confluence.atlassian.com/bitbucket/set-up-an-ssh-key-728138079.html#SetupanSSHkey-ssh2
	Then clone the repository.
6. move the cloned directory to /var/www using `sudo mv CyAppStore /var/www`
7. cd into CyAppStore and add logs directory: `mkdir logs`
8. `sudo chgrp -R www-data *` and `sudo chgrp -R www-data .git*`
9. Install social-auth-app-django using `sudo pip3 install social-auth-app-django`
10. Install zlib1g-dev: `sudo apt-get install zlib1g-dev`
11. Install Pillow using `sudo pip3 install Pillow`
12. Install Xapian: (Steps taken from https://xapian.org/docs/install.html )
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
	
	`cd xapian-omega-1.4.7` then `./configure` then `make` followed by `sudo make install`
	
	Xapian bindings:
	`cd xapian-bindings-1.4.7` then `./configure` then `make` followed by `sudo make install`

13. `sudo apt-get install python3-dev libmysqlclient-dev`
14. `pip3 install mysqlclient` (instead of MySQL-python as it doesn't support python3)
14.  mod_wsgi for python 3:  `sudo apt-get install python3-pip apache2 libapache2-mod-wsgi-py3`

#### Install dependencies:
1. `pip3 install django-haystack`
2. `pip3 install Whoosh`
3. `sudo apt-get install libjpeg-dev`
4. `sudo apt-get install libpng-dev`
5. `pip3 install ipython` for debugging purposes


#### GeoIP:

1. go to download/geolite directory, type `make`.
2. `apt-cache search geoip`
3. `sudo apt-get install libgeoip-dev -y`
4. Copy all the files with ‘-template.py’ end with their names after removing ‘-template’ part (dbs-template.py, apikeys-template.py, geoip-template.py, mvn-template.py, emails-template.py) Eg. ‘cp dbs-template.py dbs.py’
5. In the home directory, `cp maven-app-repo-settings-template.xml maven-app-repo-settings.xml`

#### Installing MySQL-server:
1. `sudo apt-get install mysql-server`
2. Set up mysql security settings like root passwordetc. using `sudo mysql_secure_installation`
3. To see if the mysql server is running, use `sudo systemctl status mysql.service`
refer this link for more information
https://www.digitalocean.com/community/tutorials/how-to-install-the-latest-mysql-on-ubuntu-16-04#step-2-%E2%80%94-installing-mysql

#### Setting up the MySQL:
1. Create a database in mysql. You can enter MySQL client using `mysql -u <username> -p`
2. Update the settings.py file in the home folder of the appstore repo to include the database settings:
	---settings.py:---
	DATABASES = {
			'default':{
			'ENGINE': 'django.db.backends.mysql',
			'OPTIONS': {
				'read_default_file': '/etc/mysql/my.cnf',
			},
			}
		}

3. Add the database details in the file /etc/mysql/my.conf
	[client]
	database = <name_of_db>
	user = <username>
	password = <pwd>
	default-character-set = utf8

### Starting the app:

1. Comment the line starting with STATIC_ROOT = SITE_DIR + "/Static/"..........
2. Comment the line starting with filejoin(Site_dir, '/home/jeff.......
3. Run `python3 manage.py migrate`
4. Run `python3 manage.py runserver 8080` This will host the app on localhost:8080

