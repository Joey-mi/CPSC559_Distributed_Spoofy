<!-- @todo: We can turn this into an actual button at some point instead of a hyperlink -->
<?php
include "../modules/mysql_connect.php";
require_once("../modules/python_connect.php");

if(!isset($_SESSION)) { session_start(); }
if (isset($_SESSION["LoggedIn"]) && $_SESSION["LoggedIn"] && $_SESSION["Admin"]) {
    $SongID = $_GET["SongID"];
	$AlbumID = $_GET["AlbumID"];
    $sql = "DELETE FROM ALBUM_CONTAINS WHERE SongID=$SongID AND AlbumID=$AlbumID";
    sendQuery($sql);
    header("Refresh:0; url=remove_album_contains.php?AlbumID=" . $AlbumID . "");
} else {
    header("location: ../error.php");
}
?>
