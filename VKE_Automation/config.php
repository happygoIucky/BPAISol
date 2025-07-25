<?php
$XVWA_WEBROOT = '';
$host = "app.1day1kb.com";  // Your domain
$dbname = 'xvwa';
$user = 'root';
$pass = 'root';
$conn = mysql_connect($host, $user, $pass);
$conn1 = new mysqli($host, $user, $pass, $dbname);
?>
