<?php
require_once("python_connect.php");
function create_playlist($con, $playlist_name, $userID) {
    // Replace single quotes with escape characters
	$playlist_name = str_replace("'", "\'", $playlist_name);

    $sql = "INSERT INTO PLAYLIST (PlaylistName, CreatorID) VALUES ('$playlist_name', $userID)";
    sendQuery($sql);
    // $prepare = mysqli_prepare($con, "INSERT INTO PLAYLIST (PlaylistName, CreatorID) VALUES (?, ?)");
    // $prepare -> bind_param("ss", $playlist_name, $userID);
    // $prepare -> execute();
    // $prepare -> close();
}

function delete_playlist($con, $playlistID) {
    $sql = "DELETE FROM PLAYLIST WHERE PlaylistID=$playlistID";
    sendQuery($sql);

    // // Get current URL
    // if(isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on')   
    //     $url = "https://";   
    // else  
    //     $url = "http://";   
    // // Append the host(domain name, ip) to the URL.   
    // $url.= $_SERVER['HTTP_HOST'];   

    // // Append the requested resource location to the URL   
    // $url.= $_SERVER['REQUEST_URI'];

    // echo $url;

    // header("Refresh:0; url=" + $url); 
    // $prepare = mysqli_prepare($con, "DELETE FROM PLAYLIST WHERE PlaylistID=?");
    // $prepare -> bind_param("s", $playlistID);
    // $prepare -> execute();
    // $prepare -> close();
}

function add_song($con, $playlistID, $songID) {
    $sql = "INSERT INTO PLAYLIST_CONTAINS (PlaylistID, SongID) VALUES ($playlistID, $songID)";
    sendQuery($sql);
    // $prepare = mysqli_prepare($con, "INSERT INTO PLAYLIST_CONTAINS (PlaylistID, SongID) VALUES (?, ?)");
    // $prepare -> bind_param("ss", $playlistID, $songID);
    // $prepare -> execute();
    // $prepare -> close();
}

function remove_song($con, $playlistID, $songID) {
    // Prevent a user from adding a song to a playlist that already contains it
    $prepare = mysqli_prepare($con, "SELECT * FROM PLAYLIST_CONTAINS WHERE PlaylistID=? AND SongID=?");
    $prepare -> bind_param("ss", $playlistID, $songID);
    $prepare -> execute();
    $result = $prepare -> get_result();
    $prepare -> close();
    if (mysqli_num_rows($result) > 0) { return; }

    $sql = "DELETE FROM PLAYLIST_CONTAINS WHERE PlaylistID=$playlistID AND SongID=$songID";
    sendQuery($sql);
    // $prepare = mysqli_prepare($con, "DELETE FROM PLAYLIST_CONTAINS WHERE PlaylistID=? AND SongID=?");
    // $prepare -> bind_param("ss", $playlistID, $songID);
    // $prepare -> execute();
    // $prepare -> close();
}

function play_playlist($con, $playlistID) {
    if(!isset($_SESSION)) { session_start(); }
    $prepare = mysqli_prepare($con, "SELECT SongID FROM PLAYLIST_CONTAINS WHERE PlaylistID=?");
    $prepare -> bind_param("s", $playlistID);
    $prepare -> execute();
    $result = $prepare -> get_result();
    $prepare -> close();

    if (mysqli_num_rows($result) == 0) { return; }
    $_SESSION["Queue"] = array();
    $_SESSION["SongIndex"] = 0;
    while($row = mysqli_fetch_array($result)) {
        array_push($_SESSION["Queue"], $row["SongID"]);
    }
}
?>
