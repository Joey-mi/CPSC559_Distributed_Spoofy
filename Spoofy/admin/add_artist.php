<?php
include "../modules/menubar.php";
include "../modules/mysql_connect.php";
require_once("../modules/python_connect.php");

if(!isset($_SESSION)) { session_start(); }
if (isset($_SESSION["LoggedIn"]) && $_SESSION["LoggedIn"] && $_SESSION["Admin"]){

	// Define variables and initialize with empty values
	$error_string = "";
	$name = "";
	$about = "";
	$pfp = "";
	$bp = "";

	// Processing form data when form is submitted
	if($_SERVER["REQUEST_METHOD"] == "POST"){

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

			// Replace single quotes with escape characters
			$name = str_replace("'", "\'", $name);
			$about = str_replace("'", "\'", $about);
			$pfp = str_replace("'", "\'", $pfp);
			$bp = str_replace("'", "\'", $bp);
			
			// Prepare an insert statement
			$sql = "INSERT INTO ARTIST (Name, About, ProfilePicture, BannerPicture, TotalPlays, MonthlyPlays) VALUES ('$name', '$about', '$pfp', '$bp', 0, 0)";
			sendQuery($sql);
			// $sql = "INSERT INTO ARTIST (Name, About, ProfilePicture, BannerPicture, TotalPlays, MonthlyPlays) VALUES (?, ?, ?, ?, 0, 0)";
			// $prepare = mysqli_prepare($con, $sql);
			if($prepare) {
				
				// // Bind all values
				// $prepare -> bind_param("ssss", $name, $about, $pfp, $bp);
				// $prepare -> execute();
				// $result = $prepare -> get_result();
				
				// Redirect to login page after registering
				header("Refresh:0; url=manage_artists.php"); 
				// header("location: manage_artists.php");
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
        <title>Add Artist - Spoofy</title>
    </head>
    <body>
        <div class="wrapper">
        <h2>Add an Artist</h2>
        <p>Fill in artist information:</p>
            <form action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]); ?>" method="post">
                <div class="form-group">
                    <label>Artist Name</label>
                    <input type="text" name="name" class="form-control" value="<?php echo $name; ?>">
                </div>
				<label for="about">About</label>
                <div class="form-group">
					<textarea name="about" rows="4" cols="80"><?php echo $about; ?></textarea>
                </div>
                <div class="form-group">
                    <label>Path to Profile Picture</label>
                    <input type="text" name="pfp" class="form-control" placeholder="profiles/<artist>.png" value="<?php echo $pfp; ?>">
                </div>
				<div class="form-group">
                    <label>Path to Banner Picture</label>
                    <input type="text" name="bp" class="form-control" placeholder="banners/<artist>.png" value="<?php echo $bp; ?>">
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
