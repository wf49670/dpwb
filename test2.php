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
td.tooltip{
    position:relative;
}
td.tooltip::before {
    content: attr(data-tooltip) ;
    font-size: 12px;
    position:absolute;
    z-index: 999;
    white-space:nowrap;
    bottom:9999px;
    left: 0;
    background:#000;
    color:#e0e0e0;
    padding:0px 7px;
    line-height: 24px;
    height: 24px;
    opacity: 0;
}
td.tooltip:hover::before {
    opacity: 1;
    top:22px;
}
td.tooltip:hover::after {
    content: "";
    opacity: 1;
    width: 0; 
    height: 0; 
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-bottom: 5px solid black;
    z-index: 999;
    position:absolute;
    white-space:nowrap;
    top:17px;
    left: 0px;
}
     
    </style>
  </head>

  <body>

<h1>DP Workbench Test Page <span style='font-size:small;'>(version 2018.03.22)</span></h1>

<p>This is a test page for the DP Workbench.<br/>Here the file is uploaded, scanned for viruses, and then dispatched to an available test.</p>

<p>For these first tests you must upload a <span style='text-decoration:underline'>text</span> file only.<br/>
Drag and drop your text file on the "Choose File" button or click the button for a 
dialog box.<br/>
Once that file is ready, choose one
test (for now) from the available checkboxes.<br/>
Tests without checkboxes are not available yet.
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
      <td class='tooltip'
      data-tooltip="This program borrows checks from many other scattered programs, including the gutcheck (Gutenberg check) macros. It runs about eighty checks with more to be added.">Ppgutc gutcheck-type tests</td>
      <td>UTF-8 or Latin-1 text</td>
    </tr>
    <tr>
      <td><input type="radio" name="requested_test" value="pplev" /></td>
      <td class='tooltip' data-tooltip="Pplev does Levenshtein or &quot;edit-distance&quot; checks on a UTF-8 text file. The Levenshtein distance between two words is the minimum number of single-character edits (insertions, deletions or substitutions) required to change one word into the other. Short edit distances can uncover inconsistent spellings, such as &quot;Marañon&quot; and &quot;Marañón&quot; in the same document.">Pplev edit distance checks</td>
      <td>UTF-8 or Latin-1 text</td>
    </tr>
    <tr>
      <td></td>
      <td class='tooltip' data-tooltip="This program performs specific checks on an HTML file and images in an images folder related to post-processing verification.">PP PPV Checks</td>
      <td>Zip file with HTML and images</td>
    </tr>   
    <tr>
      <td></td>
      <td class='tooltip' data-tooltip="This is an online version of the ppspell program. It attempts to do an intelligent spell-check of a text file. For example, non-dictionary words that meet certain tests, such as frequency of occurence, are accepted as good words.">PPSpell</td>
      <td>UTF-8 text</td>
    </tr>  
  </table>
    <div style='margin-top:1em'>When ready, click Submit: <input type="submit" name="upload"/></div>
</form>

<p>It can take up to a minute for results to appear on the next page.<br/>Once they do, you may either
  view or download the results.</p>

  </body>
</html>

