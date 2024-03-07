Floor
floorvi
Invisible

Jesse — 03/01/2024 7:11 PM
Meet at the usual time this Sunday?
Grant — 03/01/2024 7:11 PM
works for me
Eric — 03/01/2024 7:12 PM
👍
Jesse — 03/01/2024 7:12 PM
Alright. I'll be sure to do some more research into the replication before then.
Thanks every one. Good show. 
Floor — 03/02/2024 12:13 PM
guys, why does it say demo 3 for replication is due tomorrow 
Jesse — 03/02/2024 12:14 PM
The proposal for it is. Just like we had to hand in yesterdays’s proposal last Sunday.
Floor — 03/02/2024 12:14 PM
O
That makes more sense
So I guess we'll be writing that up at 12pm tmrrw
Eric — 03/03/2024 10:47 AM
if anyone wants to do some reading before the meeting: i think we can use HAProxy instead of an apache server for the load balancer, because making a custom load balancing algorithm for apache would be a massive pain, whereas with HAProxy we just write a lua script. There's also something called Nginx we could use, but from what i understand HAProxy has a better system for detecting crashed servers and location-based routing if we want to keep that idea.
https://www.haproxy.org/
HAProxy - The Reliable, High Perf. TCP/HTTP Load Balancer
Reliable, High Performance TCP/HTTP Load Balancer
Eric — 03/03/2024 12:15 PM
Yes, you can interact with a Python script running on a backend server from PHP. There are several ways to achieve this, depending on your specific requirements and the nature of the interaction you need. Here are a few common methods:

    HTTP Requests:
        You can use HTTP requests to communicate between PHP and Python scripts. Your Python script can expose an HTTP API (e.g., using Flask or Django) that PHP can call using functions like file_get_contents() or curl() in PHP.
        For example, PHP can send an HTTP POST request to the Python script with data as parameters, and the Python script can process the request and return a response.

    Inter-process Communication:
        If both the PHP and Python scripts are running on the same server or on servers with shared filesystem access, you can use inter-process communication methods like writing to shared files, using message queues, or shared memory.
        For example, PHP can write data to a file, and the Python script can periodically read from that file to process the data.

    Socket Communication:
        PHP and Python scripts can communicate via sockets. One script acts as a server, listening for incoming connections, while the other script acts as a client, initiating a connection and sending/receiving data.
        For example, the Python script can create a TCP server socket, and PHP can establish a TCP client connection to send data to the Python script.

    Remote Procedure Call (RPC):
        You can use RPC mechanisms like gRPC, XML-RPC, or JSON-RPC to invoke functions/methods in the Python script from PHP.
        For example, the Python script can expose functions/methods as RPC endpoints, and PHP can call these functions/methods remotely using an RPC client library.

    Shared Database:
        If both PHP and Python scripts need access to shared data, you can use a shared database (e.g., MySQL, PostgreSQL) as a communication channel. Both scripts can read from and write to the same database to exchange data.
        For example, PHP can insert data into a database table, and the Python script can periodically query the database for new data.

Choose the method that best fits your use case and requirements, considering factors like performance, scalability, security, and ease of implementation. Each method has its advantages and limitations, so evaluate them based on your specific needs.
Floor — 03/03/2024 12:52 PM
To do:
Python socket program (listener) - Get messages from other servers
Python socket program (sender) - Await orders from php Socket. Wait for changes and send to other servers
PHP socket program sends to the sender Python socket program
Alter mysql statements to forward statements to Python Script
HAProxy setup
 
Jesse — 03/03/2024 1:05 PM
https://stackoverflow.com/questions/24005774/sending-a-message-from-php-to-python-through-a-socket
Stack Overflow
Sending a message from PHP to Python through a socket
I'm trying to send a message to a Python socket using PHP and that it prints the message.

Here is the PHP code so far:

<?
$host = "localhost";
$port = 12345;

$f = socket_create(AF_INET, SOCK_...
Image
Eric — 03/03/2024 1:06 PM
Sure! Below is an example of how you can implement communication between a PHP script and a Python script using sockets. In this example, the PHP script acts as the client, sending data to the Python script, which acts as the server, receiving the data and performing some processing.

PHP client script (client.php):
<?php

$host = '127.0.0.1';
$port = 12345;

// Create a TCP/IP socket
$socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
if ($socket === false) {
    echo "Failed to create socket: " . socket_strerror(socket_last_error()) . "\n";
    exit(1);
}

// Connect to the server
$result = socket_connect($socket, $host, $port);
if ($result === false) {
    echo "Failed to connect to server: " . socket_strerror(socket_last_error()) . "\n";
    exit(1);
}

// Send data to the server
$data = "Hello from PHP!";
socket_write($socket, $data, strlen($data));

// Receive response from the server
$response = socket_read($socket, 1024);
echo "Response from server: " . $response . "\n";

// Close the socket
socket_close($socket);

?>


Python server script (server.py):
import socket

HOST = '127.0.0.1'
PORT = 12345

# Create a TCP/IP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the address and port
server_socket.bind((HOST, PORT))

# Listen for incoming connections
server_socket.listen(1)
print(f'Server listening on {HOST}:{PORT}')

while True:
    # Accept a new connection
    client_socket, client_address = server_socket.accept()
    print(f'Connection from {client_address}')

    # Receive data from the client
    data = client_socket.recv(1024)
    if data:
        print(f'Received data: {data.decode()}')

        # Process the data (e.g., perform some computation)
        # In this example, just echo the received data back to the client
        response = f'Received: {data.decode()}'
        client_socket.sendall(response.encode())

    # Close the client socket
    client_socket.close()


To run this example:

Save the PHP client script as client.php.
Save the Python server script as server.py.
Start the Python server script by running python server.py in a terminal.
Run the PHP client script by accessing http://localhost/client.php in a web browser or executing php client.php in a terminal.

This example demonstrates a simple communication between a PHP client and a Python server using sockets. You can extend and modify it to suit your specific requirements and use case.
Jesse — 03/03/2024 1:14 PM
crenshaw-picklops
Grant — 03/03/2024 1:14 PM
gtkachyk
Eric — 03/03/2024 1:14 PM
E-Gantz
Prat — 03/03/2024 1:14 PM
itzbrownboi
Floor — 03/03/2024 1:20 PM
To do:
Python socket program (listener) - Get messages from other servers
Python socket program (sender) - Await orders from php Socket. Wait for changes and send to other servers
PHP socket program sends to the sender Python socket program
Send query string and variables?
Alter mysql statements to forward statements to Python Script
HAProxy setup
 
Floor — 03/03/2024 1:42 PM
To do:
Python socket program (listener) - Get messages from other servers
Has port 9001
Assigned: Joanne
Python socket program (sender) - Await orders from php Socket. Wait for changes and send to other servers
Has port 9000
Assigned: Jesse
PHP socket program sends to the sender Python socket program
Has port: 9002
Alter mysql statements to forward statements to Python Script
Assigned: Grant
HAProxy setup (If possible)
Assigned: Eric
Help Someone with Lots of Work
Assigned: Prat
 
General Message format for sockets:
Msg: Send query string but replaces $ with % and input variables for query
e.g. """INSERT INTO Laptop (Id, Name, Price, Purchase_date) 
          VALUES (15, 'Lenovo ThinkPad P71', 6459, '2019-08-14') """
If see ? then replace with variable
 
Eric — 03/04/2024 3:33 PM
So something to note: C4 from the notes on consistency satisfies both coherence and P-Ram but not SC, and he kind of hinted that an exam question might be to find something that fits that description. he showed proving each part of that in class as well.
Image
just in case it actually is on the exam
Floor — 03/04/2024 4:22 PM
Yo thanks, I completely missed that
Grant — Yesterday at 3:17 PM
Where do you all want to meet?
Floor — Yesterday at 3:18 PM
Hmm
Not sure, maybe math science. It’s a little noisy in Eng rn
Jesse — Yesterday at 3:20 PM
Sure, MS works.
@Floor  We’re in MS on the side w/ tables.
Jesse — Yesterday at 4:20 PM
import socket
import sys
from threading import Thread
from queue import Queue
import mysql.connector

Expand
spoofy_rep_send.py
5 KB
Grant — Yesterday at 4:29 PM
import socket

# Set the host and port for the server
host = '127.0.0.1'  # Change this to the desired IP address or use 'localhost'
port = 9000  # Change this to the desired port number

Expand
php_python_communication_test.py
1 KB
<?php
include "modules/menubar.php";
include "modules/mysql_connect.php";
include "modules/python_connect.php";

if(!isset($_SESSION)) { session_start(); }
Expand
index.php
2 KB
<?php

$host = '127.0.0.1';
$port = 9000;

// Create a TCP/IP socket
Expand
python_connect.php
1 KB
Eric — Today at 10:35 AM
got HAProxy working after some futzing, just using this as the config rn
Attachment file type: unknown
haproxy.cfg
345 bytes
oh and i used this guide, pretty easy cheesy https://www.haproxy.com/blog/haproxy-configuration-basics-load-balance-your-servers
HAProxy Technologies
HAProxy Configuration Basics: Load Balance Your Servers
If you’re new to using the HAProxy load balancer, you’re at the right place. In this blog post, you’ll learn how to configure HAProxy for basic load balancing.
HAProxy Configuration Basics: Load Balance Your Servers
Grant — Today at 10:41 AM
Added a proof of concept for sending formatted sql queries from php to python. Pull from the repo and check out edit_artist.php
Jesse — Today at 10:44 AM
I’ll pull this and test it against what I have. @Grant  and @Floor , do you want to meet tonight for a bit and go through what we have so far?
Floor — Today at 10:44 AM
Sure! Are we thinking 7pm?
Jesse — Today at 10:46 AM
8 would be better but if 7 only works for you guys I can do that.
Floor — Today at 10:47 AM
I can also do 8pm
Grant — Today at 10:53 AM
8 sounds good
Eric — Today at 11:08 AM
think i'm going to set up the proxy to access each server based on port, which is shown in the guide. That way we can access a specific server for the demo if we need to show anything (like changes being propagated) without having to like spam reload to get the server we want based on round robin. Then we can switch it back to round robin later once we don't need to show things on a specific server
or i guess we would just access the server directly bypassing the proxy, and leave the proxy as is so we can show fault tolerance later? not sure
Jesse — Today at 11:40 AM
I think it might be best to leave the proxy out for now and then show it for the fault tolerance demo.
Jesse — Today at 4:30 PM
@Eric  I wanted to confirm something. On the website, when you 'Add a song' there's no actual uploading of a music file happening. You're just inserting the local file path to the song in the database. 
Eric — Today at 4:30 PM
correct, the DB just has file paths
Jesse — Today at 4:31 PM
OK thanks. Just wanted to check to see if my program should be listening for a bunch of data (that contains a file) or just the MySQL statement.
@Floor we should only just have to listen for a small message then, no need to do a for loop continually listening for more data.
Eric — Today at 4:31 PM
we may have to send the data otherwise the server cant play it
Jesse — Today at 4:32 PM
That would be something separate then I suppose. Send the query and then send the song file.
Maybe let's put that on the "nice-to-have" pile for now.
Grant — Today at 8:15 PM
Image
Jesse — Today at 8:52 PM
<?php
include "../modules/menubar.php";
include "../modules/mysql_connect.php";
require_once("../modules/python_connect.php"); // Make python_connect.php a requirement to run this file


if(!isset($_SESSION)) { session_start(); }
if (isset($_SESSION["LoggedIn"]) && $_SESSION["LoggedIn"] && $_SESSION["Admin"]) {

	// @todo: This throws a php notice if POST is called, as GET has no ArtistID index
	$ArtistID = $_GET["ArtistID"];

	$prepare = mysqli_prepare($con, "SELECT * FROM ARTIST WHERE ArtistID=?");
	$prepare -> bind_param("s", $ArtistID);
	$prepare -> execute();
	$result = $prepare -> get_result();
	$row = mysqli_fetch_array($result);

	//set default values
	$nameDef = $row["Name"];
	$aboutDef = $row["About"];
	$pfpDef = $row["ProfilePicture"];
	$bpDef = $row["BannerPicture"];

	// Define variables and initialize with empty values
	$error_string = "";
	$name = "";
	$about = "";
	$pfp = "";
	$bp = "";

	// Processing form data when form is submitted
	if($_SERVER["REQUEST_METHOD"] == "POST"){

		$ArtistID = trim($_POST["ArtistID"]);

		// Validate title
		$name = trim($_POST["name"]);
		if(empty($name)) {
			$error_string = "Name can't be empty.";
		}
		
		// Validate about section
		// TODO: Actual validation checks
		$about = trim($_POST["about"]);
		
		// Validate profile picture path
		// TODO: Actual validation checks
		$pfp = trim($_POST["pfp"]);
		
		// Validate banner picture path
		// TODO: Actual validation checks
		$bp = trim($_POST["bp"]);
		
		

		// If there are no errors, insert into the database
		if(empty($error_string)) {

			// ************************************************************************************************************************************************************************************
			// ************************************************************************************************************************************************************************************
			// ************************************************************************************************************************************************************************************
			// Proof of concept: 
			// - Sends fully prepared SQL queries to Replication/php_python_communication_test.py
			// - To run:
			// 		- Run Replication/php_python_communication_test.py.
			// 		- login as admin, select 'manage music', select 'manage artists', click 'edit' on any artist, then click 'submit'. 
			//		- Output will be displayed in the terminal running Replication/php_python_communication_test.py.
			$sql_test = "UPDATE ARTIST SET Name='$name', About='$about', ProfilePicture='$pfp', BannerPicture='$bp' WHERE ArtistID=$ArtistID";
			// socket_write($socket, $sql_test, strlen($sql_test));
			// $response = socket_read($socket, 1024);
			// socket_close($socket);
			sendStmnt($sql_test);
			// End proof of concept			// ************************************************************************************************************************************************************************************
			// ************************************************************************************************************************************************************************************
			// ************************************************************************************************************************************************************************************
			
			// // Prepare an insert statement
			// $sql = "UPDATE ARTIST SET Name=?, About=?, ProfilePicture=?, BannerPicture=? WHERE ArtistID=?";
			// $prepare = mysqli_prepare($con, $sql);
			// if($prepare) {
				
			// 	// Bind all values
			// 	$prepare -> bind_param("sssss", $name, $about, $pfp, $bp, $ArtistID);
			// 	$prepare -> execute();
			// 	$result = $prepare -> get_result();
				
				// Redirect to login page after registering
				header("location: manage_artists.php");
				$prepare -> close();
			// }
		}
		
		// Close connection
		mysqli_close($con);
	}
} else {
	header("location: ../error.php");
}
?>
... (44 lines left)
Collapse
edit_artist.php
6 KB
<?php

// $host = '127.0.0.1';
// $port = 9000;
// $disconnect = 'disconnect'


function sendStmnt($stmnt){

    $socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
    if ($socket === false) {
        echo "Failed to create socket: " . socket_strerror(socket_last_error()) . "\n";
        exit(1);
    }

    $result = socket_connect($socket, '127.0.0.1', 9000);
    if ($result === false) {
        echo "Failed to connect to server: " . socket_strerror(socket_last_error()) . "\n";
        exit(1);
    }

    socket_write($socket, $stmnt, strlen($stmnt));
    socket_close($socket);
}

// Create a TCP/IP socket
// $socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
// if ($socket === false) {
//     echo "Failed to create socket: " . socket_strerror(socket_last_error()) . "\n";
//     exit(1);
// }

// // Connect to the server
// $result = socket_connect($socket, $host, $port);
// if ($result === false) {
//     echo "Failed to connect to server: " . socket_strerror(socket_last_error()) . "\n";
//     exit(1);
// }

// Send data to the server
// $data = "Hello from PHP!";
// socket_write($socket, $data, strlen($data));

// Receive response from the server
// $response = socket_read($socket, 1024);
// echo "Response from server: " . $response . "\n";

// Close the socket
// socket_close($socket);

?>
Collapse
python_connect.php
2 KB
﻿
<?php

// $host = '127.0.0.1';
// $port = 9000;
// $disconnect = 'disconnect'


function sendStmnt($stmnt){

    $socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
    if ($socket === false) {
        echo "Failed to create socket: " . socket_strerror(socket_last_error()) . "\n";
        exit(1);
    }

    $result = socket_connect($socket, '127.0.0.1', 9000);
    if ($result === false) {
        echo "Failed to connect to server: " . socket_strerror(socket_last_error()) . "\n";
        exit(1);
    }

    socket_write($socket, $stmnt, strlen($stmnt));
    socket_close($socket);
}

// Create a TCP/IP socket
// $socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
// if ($socket === false) {
//     echo "Failed to create socket: " . socket_strerror(socket_last_error()) . "\n";
//     exit(1);
// }

// // Connect to the server
// $result = socket_connect($socket, $host, $port);
// if ($result === false) {
//     echo "Failed to connect to server: " . socket_strerror(socket_last_error()) . "\n";
//     exit(1);
// }

// Send data to the server
// $data = "Hello from PHP!";
// socket_write($socket, $data, strlen($data));

// Receive response from the server
// $response = socket_read($socket, 1024);
// echo "Response from server: " . $response . "\n";

// Close the socket
// socket_close($socket);

?>
python_connect.php
2 KB