<?php

$module_config["pplev"] = array(
    "description" => "edit distance checks",
    "input" => "text file",
    "output" => "list of edit-distance 1 suspect words, in context",
    "documentation" => <<<DOCS
  <p>The pplev program does Levenshtein or "edit-distance" checks on a
    UTF-8 text file. The Levenshtein distance between two words
    is the minimum number of single-character edits (insertions,
    deletions or substitutions) required to change one word into the other.</p>

<p>Here is a part of a report of two words with an edit distance of 1.
  It includes how many times each word occured (once and nine times),
  and the line and line number illustrating each word in the text.</p>

  <pre>Marañon (1) <-> Marañón (9)
      12077: rivers Uriaparia and Marañon, and this one of La Plata. I answered
      1047: Gran Chaco, of Alvarado and Mercadillo in the valleys of the Marañón</pre>
DOCS
);
