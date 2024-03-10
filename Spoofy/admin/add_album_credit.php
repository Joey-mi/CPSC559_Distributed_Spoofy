<?php
include "../modules/mysql_connect.php";
include "../modules/menubar.php";
require_once("../modules/python_connect.php");

if(!isset($_SESSION)) { session_start(); }
if (isset($_SESSION["LoggedIn"]) && $_SESSION["LoggedIn"] && $_SESSION["Admin"]) {
	if($_SERVER["REQUEST_METHOD"] == "POST"){
		$AlbumID = $_POST["AlbumID"];
		$ArtistID = $_POST["ArtistID"];

		$sql = "INSERT INTO HAS VALUES($AlbumID,$ArtistID)";
		sendQuery($sql);
		// $sql = "INSERT INTO HAS VALUES(?,?)";
		// $prepare = mysqli_prepare($con, $sql);
		if($prepare) {
			// // Bind all values
			// $prepare -> bind_param("ss", $AlbumID, $ArtistID);
			// $prepare -> execute();
			// $result = $prepare -> get_result();
			header("Refresh:0; url=manage_albums.php"); 
			// header("location: manage_albums.php");
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
        <title>Add Album Credit - Spoofy</title>
    </head>
    <body>
        <h1>Add Album Credit</h1>
        <form action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]); ?>" method="post">
            <div class="form-group">
                <label>AlbumID</label>
                <input type="text" name="AlbumID" class="form-control">
            </div>   
            <div class="form-group">
                <label>ArtistID</label>
                <input type="text" name="ArtistID" class="form-control">
            </div>
            <div class="form-group">
                <input type="submit" class="submitForm" value="Add Credit">
            </div>
			<button onclick='location.href="manage_albums.php"' type='button'>
				Return to Manage Albums
			</button><br>
        </form>
		<?php 
		echo "<table><tr><td>";

		echo "<h3>Albums:</h3>";
		
		$result = mysqli_query($con, "SELECT * FROM Album");
		echo "<table border='1'>
		<th>ID</th>
		<th>Title</th>
		<th>Artist</th>
		</tr>";

		while($row = mysqli_fetch_array($result)) {
			echo "<tr>
			<td>" . $row['AlbumID'] . "</td>
			<td>" . $row['Title'] . "</td>";

			$prepare = mysqli_prepare($con, "SELECT Name FROM ARTIST, HAS WHERE ARTIST.ArtistID = HAS.ArtistID AND HAS.AlbumID = ?");
			$prepare -> bind_param("s", $row['AlbumID']);
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
