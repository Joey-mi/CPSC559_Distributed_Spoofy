<?php
include "../modules/mysql_connect.php";
require_once("../modules/python_connect.php");

if(!isset($_SESSION)) { session_start(); }
if (isset($_SESSION["LoggedIn"]) && $_SESSION["LoggedIn"]) {
    $Premium = filter_var($_GET["Premium"], FILTER_VALIDATE_BOOLEAN);
    $UserID = $_SESSION["UserID"];

    		// 	// Replace single quotes with escape characters
			// $name = str_replace("'", "\'", $name);
			// $about = str_replace("'", "\'", $about);
			// $pfp = str_replace("'", "\'", $pfp);
			// $bp = str_replace("'", "\'", $bp);

			// $sql = "UPDATE ARTIST SET Name='$name', About='$about', ProfilePicture='$pfp', BannerPicture='$bp' WHERE ArtistID=$ArtistID";
			// sendQuery($sql);
			// header("Refresh:0; url=manage_artists.php"); // Test for refreshing page after update

            
    if ($Premium) {
        $premium = TRUE;
        $prepare = mysqli_prepare($con, $sql);
        if ($prepare) {
            $renew_date = date("Y-m-d", strtotime("+1 month"));
            $prepare -> bind_param("ss", '$renew_date', $UserID);
            // $prepare -> execute();
            // $_SESSION["IsPremium"] = true;
            $sql = "UPDATE USER SET IsPremium='$premium', SubRenewDate='$renew_date' WHERE UserID='$UserID'";
            sendQuery($sql);
        }
        $prepare -> close();
    } else {
        $premium = FALSE;
        $prepare = mysqli_prepare($con, $sql);
        if ($prepare) {
            $prepare -> bind_param("s", $UserID);
            // $prepare -> execute();
            // $_SESSION["IsPremium"] = false;
            $sql = "UPDATE USER SET IsPremium='$premium', SubRenewDate=NULL WHERE UserID='$UserID'";
            sendQuery($sql);
        }
        $prepare -> close();
    }

    // if ($Premium) {
    //     $sql = "UPDATE USER SET IsPremium=TRUE, SubRenewDate=$renew_date WHERE UserID=$UserID";
    //     sendQuery($sql);
    // } else {
    //     $sql = "UPDATE USER SET IsPremium=FALSE, SubRenewDate=$renew_date WHERE UserID=$UserID";
    //     sendQuery($sql);
    // }

    $_SESSION["Queue"] = null;
    $_SESSION["SongIndex"] = 0;
    // header("Refresh:0; url=/user/profile.php?UserID=".$UserID);
    header("location: /user/profile.php?UserID=".$UserID);
} else {
    // Someone not logged in is trying to update premium
    header("location: /user/login.php");
}
?>
