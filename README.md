# CPSC559_Spoofy

A distributed web application for CPSC 559 - Distributed Systems

## Code Development

**Tools**:
 - PHP as the frontend
 - Apache as the servers
 - MySQL as the database
 - HAProxy as the proxy/load balancer
 - Python script running synchronizing and replicating the servers and database

Clone the project to a local directory:

 - `git clone https://github.com/Joey-mi/CPSC559_Distributed_Spoofy.git`

## Setting up the Environment Variables
Before running our website it's advised to take a look at the .env file and change the values to suit your system and database. The most important node to change would be MACHINE which is currently set to MacOs. If you're using Linux or Windows you need to change MACHINE to be 'Win' or 'Linux'.

Next we need to download a few things to make sure the environment variables work as intended:

- `pip install python-dotenv`
- Install the Visual Studio Installer
    - Then just select the Microsoft C++ Build Tools and download
- `pip install netifaces`

This should be all the setup require to use the environment variables. If after setting things up you want to hide your .env file simply add .env to the .gitignore file.

## Linking with MySQL
The first thing that needs to be created is the `SpoofyDB` database. This can be done through the mysql command line utility.
```
CREATE DATABASE SpoofyDB;
```

We will be using a test user between all contributors to not have to worry about updating credentials. This test user will have all privileges on the `SpoofyDB` database that was just created.
 - Test Username: `spoofyUser`
 - Test Password: `testing`

To add this user to MySQL through the command line utility:
```
CREATE USER 'spoofyUser'@'localhost'
    IDENTIFIED WITH mysql_native_password BY 'testing';
GRANT ALL PRIVILEGES 
    ON SpoofyDB.* 
    TO 'spoofyUser'@'localhost' 
    WITH GRANT OPTION;
```
List users with `SELECT user FROM Mysql.user;`

**Note:** If these steps are not followed, the database in the next step will not initialize.

## Setting up Default MySQL Database
There is an included python script ([initialize.py](InitDB/initialize.py)) that will automatically construct our mysql database and fill it with default values.

This can be run with `python InitDB/initialize.py init`. The test user and database must be created before this is run.

 - `python InitDB/initialize.py help` for more options.

If the python script fails to run due to failed imports, you may need to run `pip install mysql-connector-python` for the python mysql driver.

**WARNING**: This will overwrite your current database and reset it to its default state if the `SpoofyDB` database already exists.

Feel free to add insert queries to the `initialize_data` function in `data.py` to increase the size of our default database. Remember to `refresh` the database whenever you make changes to ensure those changes worked correctly.

 - The only data that does not currently have defaults are `Playlist` and `Playlist_Contains`

## PHP and Apache Server Setup

AppServ ([download](https://www.appserv.org/en/download/)) will handle setting up PHP and Apache. Ensure that these are added to your PATH. Don't install mysql if it is already installed.

Once AppServ is installed, you need to edit the Apache default `DocumentRoot` to our working directory.
 - Navigate to the AppServ install (default: `C:\AppServ\Apache24`)
 - Open `conf\httpd.conf` (make a backup copy just in case)
 - Ctrl-F to find `DocumentRoot`, set this to point to `Spoofy` in the project directory
 - You may need to run `httpd -d C:<project_dir>\Spoofy`
 - Restart Apache with the `Apache Restart` utility installed with AppServ
 - Go to your webbrowser and go to `localhost` (optionally `localhost:80`)

To allow for load balancing and the ability for a client to be connected to any server the default Apache `ServerName` will also need to be updated.
 - Navigate to the AppServ install (default: `C:\AppServ\Apache24`)
 - Open `conf\httpd.conf` (make a backup copy just in case)
 - Ctrl-F to find `ServerName`, and change the IP to each server's current IP address. For example the `ServerName` could now read `ServerName 10.13.83.202:80`.
  - Restart Apache with the `Apache Restart` utility installed with AppServ

Apache logs should be stored at `C:\AppServ\Apache24\logs`. If you open `error.log` in Visual Studio Code it will automatically update the file whenever new logs are created.

## Running Python Distributor File
The file `spoofy_distributor.py` must be run on every computer that will host the database (every computer that will act as a replica). In order to run it the following Python module installations must be run:
 - `pip install mysql-connector-python`
 - `pip install netifaces`
 - `pip install python-dotenv`
 - `pip install requests`

There will need to be a '**primary**' replica that initiates the passing of the token once all the replicas are running. This is indicated as the command line input `--prim`. The rest of the replicas can be run as a non-primary replica with the command line input `--no`. Note that the primary replica must be started after all the other replicas have their Python script running so that the token passing can commence properly. Also please note that all the replica python scripts must be started in quick succession to avoid triggering a timeout on the token passing. The program can be run two different ways, with a proxy included or without. In this instance a proxy will be a part of the system, so it can be indicated as the command line input `--proxy`. The rest of the command line inputs for the program are the IP addresses (in no particular order) of all the replicas in the system (including the IP of the computer the program is running on).

**Commands:**
 - TO RUN A NON-PRIMARY REPLICA WITH A PROXY
    - `python spoofy_distributor.py --no --proxy <list of ALL replicas in system, INCLUDING your own>`
 - TO RUN THE PRIMARY REPLICA WITH A PROXY
    - `python spoofy_distributor.py --prim --proxy <list of ALL replicas in system, INCLUDING your own>`
 - Example of a non-primary replica, with a proxy, and three replicas in the system
   - `python spoofy_distributor.py --no --proxy 10.13.83.202 10.13.105.49 10.13.145.125`
 - Example of a primary replica, with a proxy, and three replicas in the system
   - `python spoofy_distributor.py --prim --proxy 10.13.83.202 10.13.105.49 10.13.145.125`

## Setting up HAProxy
For this project we're using HAProxy for the load balancer. Install this from [https://www.haproxy.org/](https://www.haproxy.org/) on either a linux machine or VM (there is no Windows/Mac version as of yet) and copy our haproxy.cfg file into `/etc/haproxy`, overwriting the default configuration file. Make sure to edit the configuration file to use the correct ip addresses for your proxy and servers. Finally, run the load balancer **as Root** from the command line with:
 - `haproxy -f /etc/haproxy/haproxy.cfg -db`
