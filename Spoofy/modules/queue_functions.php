<?php
require_once("../modules/python_connect.php");
function play_song($songID) {
    if(!isset($_SESSION)) { session_start(); }
    $_SESSION["Queue"] = array($songID);
    $_SESSION["SongIndex"] = 0;
}

function add_song_to_queue($songID) {
    if(!isset($_SESSION)) { session_start(); }
    if ($_SESSION["Queue"] == null) {
        $_SESSION["Queue"] = array();
        $_SESSION["SongIndex"] = 0;
    }
    array_push($_SESSION["Queue"], $songID);
}

function play_album($con, $albumID) {
    if(!isset($_SESSION)) { session_start(); }

    // Clear the current queue, put each song from the album into the queue
    $_SESSION["Queue"] = array();
    $_SESSION["SongIndex"] = 0;

    // Get all song IDs in this album
    $prepare = mysqli_prepare($con, "SELECT SongID FROM ALBUM_CONTAINS WHERE AlbumID=?");
    $prepare -> bind_param("s", $albumID);
    $prepare -> execute();
    $result = $prepare -> get_result();
    while ($row = mysqli_fetch_array($result)) {
        array_push($_SESSION["Queue"], $row["SongID"]);
    }
    if (count($_SESSION["Queue"]) == 0) { $_SESSION["Queue"] = null; }
    else {
        increment_song_plays($con, $_SESSION["Queue"][0]);
    }
    $prepare -> close();
}

function increment_song_plays($con, $songID) {
    // This cannot go in play_song due to ads
    $sql = "UPDATE SONG SET TotalPlays = TotalPlays + 1, MonthlyPlays = MonthlyPlays + 1 WHERE SongID=?";
    $prepare = mysqli_prepare($con, $sql);
    $prepare -> bind_param("s", $songID);
    $prepare -> execute();

    $sql = "UPDATE ARTIST SET TotalPlays = TotalPlays + 1, MonthlyPlays = MonthlyPlays + 1 
            WHERE ArtistID IN (
            SELECT ArtistID FROM WRITES WHERE SongID=$songID
            )";
    sendQuery($sql);
    // $sql = "UPDATE ARTIST SET TotalPlays = TotalPlays + 1, MonthlyPlays = MonthlyPlays + 1 
    //         WHERE ArtistID IN (
    //             SELECT ArtistID FROM WRITES WHERE SongID=?
    //         )";
    // $prepare = mysqli_prepare($con, $sql);
    // $prepare -> bind_param("s", $songID);
    // $prepare -> execute();
    if($prepare){
        $prepare -> close();
    }
}

/* Notes:
 - play_playlist is handled in playlist_functions.php
 - play_song and add_song_to_queue work identically for ads
*/
?>
