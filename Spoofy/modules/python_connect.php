<?php

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

?>