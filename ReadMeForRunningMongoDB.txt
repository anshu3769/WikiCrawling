Please follow the steps to download and install MongoDb:


1.Execute the following command to create MongoDb enterprise repo -
vi /etc/yum.repos.d/mongodb-enterprise.repo

2. This will open up a file for you. Enter the following contents in the file -

[mongodb-enterprise]
name=MongoDB Enterprise Repository
baseurl=https://repo.mongodb.com/yum/redhat/$releasever/mongodb-enterprise/3.6/$basearch/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-3.6.asc

Save and close the file.

3. Execute the following commands to enable the repo - 
	a) Check the id of the mongodb repo
		yum repolist all
	   This will give a list of the currently present repos in the system. Note down the mongodb repo id to be used in next command.
	b) Enable the repo
		yum-config-manager --enable mongodb-enterprise/x86_64
		
4. Execute the following command to install mongodb - 
sudo yum install -y mongodb-enterprise

5. Mongodb needs this directory to run. Create the directory with the following command -
sudo mkdir -p /data/db

6.To run mongodb server, execute the following commands
sudo mongod

7.To create the database in mongodb, execute the following command - 
mongo
use wiki

8. To create mongo db collection named "content", execute -
db.createCollection("content")

mongodb is up and running now.
