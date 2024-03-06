<?php
include "modules/menubar.php";
include "modules/mysql_connect.php";

if(!isset($_SESSION)) { session_start(); }
$loggedIn = isset($_SESSION["LoggedIn"]) && $_SESSION["LoggedIn"];
echo '<img src="/assets/spoofylogo.png" class="center">';
if ($loggedIn) { 
    echo "<h1 class='centered_text'>Welcome ".$_SESSION["Username"]."!</h1>";
} else {
    echo "<h1 class='centered_text'>Welcome to Spoofy!</h1>";
}

$isPremium = array_key_exists("IsPremium", $_SESSION) && $_SESSION["IsPremium"];

if ($isPremium) {
    // Display songs
    $result = mysqli_query($con, "SELECT * FROM Song");
    echo "<h3 class='centered_text'>Your gateway to ".(string)mysqli_num_rows($result)." songs!</h3";
} else {
    // Display ads
    $result = mysqli_query($con, "SELECT * FROM Advertisement");
    echo "<h3 class='centered_text'>Your gateway to ".(string)mysqli_num_rows($result)." advertisements!</h3";
}

if (!$loggedIn) {
    echo "<p></p><a class='centered_text' href=\"/user/login.php\">Log In</a>
            <a class='centered_text' href=\"/user/register.php\">Register</a>";
}
?>

<html>
    <head>
    <link href="/styles/style.css" rel="stylesheet" />
        <title>CPSC 471 - Spoofy</title>
    </head>
</html>
