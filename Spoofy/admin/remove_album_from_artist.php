<!-- @todo: We can turn this into an actual button at some point instead of a hyperlink -->
<?php
include "../modules/mysql_connect.php";
require_once("../modules/python_connect.php");

if(!isset($_SESSION)) { session_start(); }
if (isset($_SESSION["LoggedIn"]) && $_SESSION["LoggedIn"] && $_SESSION["Admin"]) {
    $ArtistID = $_GET["ArtistID"];
	$AlbumID = $_GET["AlbumID"];
	$ArtistName = $_GET["ArtistName"];
    $sql = "DELETE FROM HAS WHERE ArtistID=$ArtistID AND AlbumID=$AlbumID";
    sendQuery($sql);
    // $sql = "DELETE FROM HAS WHERE ArtistID=? AND AlbumID=?";
    // $prepare = mysqli_prepare($con, $sql);
    // if ($prepare) {
    //     $prepare -> bind_param("ss", $ArtistID, $AlbumID);
    //     $prepare -> execute();
    // }
    if ($prepare) {
        $prepare -> close();
    }
    header("location: remove_has.php?ArtistID=" . $ArtistID . "&ArtistName=" . $ArtistName . "");
} else {
    header("location: ../error.php");
}
?>
