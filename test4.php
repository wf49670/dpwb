<!doctype html>
<html lang="en">
  <head>
	  <meta charset="utf-8">
	  <meta name=viewport content="width=device-width, initial-scale=1">
    <title>DP Workbench</title>
    <link rel="stylesheet" type="text/css" href="wb2.css">
  </head>

  <body>

<h1 class='rf'>DP Workbench Test Page <span style='font-size:small;'>(version 2018.03.23)</span></h1>

<p>This is a test page for the DP Workbench.<br/>Here the file is uploaded, scanned for viruses, and then dispatched to an available test.</p>

<p>For these first tests you may upload a text file or a zip file.<br/>
Drag and drop your file on the "Choose File" button or click the button for a 
dialog box.<br/>
Once that file is ready, choose one
test (for now) from the available checkboxes.<br/>
Tests without checkboxes are not available yet.<br/>
Click on the description to get more information about the program, incluing usage instructions.<br/>
When you have selected a file and a test to run, click Submit.</p>

<form action="test_action4.php" method="POST" enctype="multipart/form-data">
    <input type="file" name="userfile" /><br/>
    <div style='margin-top:1em'>Then choose one of these available tests:</div>
    <table>
    <tr>
      <th>Select</th>
      <th>Description</th>
      <th>Input file type</th>
    </tr>      
    <tr>
      <td><input type="radio" name="requested_test" value="ppgutc" checked="checked"/></td>
      <td><a href='writeup-gutcheck.html' target="_blank">Ppgutc gutcheck-type tests</a></td>
      <td>text file</td>
    </tr>
    <tr>
      <td><input type="radio" name="requested_test" value="pplev" /></td>
      <td><a href='writeup-pplev.html' target="_blank">Pplev edit distance checks</a></td>
      <td>text file</td>
    </tr>
    <tr>
      <td><input type="radio" name="requested_test" value="ppspell" /></td>
      <td><a href='writeup-ppspell.html' target="_blank">Ppspell spell checker</a></td>
      <td>text file<br/>or Zip file of text file and good_words.txt</td>
    </tr>   
    <tr>
      <td><input type="radio" name="requested_test" value="ppsmq" /></td>
      <td><a href='writeup-ppsmq.html' target="_blank">Ppsmq</a></td>
      <td>text with "straight" quotes.<br/>result file has typographer's quotes</td>
    </tr>
    <tr>
      <td><input type="radio" name="requested_test" value="ppjeeb" /></td>
      <td><a href='writeup-ppjeeb.html' target="_blank">Ppjeeb</a></td>
      <td>text file</td>
    </tr>        
  </table>
    <div style='margin-top:1em'>When ready, click Submit: <input type="submit" name="upload"/></div>
</form>

<p>It can take up to a minute for results to appear on the next page.<br/>Once they do, you may either
  view or download the results.</p>

  </body>
</html>

