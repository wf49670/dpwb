<?php

$module_config["ppspell"] = array(
    "description" => "spell checker",
    "input" => "text file or Zip file of text file+goodwords.txt",
    "takes_options" => TRUE,
    "output" => "suspect words with frequency and context<br><small>Please note: more accurate results if updated goodwords.txt file included in zip</small>",
    "documentation" => <<<DOCS
  <p>The ppspell program runs an intelligent spellcheck on a text file. It uses a combination
    of filtering hueristics backed by the aspell dictionaries for English and several
    other languages.</p>

    <p>If a single, unzipped file is uploaded a straightforward spell-check is
      completed. Suspect words are presented with line numbers and context. Users
      with an available project Good Word List can improve the accuracy of the
      check by creating a Zip file containing the text file and the good
      words in a file named <span style='color:brown'>goodwords.txt</span>.
      The ppspell program will use a goodwords.txt file if it finds one.</p>

    <p>The goodwords.txt file can be Latin-1 or UTF-8. However, if you want to
      include words with diacriticals not available in Latin-1, submit a
      UTF-8 goodwords.txt file. You are encouraged to review and edit the goodwords.txt
     file before uploading it.</p>

      <p>Currently the dictionary used is aspell's "en_us". Others are available using
      the User options.</p>
    <h2>User options for ppspell</h2>

    <p>On the Post Processing Workbench main page there is a place for the user to enter "User options" for this program.
      You do not have to enter anything in this box. Default values are appropriate for many people. However if
    you want to customize the report, here are the options and some samples of how to use them.</p>

    <table style='width:90%'>
      <tr>
        <th>SHORT FORM</th>
        <th>LONG FORM</th>
        <th>DESCRIPTION</th>
      </tr>
      <tr>
        <td>-l</td><td>--lang</td><td>User specified language (one of "en", "de", "es", "fr", "en_us"). Default
        is "en_us"</td>
      </tr>
    </table>

    <p>Options are entered into the User options box separated by a space.
    You can only enter a letters, numbers, a hyphen, comma, space, underscore or equal sign
    to create your user options line.</p>      
DOCS
);
