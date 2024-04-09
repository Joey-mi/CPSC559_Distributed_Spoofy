<?php
include "../modules/mysql_connect.php";
require_once("../modules/python_connect.php");

if(!isset($_SESSION)) { session_start(); }
if (isset($_SESSION["LoggedIn"]) && $_SESSION["LoggedIn"]) {
    $Premium = filter_var($_GET["Premium"], FILTER_VALIDATE_BOOLEAN);
    $UserID = $_SESSION["UserID"];

    if ($Premium) {
        $bool = TRUE;
        $renew_date = date("Y-m-d", strtotime("+1 month"));
        $_SESSION["IsPremium"] = true;
        $sql = "UPDATE USER SET IsPremium='$bool', SubRenewDate='$renew_date' WHERE UserID='$UserID'";
        echo $sql;
    } else {
        $bool = FALSE;
        $_SESSION["IsPremium"] = false;
        $sql = "UPDATE USER SET IsPremium='$bool', SubRenewDate=NULL WHERE UserID='$UserID'";
        echo $sql;
        sendQuery($sql);
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
