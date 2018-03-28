<!doctype html>
<html lang="en">
  <head>
	  <meta charset="utf-8">
	  <meta name=viewport content="width=device-width, initial-scale=1">
    <title>DP Workbench</title>
    <link rel="stylesheet" type="text/css" href="wb2.css">
  </head>

  <body>

<h1 class='rf'>DP Workbench Test Page <span style='font-size:small;'>(version 2018.03.28)</span></h1>

<p>This is a test page for the DP Workbench.<br/>Here the file is uploaded, scanned for viruses, and then dispatched to an available test.</p>

<p>For these tests you may upload a text file or a zip file.<br/>
Drag and drop your file on the "Choose File" button or click the button for a dialog box.<br/>
Once that file is ready, choose one test (for now) from the available checkboxes.<br/>
Any test without a checkbox is not available yet.<br/>
Click on the description to get more information about the program.<br/>
When you have selected a file and a test to run, click Submit.</p>

<form action="test_action4.php" method="POST" enctype="multipart/form-data">
    <input type="file" name="userfile" /><br/>
    <div style='margin-top:1em'>Then select one of these available tests:</div>
    <table>
    <tr>
      <th>Select</th>
      <th>Description</th>
      <th>Usage</th>
    </tr>      
    <tr>
      <td><input type="radio" name="requested_test" value="ppgutc" checked="checked"/></td>
      <td><a href='writeup-gutcheck.html' target="_blank">Ppgutc</a><br/>gutcheck-type tests</td>
      <td>
        input: text file<br/>
        output: report file listed by test number
      </td>
    </tr>
    <tr>
      <td><input type="radio" name="requested_test" value="pplev" /></td>
      <td><a href='writeup-pplev.html' target="_blank">Pplev</a><br/>edit distance checks</td>
      <td>
        input: text file<br/>
        output: list of edit-distance 1 suspect words, in context
      </td>
    </tr>
    <tr>
      <td><input type="radio" name="requested_test" value="ppspell" /></td>
      <td><a href='writeup-ppspell.html' target="_blank">Ppspell</a><br/>spell checker</td>
      <td>
        input: text file or Zip file of text file+good_words.txt<br/>
        output: suspect words with frequencey and context
      </td>
    </tr>   
    <tr>
      <td><input type="radio" name="requested_test" value="ppsmq" /></td>
      <td><a href='writeup-ppsmq.html' target="_blank">Ppsmq</a></a><br/>Smart quote text reformatter</td>
      <td>
        input: text file with "straight" quotes.<br/>
        output: text file with typographer's quotes
      </td>
    </tr>
    <tr>
      <td><input type="radio" name="requested_test" value="ppjeeb" /></td>
      <td><a href='writeup-ppjeeb.html' target="_blank">Ppjeeb</a></a><br/>Python port of jeebies</td>
      <td>
        input: text file<br/>
        output: list of "he/be" suspects with context
      </td>
    </tr>
    <tr>
      <td><input type="radio" name="requested_test" value="pptxt" /></td>
      <td><a href='writeup-pptxt.html' target="_blank">Pptxt</a></a><br/>text checks for post-processing</td>
      <td>
        input: text file<br/>
        output: results file sorted by test.
      </td>
    </tr>       
  </table>
    <div style='margin-top:1em'>When ready, click Submit: <input type="submit" name="upload"/></div>
</form>

<p>It can take up to a minute for results to appear on the next page.<br/>Once they do, you may either
  view or download the results.</p>

  </body>
</html>

