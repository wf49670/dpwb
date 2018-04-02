<?php

$module_config["ppspell"] = array(
    "description" => "spell checker",
    "input" => "text file or Zip file of text file+goodwords.txt",
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

      <p>Currently the dictionary used is aspell's en_US. Others may be available based on demand.</p>
DOCS
);