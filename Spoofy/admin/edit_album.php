<?php
include "../modules/menubar.php";
include "../modules/mysql_connect.php";
require_once("../modules/python_connect.php");


if(!isset($_SESSION)) { session_start(); }
if (isset($_SESSION["LoggedIn"]) && $_SESSION["LoggedIn"] && $_SESSION["Admin"]){

	$AlbumID = $_GET["AlbumID"];

	$prepare = mysqli_prepare($con, "SELECT * FROM ALBUM WHERE AlbumID=?");
	$prepare -> bind_param("s", $AlbumID);
	$prepare -> execute();
	$result = $prepare -> get_result();
	$row = mysqli_fetch_array($result);

	//set default values
	$titleDef = $row["Title"];
	$singleDef = $row["IsSingle"];
	$coverDef = $row["CoverArt"];
	$releaseDef = $row["ReleaseDate"];
	$genreDef = $row["Genre"];

	// Define variables and initialize with empty values
	$error_string = "";
	$title = "";
	$single = "";
	$cover = "";
	$genre = "";
	$release = "";

	// Processing form data when form is submitted
	if($_SERVER["REQUEST_METHOD"] == "POST"){

		$AlbumID = trim($_POST["AlbumID"]);

		// Validate title
		$title = trim($_POST["title"]);
		if(empty($title)) {
			$error_string = "Title can't be empty.";
		}
		
		// Validate issingle
		$single = trim($_POST["single"]);
		if(empty($single) && !is_numeric($single)){	// empty() evaluates "0" to true for some reason: https://www.php.net/manual/en/function.empty.php
			$error_string = "Single can't be empty.";
		} elseif(!preg_match('/^[0-1]$/', trim($_POST["single"]))){
			$error_string = "Single must be either 0 (not a single) or 1 (is a single).";
		}
		
		// Validate cover art path
		// TODO: Actual validation checks
		$cover = trim($_POST["cover"]);
		
		// Validate release date
		// TODO: Improve this regex
		$release = trim($_POST["release"]);
		if(!empty($release)){
			if(!preg_match('/^[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]$/', trim($_POST["release"]))){
				$error_string = "release date should be formatted as yyyy-mm-dd";
			}
		} else {
			$release = '1970-01-01';
		}
		
		// Validate genre
		// TODO: Actual validation checks
		$genre = trim($_POST["genre"]);

		// If there are no errors, insert into the database
		if(empty($error_string)) {
			
			// Prepare an insert statement
			$sql = "UPDATE ALBUM SET Title=$title, IsSingle=$single, CoverArt=$cover, ReleaseDate=$release, Genre=$genre WHERE AlbumID=$AlbumID";
			sendQuery($sql);
			// $sql = "UPDATE ALBUM SET Title=?, IsSingle=?, CoverArt=?, ReleaseDate=?, Genre=? WHERE AlbumID=?";
			// $prepare = mysqli_prepare($con, $sql);
			if($prepare) {
				
				// // Bind all values
				// $prepare -> bind_param("ssssss", $title, $single, $cover, $release, $genre, $AlbumID);
				// $prepare -> execute();
				// $result = $prepare -> get_result();
				
				// Redirect to login page after registering
				header("location: manage_albums.php");
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
        <title>Edit Album - Spoofy</title>
    </head>
    <body>
        <div class="wrapper">
        <h2>Edit Album</h2>
        <p>Update album information:</p>
            <form action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]); ?>" method="post">
			    <div class="form-group">
                    <label>Album ID</label>
					<input type="text" name="AlbumID" class="form-control" value="<?php echo $AlbumID; ?>" readonly style="background-color: grey;" >
                </div>
                <div class="form-group">
                    <label>Title</label>
                    <input type="text" name="title" class="form-control" value="<?php echo $titleDef; ?>">
                </div>    
                <div class="form-group">
                    <label>Single or Not? (1 or 0)</label>
                    <input type="text" name="single" class="form-control" value="<?php echo $singleDef; ?>">
                </div>
				<div class="form-group">
                    <label>Path to Cover Art</label>
                    <input type="text" name="cover" class="form-control" value="<?php echo $coverDef; ?>">
                </div> 
				<div class="form-group">
                    <label>Release Date</label>
                    <input type="text" name="release" class="form-control" value="<?php echo $releaseDef; ?>">
                </div> 
				<div class="form-group">
                    <label>Genre</label>
                    <input type="text" name="genre" class="form-control" value="<?php echo $genreDef; ?>">
                </div> 
                <div class="form-group">
                    <input type="submit" class="submitForm" value="Submit">
                    <input type="reset" class="btn btn-secondary ml-2" value="Reset">
                </div>
                <?php if ($error_string) echo "<p style=\"color:red;\">".$error_string."</p>";?>
				<button onclick='location.href="manage_albums.php"' type='button'>
					Return to Manage Albums
				</button><br>
            </form>
        </div>
    </body>
</html>
