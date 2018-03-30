<!doctype html>
<html lang="en">
  <head>
	  <meta charset="utf-8">
	  <meta name=viewport content="width=device-width, initial-scale=1">
    <title>Post-Processing Workbench</title>
    <link rel="stylesheet" type="text/css" href="dpwb.css">
  </head>

  <body>

<h1 class='rf'>Post-Processing Workbench Test Page <span style='font-size:small;'>(version 2018.03.30)</span></h1>

<p>This is a test page for the Post-Processing Workbench.</p>

<p>Here you may upload a text or .zip file and select, one by one, the tests you would like it to undergo.</p>

<p>Instructions:</p>

<ol>
<li>Drag and drop your text or .zip file onto the "Choose File" or "Browse" button or click the button to select your file via a dialogue box. Zip files should contain only the HTML/text/image etc. files prepared as you would to submit to PPV or to Project Gutenberg.</li>
<li>Once your file has been uploaded it's name will appear beside the button.</li>
<li>Select a test from the list and press the "Submit" button.</li>
<li>Once the test is completed (it can take a minute or more to complete), you may view or download the test results.</li>
<li>To return to the test selection screen, simply use your "Back" button. You can then select and run another test.</li>
</ol>

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
      <td><a href='writeup-ppgutc.html' target="_blank">Ppgutc</a><br/>gutcheck-type tests</td>
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
    <div style='margin-top:1em; margin-bottom:2em;'><input type="submit" name="upload"/></div>
</form>

<p>Please remember to also run these tests:</p>

<ul>
      <li><a href='http://epubmaker.pglaf.org/'>Gutenberg online epubmaker</a></li>
    <li><a href="http://validator.w3.org/">W3C HTML markup validator</a></li>
    <li><a href="http://jigsaw.w3.org/css-validator/">W3C CSS validator</a></li>
    <li><a href="http://validator.w3.org/checklink">W3C Link Checker</a></li>
  </ul>

  </body>
</html>
