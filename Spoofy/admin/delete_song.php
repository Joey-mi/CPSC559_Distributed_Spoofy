<?php
include "../modules/mysql_connect.php";
require_once("../modules/python_connect.php");

if(!isset($_SESSION)) { session_start(); }
if (isset($_SESSION["LoggedIn"]) && $_SESSION["LoggedIn"] && $_SESSION["Admin"]) {
    $ID = $_GET["SongID"];
    $sql = "DELETE FROM SONG WHERE SongID=$ID";
    sendQuery($sql);
    // $sql = "DELETE FROM SONG WHERE SongID=?";
    // $prepare = mysqli_prepare($con, $sql);
    // if ($prepare) {
    //     $prepare -> bind_param("s", $ID);
    //     $prepare -> execute();
    // }
    if ($prepare) {
        $prepare -> close();
    }
    header("location: manage_songs.php");
} else {
    header("location: ../error.php");
}
?>
