<?php

# the wbkey.txt file holds a word that must match
# a GET variable before this code can execute.
# it is intentionally not within public_html

$s=file_get_contents('/home/rfrank/wbkey.txt');
if ( trim($_GET["pass"]) != trim($s) ) {
    exit(); # exit quietly    
}

# http://www.pgdp.org/~rfrank/maint.php?pass=passwordS
#
# typically run this to clear the working directory
# and the access.log after doing a tar and save offsite
#
# .rfrank 31-Mar-2018

function removeDirectory($path) {
    $files = glob($path . '/*');
    foreach ($files as $file) {
        is_dir($file) ? removeDirectory($file) : unlink($file);
    }
    rmdir($path);
    return;
}

# remove all the project folders

$dir = '/home/rfrank/public_html/t';
$files1 = array_slice(scandir($dir), 2);
foreach ($files1 as $t) {
    if ($t !== "access.log") {
        $dir = '/home/rfrank/public_html/t/'.$t; 
        echo("removing ".$dir."<br/>");
        removeDirectory($dir);
    }
}

# reset access.log

file_put_contents("/home/rfrank/public_html/t/access.log", "");

echo "done.";
?>
