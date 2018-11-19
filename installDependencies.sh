#!/bin/bash

declare -a aptpackages=("python3" "python3-pip" "apache2" "libapache2-mod-wsgi-py3" "zlib1g-dev" "python-dev" "libmysqlclient-dev" "libjpeg-dev" "libpng-dev" "mysql-server")
declare -a pippackages=("wheel" "django==1.8" "Pillow" "social-auth-app-django" "whoosh" "ipython" "django-haystack==2.2" "mysqlclient")
echo "Installing packages required by App store.."

for i in "${aptpackages[@]}"
do
    sudo apt install "$i"
done
pip3 install virtualenv
envname="appstoreEnv"
echo "Give virtual environment name:(Default:appstoreEnv):"
read name
name="${name:-$envname}"
python3 -m venv $name
source  $name"/bin/activate"
for i in "${pippackages[@]}"
do
   pip3 install "$i"
done
