<?php
include "../modules/menubar.php";
include "../modules/mysql_connect.php";
// include "../modules/python_connect.php";


if(!isset($_SESSION)) { session_start(); }
if (isset($_SESSION["LoggedIn"]) && $_SESSION["LoggedIn"] && $_SESSION["Admin"]) {

	// Create a TCP/IP socket
	$host = '127.0.0.1';
	$port = 9000;
	$socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
	if ($socket === false) {
	    echo "Failed to create socket: " . socket_strerror(socket_last_error()) . "\n";
	    exit(1);
	}
	$result = socket_connect($socket, $host, $port);
	if ($result === false) {
	    echo "Failed to connect to server: " . socket_strerror(socket_last_error()) . "\n";
	    exit(1);
	}

	// @todo: This throws a php notice if POST is called, as GET has no ArtistID index
	$ArtistID = $_GET["ArtistID"];

	$prepare = mysqli_prepare($con, "SELECT * FROM ARTIST WHERE ArtistID=?");
	$prepare -> bind_param("s", $ArtistID);
	$prepare -> execute();
	$result = $prepare -> get_result();
	$row = mysqli_fetch_array($result);

	//set default values
	$nameDef = $row["Name"];
	$aboutDef = $row["About"];
	$pfpDef = $row["ProfilePicture"];
	$bpDef = $row["BannerPicture"];

	// Define variables and initialize with empty values
	$error_string = "";
	$name = "";
	$about = "";
	$pfp = "";
	$bp = "";

	// Processing form data when form is submitted
	if($_SERVER["REQUEST_METHOD"] == "POST"){

		$ArtistID = trim($_POST["ArtistID"]);

		// Validate title
		$name = trim($_POST["name"]);
		if(empty($name)) {
			$error_string = "Name can't be empty.";
		}
		
		// Validate about section
		// TODO: Actual validation checks
		$about = trim($_POST["about"]);
		
		// Validate profile picture path
		// TODO: Actual validation checks
		$pfp = trim($_POST["pfp"]);
		
		// Validate banner picture path
		// TODO: Actual validation checks
		$bp = trim($_POST["bp"]);
		
		

		// If there are no errors, insert into the database
		if(empty($error_string)) {
			
			// Prepare an insert statement
			$sql = "UPDATE ARTIST SET Name=?, About=?, ProfilePicture=?, BannerPicture=? WHERE ArtistID=?";

			// Send data to the server
			$data = $sql;
			socket_write($socket, $data, strlen($data));
			$response = socket_read($socket, 1024);
			socket_close($socket);

			$prepare = mysqli_prepare($con, $sql);
			if($prepare) {
				
				// Bind all values
				$prepare -> bind_param("sssss", $name, $about, $pfp, $bp, $ArtistID);
				$prepare -> execute();
				$result = $prepare -> get_result();
				
				// Redirect to login page after registering
				header("location: manage_artists.php");
				$prepare -> close();
			}
		}
		
		// Close connection
		mysqli_close($con);
	}
} else {
	header("location: ../error.php");
}
?>

<html>
    <head>
	      <link href="/styles/style.css" rel="stylesheet" />
        <title>Edit Artist - Spoofy</title>
    </head>
    <body>
        <div class="wrapper">
        <h2>Edit Artist</h2>
        <p>Update artist information:</p>
            <form action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]); ?>" method="post">
			    <div class="form-group">
                    <label>Artist ID</label>
					<input type="text" name="ArtistID" class="form-control" value="<?php echo $ArtistID; ?>" readonly>
                </div>
                <div class="form-group">
                    <label>Artist Name</label>
                    <input type="text" name="name" class="form-control" value="<?php echo $nameDef; ?>">
                </div>
				<label for="about">About</label>
                <div class="form-group">
					<textarea name="about" rows="4" cols="80"><?php echo $aboutDef; ?></textarea>
                </div>
                <div class="form-group">
                    <label>Path to Profile Picture</label>
                    <input type="text" name="pfp" size=128 class="form-control" value="<?php echo $pfpDef; ?>">
                </div>
				<div class="form-group">
                    <label>Path to Banner Picture</label>
                    <input type="text" name="bp" size=128 class="form-control" value="<?php echo $bpDef; ?>">
                </div>
                <div class="form-group">
                    <input type="submit" class="submitForm" value="Submit">
                    <input type="reset" class="btn btn-secondary ml-2" value="Reset">
                </div>
                <?php if ($error_string) echo "<p style=\"color:red;\">".$error_string."</p>";?>
				<button onclick='location.href="manage_artists.php"' type='button'>
					Return to Manage Artists
				</button><br>
            </form>
        </div>
    </body>
</html>
