<!doctype html>
<html lang="en">
  <head>
	<meta charset="utf-8">
	<meta name=viewport content="width=device-width, initial-scale=1">
    <title>DP Workbench</title>
  </head>

  <body>

<h1>DP Workbench Test Page</h1>

<p>This is a test page linking a few tools to this page. Here the file is uploaded, scanned for viruses, and then dispatched to an available test.</p>

<p>For now you must upload a zip file. Limit it to 20Mb or less. Drag and drop your zip file on the "Choose File" button or click the button for a dialog box. Once that file
is ready, choose one test (for now) from the checkboxes. Then click Submit.</p>

<form action="test_action.php" method="POST" enctype="multipart/form-data">
    <input type="file" name="zipfile" /><br/>
    <div style='margin-top:1em'>Then choose one of these available tests:</div>
    <input type="radio" name="requested_test" value="ppgutc" checked="checked"/> Gutcheck clone (UTF-8)<br />
    <input type="radio" name="requested_test" value="pplev" /> Levenshtein Checks<br />
    <div style='margin-top:1em'>When ready, click Submit:</div>
    <input type="submit" name="upload"/>
</form>

  </body>
</html>

