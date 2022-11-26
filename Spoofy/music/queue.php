<?php
include "../modules/mysql_connect.php";

// Title
echo "<h1>Music Queue</h1>";

if(!isset($_SESSION)) { session_start(); }
$numSongs = (!isset($_SESSION["Queue"]) || $_SESSION["Queue"] == null) ? 0 : count($_SESSION["Queue"]);

// Handle button presses for individual indices
for ($i = 0; $i < $numSongs; $i++) {
    if (array_key_exists("Play".$i, $_POST)) {
        $_SESSION["SongIndex"] = $i;
    } else if (array_key_exists("Remove".$i, $_POST)) {
        if ($_SESSION["SongIndex"] > $i) { $_SESSION["SongIndex"]--; }
        unset($_SESSION["Queue"][$i]);
        $_SESSION["Queue"] = array_values($_SESSION["Queue"]);  // https://stackoverflow.com/a/369761

        if (count($_SESSION["Queue"]) == 0) { $_SESSION["Queue"] = null; }
        else if ($_SESSION["SongIndex"] >= count($_SESSION["Queue"])) { $_SESSION["SongIndex"] = count($_SESSION["Queue"]) - 1; }
    }
}
include "../modules/menubar.php";

// Do this again after menubar, clearing the queue in menubar can do weird stuff
$numSongs = (!isset($_SESSION["Queue"]) || $_SESSION["Queue"] == null) ? 0 : count($_SESSION["Queue"]);

// Display song information
if ($numSongs > 0) {
    echo "<table border='1'>
    <tr>
    <th>Title</th>
    <th>Duration</th>
    </tr>";

    for ($i = 0; $i < $numSongs; $i++) {
        // Get the songs information
        $songID = $_SESSION["Queue"][$i];
        $prepare = mysqli_prepare($con, "SELECT * FROM SONG WHERE SongID=?");
        $prepare -> bind_param("s", $songID);
        $prepare -> execute();
        $result = $prepare -> get_result();
        $row = mysqli_fetch_array($result);
        echo "<tr>";

        // Bold the title if it is currently playing
        echo $i == $_SESSION["SongIndex"] ? "<td><b>" . $row['Title'] . "</b></td>" : "<td>" . $row['Title'] . "</td>";
        echo "<td>" . $row['Duration'] . "</td>
        <td><a href='/music/song.php?SongID= " . $row['SongID'] . "'>View</a></td>
        <td>
            <form method=\"post\">
                <input type=\"submit\" name=\"Play".$i."\" class=\"button\" value=\"Play\" />
            </form>
        </td>
        <td>
            <form method=\"post\">
                <input type=\"submit\" name=\"Remove".$i."\" class=\"button\" value=\"Remove\" />
            </form>
        </td>
        </tr>";
    }
    echo "</table>";

    // Display shuffle and clear buttons, these call 'POST' and are handled when menubar is included
    echo "
    <form method=\"post\">
        <input type=\"submit\" name=\"ClearQueue\" class=\"button\" value=\"Clear Queue\" />
        <input type=\"submit\" name=\"Shuffle\" class=\"button\" value=\"Shuffle Queue\" />
    </form>";
} else {
    echo "<h3>No songs playing.</h3>";
}
?>

<html>
    <head>
        <title>Queue - Spoofy</title>
    </head>
</html>