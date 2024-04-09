<?php
include "../modules/mysql_connect.php";
include "../modules/menubar.php";
require_once("../modules/python_connect.php");

if(!isset($_SESSION)) { session_start(); }
if (isset($_SESSION["LoggedIn"]) && $_SESSION["LoggedIn"] && $_SESSION["Admin"]) {
	if($_SERVER["REQUEST_METHOD"] == "POST"){
		$SongID = $_POST["SongID"];
		$AlbumID = $_POST["AlbumID"];

		$sql = "INSERT INTO ALBUM_CONTAINS VALUES($AlbumID, $SongID)";
		sendQuery($sql);
		header("Refresh:0; url=manage_songs.php");
	}
} else {
    header("location: ../error.php");
}
?>
<html>
    <head>
	<link href="/styles/style.css" rel="stylesheet" />
        <title>Add Song to Album - Spoofy</title>
    </head>
    <body>
        <h1>Add Song to Album</h1>
        <form action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]); ?>" method="post">
            <div class="form-group">
                <label>SongID</label>
                <input type="text" name="SongID" class="form-control">
            </div>   
            <div class="form-group">
                <label>AlbumID</label>
                <input type="text" name="AlbumID" class="form-control">
            </div>
            <div class="form-group">
                <input type="submit" class="submitForm" value="Add to Album">
            </div>
			<button onclick='location.href="manage_songs.php"' type='button'>
				Return to Manage Songs
			</button><br>
        </form>
		<?php
		
		echo "<table><tr><td>";

		echo "<h3>Songs:</h3>";
		$result = mysqli_query($con, "SELECT SongID, Title FROM SONG");
		echo "<table border='1'>
		<th>ID</th>
		<th>Title</th>
		<th>Album</th>
		</tr>";

		while($row = mysqli_fetch_array($result)) {
			echo "<tr>
			<td>" . $row['SongID'] . "</td>
			<td>" . $row['Title'] . "</td>";

			$prepare = mysqli_prepare($con, "SELECT Title FROM ALBUM, ALBUM_CONTAINS WHERE ALBUM.AlbumID = ALBUM_CONTAINS.AlbumID AND ALBUM_CONTAINS.SongID = ?");
			$prepare -> bind_param("s", $row['SongID']);
			$prepare -> execute();
			$album_result = $prepare -> get_result();
			if (mysqli_num_rows($album_result) == 0) { echo "<td></td>"; }
			else { echo "<td>".mysqli_fetch_array($album_result)["Title"]."</td>"; }

			echo "</tr>";
		}
		echo "</table>";

		echo "</td><td>";
		
		echo "<h3>Albums:</h3>";
		
		$result2 = mysqli_query($con, "SELECT * FROM Album");
		echo "<table border='1'>
		<th>ID</th>
		<th>Title</th>
		</tr>";

		while($row2 = mysqli_fetch_array($result2)) {
			echo "<tr>
			<td>" . $row2['AlbumID'] . "</td>
			<td>" . $row2['Title'] . "</td>";
			
			"</tr>";
		}
		echo "</table>";

		echo "</td></tr></table>";
		
		mysqli_close($con);
		?>
    </body>
</html>
