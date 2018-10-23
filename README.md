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
4. cd into “/var/www/” if www is not present, create it by using `cd /var` then `sudo mkdir www` and then `cd www`
5. First, fork from this repo, and then clone the repo from your own bitbucket using `git clone git@bitbucket.org:<username>/appstore.git igb-appstore`
	
	If you face an issue to clone the repo, we need to enable ssh into your bitbucket. follow the instructions in the following link to create a public and private ssh keys and add to the bitbucket account.
	https://confluence.atlassian.com/bitbucket/set-up-an-ssh-key-728138079.html#SetupanSSHkey-ssh2
	Then clone the repository.