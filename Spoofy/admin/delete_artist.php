<?php
include "../modules/mysql_connect.php";
require_once("../modules/python_connect.php");

if(!isset($_SESSION)) { session_start(); }
if (isset($_SESSION["LoggedIn"]) && $_SESSION["LoggedIn"] && $_SESSION["Admin"]) {
    $ID = $_GET["ArtistID"];
    $sql = "DELETE FROM ARTIST WHERE ArtistID=$ID";
    sendQuery($sql);
    header("Refresh:0; url=manage_artists.php");
} else {
    header("location: ../error.php");
}
?>
