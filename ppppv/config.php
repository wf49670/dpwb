<?php

$module_config["ppppv"] = array(
    "description" => "checks for PPV",
    "input" => "zip file that includes HTML and images folder",
    "output" => "results file",
    "documentation" => <<<DOCS
  <p>The ppppv program attempts to automate some of the checks done
  during Post Processing Verification ("PPV"). It does not run all the
  necessary checks but either runs the check or reminds the user to make
  the check during PPV.</p>

  <p>For example, the &lt;title> in the HTML header and the &lt;h1>
  title should be fairly similar. This program shows them both, side by
  side, so the PPVer can quickly see if they are acceptably close.
  Similarly, PPVers should check the image dimensions and file sizes,
  verify they are all used and that there are no extra files in the
  images folder, etc. These tasks are well-suited to ppppv.</p>
DOCS
);
