<?php
include "../modules/mysql_connect.php";
require_once("../modules/python_connect.php");

if(!isset($_SESSION)) { session_start(); }
if (isset($_SESSION["LoggedIn"]) && $_SESSION["LoggedIn"] && $_SESSION["Admin"]) {
    $ID = $_GET["AlbumID"];
    $sql = "DELETE FROM ALBUM WHERE AlbumID=$ID";
    sendQuery($sql);
    header("Refresh:0; url=manage_albums.php"); 
} else {
    header("location: ../error.php");
}
?>
