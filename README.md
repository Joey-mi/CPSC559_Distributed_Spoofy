# CPSC471_Spoofy

A web application for CPSC 471 - Databases

See the [Project Proposal](Reports/Project_Proposal.pdf) for more details.

The [Functional Model](Reports/Functional_Model.pdf) includes the HIPO diagram, complete list of HIPO functions, DFD Diagram, and complete list of SQL Statements.

Additionally, see the [Diagrams](Diagrams/Diagrams.md) to inspect individual diagrams.

## Code Development

**Tools**:
 - PHP as the frontend
 - Apache as the server
 - MySQL as the database

Clone the project to a local directory:

 - `git clone https://github.com/alexs2112/CPSC471_Spoofy.git`

Small things to be done and cleaned up in the future are marked in comments with `@todo`. 

Our required unfinished tasks are in [Tasks.md](Tasks.md)

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

Apache logs should be stored at `C:\AppServ\Apache24\logs`. If you open `error.log` in Visual Studio Code or something, it will automatically update the file whenever new logs are created.
