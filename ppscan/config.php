<?php

$module_config["ppscan"] = array(
    "description" => "smart quote checker",
    "input" => "UTF-8 text file with curly quotes",
    "takes_options" => TRUE,
    "output" => "result file with suspicious punctuation flagged",
    "documentation" => <<<DOCS
<p>The ppscan program runs a state-based scan for punctuation on a text file that has been 
prepared for submission to Project Gutenberg. It is checking the curly quotes, so the file
should be UTF-8 with curly quotes. The user uploads a text file, chooses any options to
override deafults and clicks Submit. After the prgoram has analzyed the file, it presents
a link to the results for the user to download or view. In that file, 
<span style='color:red'>search for the "@" symbol</span>, which marks where the
program thinks there might be a problem. Usually you can spot a problem or a false positive 
quickly. If you need to know more about what the program questioned, if the verbose
option is included, a list of errors,
including the description, is appended to the end of the results file.</p>

<h2>User options for ppscan</h2>

<p>On the Post Processing Workbench main page there is a place for the user to enter
"User options" for ppscan. You do not have to enter anything in this box. Default values
are appropriate for many people. However if you want to customize the report, here are
the options for this tool:</p>

<table style='width:90%'>
  <tr>
    <th>SHORT FORM</th>
    <th>LONG FORM</th>
    <th>DESCRIPTION</th>
  </tr>
  <tr>
    <td style='width:3em'>-d</td>
    <td style='width:8em'>--desc</td>
    <td>
      This option causes ppscan to put a short descriptive 4-letter mnemonic at
      any place in question instead of the simple '@' mark. For example, a
      user seeing "@CODQ" would know to look for Consecutive Open Double QUotes.
    </td>
  </tr>
  <tr>
    <td style='width:3em'>-v</td>
    <td style='width:8em'>--verbose</td>
    <td>
      This option causes ppscan append a list of errors,
      including the description, to the end of the results file
    </td>
  </tr>
  <tr>
    <td style='width:3em'>-w</td>
    <td style='width:8em'>--wfile</td>
    <td>
      This option allows the user to use a different wordlist
      than the default en_US. Choices are "en", "de", "es", "fr", "en_us"
    </td>
  </tr>  
</table>
DOCS
);
