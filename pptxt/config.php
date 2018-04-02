<?php

$module_config["pptxt"] = array(
    "description" => "text checks for post-processing",
    "input" => "text file",
    "output" => "results file sorted by test",
    "documentation" => <<<DOCS
  <p>The pptxt program runs many diverse tests on a text file. Here is a partial list of 
  the pptxt tests:</p>
  <ul>
    <li>superfluous asterisks</li>
    <li>adjacent spaces</li>
    <li>trailing spaces</li>
    <li>characters/glyphs that occur infrequently</li>
    <li>unexpected or unusual characters</li>
    <li>too long or too short lines</li>
    <li>repeated words</li>
    <li>unexpected HTML tags</li>
    <li>ellipsis and dash checks</li>
    <li>common scannos check</li>
    <li>many special situations tests</li>
  </ul>

  <p>Source is Latin-1 or UTF-8 text file. Result is the pptxt report.</p>
DOCS
);
