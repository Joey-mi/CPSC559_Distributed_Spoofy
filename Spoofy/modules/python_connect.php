<?php

$host = '127.0.0.1';
$port = 9000;

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

?>