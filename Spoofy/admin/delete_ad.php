<?php
include "../modules/mysql_connect.php";
require_once("../modules/python_connect.php");

if(!isset($_SESSION)) { session_start(); }
if (isset($_SESSION["LoggedIn"]) && $_SESSION["LoggedIn"] && $_SESSION["Admin"]) {
    $ID = $_GET["AdID"];
    $sql = "DELETE FROM ADVERTISEMENT WHERE AdID=$ID";
    sendQuery($sql);
    // $sql = "DELETE FROM ADVERTISEMENT WHERE AdID=?";
    // $prepare = mysqli_prepare($con, $sql);
    // if ($prepare) {
    //     $prepare -> bind_param("s", $ID);
    //     $prepare -> execute();
    // }
    if ($prepare) {
        $prepare -> close();
    }
    header("Refresh:0; url=manage_ads.php");
    // header("location: manage_ads.php");
} else {
    header("location: ../error.php");
}
?>
