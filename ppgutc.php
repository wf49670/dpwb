<!doctype html>
<html lang="en">
  <head>
	<meta charset="utf-8">
	<meta name=viewport content="width=device-width, initial-scale=1">
    <title>DP Workbench:ppgutc</title>
  </head>

  <body>

  <h1>Workbench:ppgutc</h1>

  <p>Workbench:ppgutc runs extensive checks on a text file that has been prepared for submission
  to Project Gutenberg. The user uploads a text file, clicks Submit, and then downloads
  or views the results text file.</p>

  <p>Users can select "Show all reports" to request ppgutc show <em>all</em> suggested errors. Normal
   behavior is to truncate any singe type of error to 5 reports. This option also
  lists all tests that were run, even if no errors were reported.</p>

  <h2>Process:</h2>

  <ol>
    <li>Select a text file to check by clicking the “Choose File” button.
    File must end in “.txt”. Encoding must be UTF-8, Latin-1 or ASCII.</li>
    <li>After the file is selected, click “Submit” to send it to the server for analysis.</li>
    <li>When analysis is complete, you will see a “results available: here” message
        with a link to the results file. With that link, left click to view;
        right click to download.</li>
  </ol>

      <form action="ppgutc_action.php" method="POST" enctype="multipart/form-data">
         Choose a text file to analyze: <input type="file" name="textfile" /><br/>
         <br/>Normal operation is to limit reports of any one test. Tick the box below to show all reports:<br/>
         <input type="checkbox" id="verbose" name="verbose" value="Yes">
         <label for="verbose">Show all reports</label>

         <br/><br/>Click Submit to run the tests:<br/>
         <input type="submit" name="upload"/>
      </form>

</body>
</html>
