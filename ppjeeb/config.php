<?php

$module_config["ppjeeb"] = array(
    "description" => "Python port of jeebies",
    "input" => "text file",
    "output" => "list of \"he/be\" suspects with context",
    "documentation" => <<<DOCS
  <p>OCR scanning often confuses the letter "h" and the letter "b" when scanning "he" or "be" in the source text. The
  ppjeeb program tries to find where this might have happened. Provide ppjeeb a UTF-8 or a Latin-1 text file.</p>
DOCS
);
