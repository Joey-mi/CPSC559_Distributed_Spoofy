<?php
include "../modules/menubar.php";
include "../modules/mysql_connect.php";
require_once("../modules/python_connect.php");

if(!isset($_SESSION)) { session_start(); }
if (isset($_SESSION["LoggedIn"]) && $_SESSION["LoggedIn"] && $_SESSION["Admin"]) {
    // Define variables and initialize with empty values
    $duration = "";
    $company = "";
    $soundfile = "";
    $error_string = "";

    // Processing form data when form is submitted
    if($_SERVER["REQUEST_METHOD"] == "POST"){

        // Validate duration
        $duration = trim($_POST["duration"]);
		if(empty($duration)) {
			$error_string = "Duration can't be empty.";     
		} elseif(!preg_match('/^[0-5][0-9]:[0-5][0-9]:[0-5][0-9]$/', trim($_POST["duration"]))) {
			$error_string = "Duration should be formatted as 'hh:mm:ss'";
		}

        // Validate company
        $company = trim($_POST["company"]);
        if(empty($company)) {
            $error_string = "company can't be empty.";
        }
        
        // Validate soundfile
        $soundfile = trim($_POST["soundfile"]);
        if(empty($soundfile)) {
            $error_string = "company can't be empty.";
        } elseif(!preg_match('/^[a-zA-Z0-9_.\/]+$/', trim($_POST["soundfile"]))) {
            $error_string = "soundfile can only contain letters, numbers, underscores, forward slashes, and .";
        }

        // If there are no errors, insert into the database
        if(empty($error_string)) {

            // Replace single quotes with escape characters
			$company = str_replace("'", "\'", $company);
			$soundfile = str_replace("'", "\'", $soundfile);

            // Prepare an insert statement
            $sql = "INSERT INTO ADVERTISEMENT (duration, company, soundfile) VALUES ($duration, '$company', '$soundfile')";
            sendQuery($sql);
            header("Refresh:0; url=manage_ads.php");
        }

    }
} 
else {
    header("location: ../error.php");
}
?>


<html>
    <head>
    <link href="/styles/style.css" rel="stylesheet" />
        <title>Manage Advertisements - Spoofy</title>
    </head>
    <body>
        <div class="wrapper">
        <h1>Manage Advertisements</h1>
            <form action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]); ?>" method="post">
                <label>Duration</label>
                <input type="text" name="duration" placeholder="ex. 00:03:50" class="form-control" value="<?php echo $duration; ?>">

                <label>Company</label>
                <input type="text" name="company" placeholder="ex. E Corp" class="form-control" value="<?php echo $company; ?>">

                <label>SoundFile</label>
                <input type="text" name="soundfile" placeholder="ex. ads/ad.mp3" class="form-control" value="<?php echo $soundfile; ?>">
                
                <input type="submit" class="submitForm" value="Submit">
                <?php if ($error_string) echo "<p style=\"color:red;\">".$error_string."</p>";?>
            </form>
            <?php 
                $result = mysqli_query($con, "SELECT * FROM ADVERTISEMENT");
                echo "<table border='1'>
                <tr>
                <th>AdID</th>
                <th>Duration</th>
                <th>Company</th>
                <th>SoundFile</th>
                </tr>";

                while($row = mysqli_fetch_array($result)) {
                    echo "<tr>
                    <td>" . $row['AdID'] . "</td>
                    <td>" . $row['Duration'] . "</td>
                    <td>" . $row['Company'] . "</td>
                    <td>" . $row['SoundFile'] . "</td>
                    <td><a href='/admin/delete_ad.php?AdID= " . $row['AdID'] . "' onclick=\"return confirm('Are you sure?')\";>Delete</a></td>";
                    "</tr>";
                }
                echo "</table>";

                mysqli_close($con); 
            ?>
        </div>
    </body>
</html>
