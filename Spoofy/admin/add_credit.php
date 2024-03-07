<?php
include "../modules/mysql_connect.php";
include "../modules/menubar.php";
require_once("../modules/python_connect.php");

if(!isset($_SESSION)) { session_start(); }
if (isset($_SESSION["LoggedIn"]) && $_SESSION["LoggedIn"] && $_SESSION["Admin"]) {
	if($_SERVER["REQUEST_METHOD"] == "POST"){
		$SongID = $_POST["SongID"];
		$ArtistID = $_POST["ArtistID"];

		$sql = "INSERT INTO WRITES VALUES($SongID, $ArtistID)";
		sendQuery($sql);
		// $sql = "INSERT INTO WRITES VALUES(?,?)";
		// $prepare = mysqli_prepare($con, $sql);
		if($prepare) {
			// // Bind all values
			// $prepare -> bind_param("ss", $SongID, $ArtistID);
			// $prepare -> execute();
			// $result = $prepare -> get_result();
			
			header("location: manage_songs.php");
			$prepare -> close();
		}
	}
} else {
    header("location: ../error.php");
}
?>
<html>
    <head>
	      <link href="/styles/style.css" rel="stylesheet" />
        <title>Add Artist Credit - Spoofy</title>
    </head>
    <body>
        <h1>Add Artist Credit</h1>
        <form action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]); ?>" method="post">
            <div class="form-group">
                <label>SongID</label>
                <input type="text" name="SongID" class="form-control">
            </div>   
            <div class="form-group">
                <label>ArtistID</label>
                <input type="text" name="ArtistID" class="form-control">
            </div>
            <div class="form-group">
                <input type="submit" class="submitForm" value="Add Credit">
            </div>
			<button onclick='location.href="manage_songs.php"' type='button'>
				Return to Manage Songs
			</button><br>
        </form>
		<?php 
		
		echo "<table><tr><td>";
		echo "<h3>Songs:</h3>";
		
		$result = mysqli_query($con, "SELECT * FROM Song");
		echo "<table border='1'>
		<th>ID</th>
		<th>Title</th>
		<th>Artist</th>
		</tr>";

		while($row = mysqli_fetch_array($result)) {
			echo "<tr>
			<td>" . $row['SongID'] . "</td>
			<td>" . $row['Title'] . "</td>";

			$prepare = mysqli_prepare($con, "SELECT Name FROM ARTIST, WRITES WHERE ARTIST.ArtistID = WRITES.ArtistID AND WRITES.SongID = ?");
			$prepare -> bind_param("s", $row['SongID']);
			$prepare -> execute();
			$artist = $prepare -> get_result();
			if (mysqli_num_rows($artist) == 0) { echo "<td></td>"; }
			else { echo "<td>".mysqli_fetch_array($artist)["Name"]."</td>"; }
			
			echo "</tr>";
		}
		echo "</table>";

		echo "</td><td>";
		
		echo "<h3>Artists:</h3>";
		
		$result2 = mysqli_query($con, "SELECT * FROM Artist");
		echo "<table border='1'>
		<th>ID</th>
		<th>Name</th>
		</tr>";

		while($row2 = mysqli_fetch_array($result2)) {
			echo "<tr>
			<td>" . $row2['ArtistID'] . "</td>
			<td>" . $row2['Name'] . "</td>";
			
			"</tr>";
		}
		echo "</table>";

		echo "</td></tr></table>";
		
		mysqli_close($con);
		?>
    </body>
</html>
