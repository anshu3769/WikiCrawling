After the installation of MySQL server, run the following steps:-

1. From the terminal, issue the command - sudo /etc/init.d/mysql start

2.It will start the sql server for you. Now run the following command to login to the sql prompt - sudo sqld

3. From the sql> prompt, issue these commands to create database and a table in the database -
	a) create wiki;
	b) use wiki;
	c) create table WikiTable( id int PRIMARY KEY NOT NULL AUTO_INCREMENT,Wiki_Title varchar(1024),Wiki_URL varchar(2100),Wiki_Body longtext, Wiki_References mediumtext);

It will create the database and table for you. Now, you can use them in your program after connecting to the sql server.  

