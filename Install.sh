#Format the drive using ext4 file system
mkfs.ext4 /dev/sdg

#Mount the drive in /prod
mkdir /prod
mount /dev/sdg /prod

#Download and install JDK
rpm -ivh jdk-10.0.1_linux-x64_bin.rpm

#Download and install Tomcat
sudo yum install tomcat7 tomcat7-webapps

#Download and install MySQL
sudo yum install mysql-server

#Install pyhton-devel mysql-devel for connecting to MySql database from a python method
sudo yum install python-devel mysql-devel


#Install tools requied for python program
pip install -r requirmemts.txt



