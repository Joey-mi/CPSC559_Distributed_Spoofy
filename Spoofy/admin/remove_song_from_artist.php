<!-- @todo: We can turn this into an actual button at some point instead of a hyperlink -->
<?php
include "../modules/mysql_connect.php";
require_once("../modules/python_connect.php");

if(!isset($_SESSION)) { session_start(); }
if (isset($_SESSION["LoggedIn"]) && $_SESSION["LoggedIn"] && $_SESSION["Admin"]) {
    $SongID = $_GET["SongID"];
	$ArtistID = $_GET["ArtistID"];
	$ArtistName = $_GET["ArtistName"];
    $sql = "DELETE FROM WRITES WHERE SongID=$SongID AND ArtistID=$ArtistID";
    sendQuery($sql);
    header("Refresh:0; url=remove_has.php?ArtistID=" . $ArtistID . "&ArtistName=" . $ArtistName . "");
} else {
    header("location: ../error.php");
}
?>
