<!-- @todo: We can turn this into an actual button at some point instead of a hyperlink -->
<?php
include "../modules/mysql_connect.php";
require_once("../modules/python_connect.php");

if(!isset($_SESSION)) { session_start(); }
if (isset($_SESSION["LoggedIn"]) && $_SESSION["LoggedIn"] && $_SESSION["Admin"]) {
    $ID = $_GET["UserID"];
    $sql = "DELETE FROM USER WHERE UserID=$ID";
    sendQuery($sql);
    header("Refresh:0; url=manage_users.php");
} else {
    header("location: ../error.php");
}
?>
