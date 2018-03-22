<!doctype html>
<html lang="en">
  <head>
	<meta charset="utf-8">
	<meta name=viewport content="width=device-width, initial-scale=1">
    <title>DP Workbench</title>
    <style type="text/css">
        h1 { font-weight: normal; font-size: 1.4em; }
        table { border-collapse: collapse; }
        table, th, td { border: 1px solid black; }
        td { padding-left: 0.5em; padding-right: 1em;}
    </style>
  </head>

  <body>

<h1>DP Workbench Test Page <span style='font-size:small;'>(version 2018.03.22)</span></h1>

<p>This is a test page for the DP Workbench.<br/>Here the file is uploaded, scanned for viruses, and then dispatched to an available test.</p>

<p>For these first tests you must upload a <span style='text-decoration:underline'>text</span> file only.<br/>
Drag and drop your text file on the "Choose File" button or click the button for a 
dialog box.<br/>
Once that file is ready, choose one
test (for now) from the available checkboxes. Tests without checkboxes are not available yet.
Then click Submit.</p>

<form action="test_action2.php" method="POST" enctype="multipart/form-data">
    <input type="file" name="txtfile" /><br/>
    <div style='margin-top:1em'>Then choose one of these available tests:</div>
    <table>
    <tr>
      <th>Select</th>
      <th>Description</th>
      <th>Input file type</th>
    </tr>      
    <tr>
      <td><input type="radio" name="requested_test" value="ppgutc" checked="checked"/></td>
      <td>Gutcheck clone </td>
      <td>UTF-8 or Latin-1 text</td>
    </tr>
    <tr>
      <td><input type="radio" name="requested_test" value="pplev" /></td>
      <td>Levenshtein Checks</td>
      <td>UTF-8 or Latin-1 text</td>
    </tr>
    <tr>
      <td></td>
      <td>PP PPV Checks</td>
      <td>Zip file with HTML and images</td>
    </tr>   
    <tr>
      <td></td>
      <td>PPSpell</td>
      <td>UTF-8 text</td>
    </tr>  
  </table>
    <div style='margin-top:1em'>When ready, click Submit: <input type="submit" name="upload"/></div>
</form>

<p>It can take up to a minute for results to appear on the next page. Once they do, you may either
  view or download the results.</p>

  </body>
</html>

