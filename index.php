<?php

// Specify the modules we want to expose to the user
$modules = array(
    "ppgutc",
    "pplev",
    "ppspell",
    "ppsmq",
    "pptxt",
    "ppppv",
);

$module_configs = load_module_configs($modules);

// If the user wants to see details about a module, just show that
$module = @$_GET["module"];
if($module)
{
    output_header();
    echo "<h1>Workbench Component: $module</h1>";
    echo $module_configs[$module]["documentation"];
    output_footer();
    exit;
}

output_header();
output_workbench_menu($module_configs);
output_footer();

//---------------------------------------------------------------------------

function load_module_configs($modules)
{
    $module_config = array();
    foreach($modules as $module)
    {
        require("$module/config.php");
    }

    return $module_config;
}

function output_module_table($module_configs)
{
    echo <<<HEAD
    <table>
    <tr>
      <th>Select</th>
      <th>Description</th>
      <th>Usage</th>
    </tr>
HEAD;

    foreach($module_configs as $module => $config)
    {
        $description = $config["description"];
        $input = $config["input"];
        $output = $config["output"];

        echo <<<ROW
    <tr>
      <td><input type="radio" name="requested_test" value="$module"></td>
      <td><a href='?module=$module' target="_blank">$module</a><br>$description</td>
      <td>
        Input: $input<br>
        Output: $output
      </td>
    </tr>
ROW;
    }
    echo "</table>";
}

function output_header()
{
    echo <<<HEAD
<!doctype html>
<html lang="en">
  <head>
	  <meta charset="utf-8">
	  <meta name=viewport content="width=device-width, initial-scale=1">
    <title>Post-Processing Workbench</title>
    <link rel="stylesheet" type="text/css" href="dpwb.css">
  </head>

  <body>
HEAD;
}

function output_footer()
{
    echo <<<FOOT
  </body>
</html>
FOOT;
}

function output_workbench_menu($module_configs)
{
    echo <<<MENU

<h1 class='rf'>Post-Processing Workbench</h1>

<p>Welcome to the Post-Processing Workbench.
Here you may upload a text or .zip file and select, one by one, the tests you would like it to undergo.</p>

<div>Instructions:</div>
<ol style='margin-top:0'>
    <li>Drag and drop your text or .zip file onto the "Choose File" or "Browse" button or click the button to select your file via a dialogue box. Zip files should contain the HTML/text/image etc. files prepared as you would to submit to PPV or to Project Gutenberg and other files (such as goodwords.txt) appropriate to a particular test.</li>
<li>Once your file has been uploaded it's name will appear beside the button.</li>
<li>Select a test from the list and press the "Submit" button.</li>
<li>Once the test is completed (it can take a minute or more to complete), you may view or download the test results.</li>
<li>To return to the test selection screen, simply use your "Back" button. You can then select and run another test.</li>
</ol>

<form action="action.php" method="POST" enctype="multipart/form-data">
    <input type="file" name="userfile"  /><br/>
    <div style='margin-top:1em; margin-bottom:0.5em;'>Then select one of these available tests:</div>
MENU;

    output_module_table($module_configs);

    echo <<<MENU
    <div style='margin-top:1em; margin-bottom:2em;'><input type="submit" value="Submit" name="upload"/></div>
</form>

<div>Please remember to also run these tests:</div>
  <ul style='margin-top:0'>
    <li><a href='http://epubmaker.pglaf.org/'>Gutenberg online epubmaker</a></li>
    <li><a href="http://validator.w3.org/">W3C HTML markup validator</a></li>
    <li><a href="http://jigsaw.w3.org/css-validator/">W3C CSS validator</a></li>
    <li><a href="http://validator.w3.org/checklink">W3C Link Checker</a></li>
  </ul>
MENU;
}
