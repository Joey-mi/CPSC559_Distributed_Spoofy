<?php
/* 
Include this file at the top of your PHP whenever you wish to connect to mysql
It will set the variable $con to be the mysql connection
Don't forget to close the mysql connection when you are done using it!
*/ 
require __DIR__ . '/../../vendor/autoload.php';

Dotenv\Dotenv::createUnsafeImmutable(__DIR__ . '/../../')->load();

// Create connection
$con = mysqli_connect($_ENV['DB_Host'], $_ENV['DB_User'], $_ENV['DB_Pass'], $_ENV['DB_Name']);

// Check connection
if (!$con) {
    $msg = "Connection to MySQL failed: " . mysqli_connect_error();
    echo "<p>".$msg."</p>";
    die($msg);
}
?>
