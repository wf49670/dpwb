<?php

$module_config["ppsmq"] = array(
    "description" => "Smart quote text reformatter",
    "input" => "text file with \"straight\" quotes",
    "output" => "text file with typographer's quotes",
    "documentation" => <<<DOCS
  <p>The ppsmq program attempts to convert a text file with straight quotes into one
  with curly quotes. It only makes changes it's pretty certain are
  correct. It will flag those it is uncertainabout with the "@"
  character. It will leave alone any straight quotes it can't reliably
  classify.</p>

  <p>Even if you don't intend to convert your book to curly quotes,
    anything that this program flags is often an error and should
    be investigated.</p>

  <p>If you are converting,
    once you've run the program and downloaded the result file, search
  everywhere for "@" and manually enter the correct punctuation, then
  remove the "@" flag. Then search for straight double quotes (there
  should be none) and straight single quotes (there usually are
  some).</p>

  <p>If you run this on an HTML file, you will find it converts all
  single quotes inside HTML tags to "∮" and all double quotes in tags to "∯"
  to protect them. The process is the same as in the previous paragraph.
  Then there is an added step to replace all "∮" with single quotes and
  all "∯" with double quotes to restore the HTML tags.</p>
DOCS
);
