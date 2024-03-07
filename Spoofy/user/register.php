<?php
include "../modules/menubar.php";
include "../modules/mysql_connect.php";

if(!isset($_SESSION)) { session_start(); }
if (isset($_SESSION["LoggedIn"]) && $_SESSION["LoggedIn"]) {
    // @todo send to user profile
    header("location: /index.php");
 }

// Define variables and initialize with empty values
$username = "";
$password = "";
$password2 = "";
$error_string = "";

// Processing form data when form is submitted
if($_SERVER["REQUEST_METHOD"] == "POST") {

    // Validate username
    $username = trim($_POST["username"]);
    if(empty($username)) {
        $error_string = "Username can't be empty.";
    } elseif(!preg_match('/^[a-zA-Z0-9_]+$/', trim($_POST["username"]))) {
        $error_string = "Username can only contain letters, numbers, and underscores.";
    } else {
        // Make sure this username is unique
        $sql = "SELECT UserID FROM USER WHERE Username = ?";
        $prepare = mysqli_prepare($con, $sql);
        if($prepare) {
            $prepare -> bind_param("s", $username);
            $prepare -> execute();
            $result = $prepare -> get_result();
            if ($result) {
                if (mysqli_num_rows($result) > 0) {
                    // Failure, other user with same username exists
                    $error_string = "This username is already taken.";
                }
            } else {
                echo "Error: failed to register.";
            }
            $prepare -> close();
        }
    }
    
    // Validate password
    $password = trim($_POST["password"]);
    if(empty($password)) {
        $error_string = "Password can't be empty.";     
    } elseif(strlen($password) < 4) {
        $error_string = "Password must have atleast 4 characters.";
    }
    
    // Validate confirm password
    $password2 = trim($_POST["password2"]);
    if(empty($password2)) {
        $error_string = "Please confirm password.";     
    } else {
        if($password != $password2) {
            $error_string = "Passwords don't match.";
        }
    }

    // If there are no errors, insert into the database
    if(empty($error_string)) {
        
        // Prepare an insert statement
        $sql = "INSERT INTO USER (Username, PasswordHash, IsPremium) VALUES ($username, $password_hash, FALSE)";
        sendQuery($sql);
        // $sql = "INSERT INTO USER (Username, PasswordHash, IsPremium) VALUES (?, ?, FALSE)";
        // $prepare = mysqli_prepare($con, $sql);
        if($prepare) {

            // // Hash the password before binding it
            // $password_hash = hash("sha256", $password);
            // $prepare -> bind_param("ss", $username, $password_hash);

            // $prepare -> execute();
            // $result = $prepare -> get_result();
            
            // Redirect to login page after registering
            header("location: /user/login.php");
            $prepare -> close();
        }
    }
    
    // Close connection
    mysqli_close($con);
}
?>

<html>
    <head>
    <link href="/styles/style.css" rel="stylesheet" />
        <title>Register - Spoofy</title>
    </head>
    <body>
        <div class="wrapper">
        <h2>Sign Up</h2>
        <p>Please fill this form to create an account.</p>
            <form action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]); ?>" method="post">
                <label>Username</label>
                <input type="text" name="username" class="form-control" value="<?php echo $username; ?>">

                <label>Password</label>
                <input type="password" name="password" class="form-control" value="<?php echo $password; ?>">

                <label>Confirm Password</label>
                <input type="password" name="password2" class="form-control" value="<?php echo $password2; ?>">
                
                <input type="submit" class="submitForm" value="Submit">
                <input type="reset" class="btn btn-secondary ml-2" value="Reset">
                <?php if ($error_string) echo "<p style=\"color:red;\">".$error_string."</p>";?>
                <p>Already have an account? <a href="/user/login.php">Login here</a>.</p>
            </form>
        </div>
    </body>
</html>
