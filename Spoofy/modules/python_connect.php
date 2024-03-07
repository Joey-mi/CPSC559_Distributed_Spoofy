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