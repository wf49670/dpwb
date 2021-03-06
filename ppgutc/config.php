<?php

$module_config["ppgutc"] = array(
    "description" => "gutcheck-type tests",
    "input" => 'text file',
    "output" => "report file listed by test number",
    "takes_options" => TRUE,
    "documentation" => <<<DOCS
  <p>The ppgutc program runs extensive checks on a text file that has been prepared for submission
  to Project Gutenberg. The user uploads a text file or zip file
  containing a text file, clicks Submit, waits for the test to run and then downloads
  or views the results text file.</p>

  <p>After a run, each report shows a test number along with reports for that test. Usually
    the first five errors of any type are reported. Report format can be altered with
  user-supplied options as described below. For many users, the default options are adequate.</p>

    <p>Please Note: both ppgutc and its ancestor, gutcheck, have very basic
      he/be, had/bad and hut/but checks. However, these cannot be relied on especially
      for the he/be checks. It is strongly recommended that you run ppjeeb, a Python
    port of jeebies, for he/be checks in addition to the ppgutc checks.</p>

    <h2>User options for ppgutc</h2>

    <p>On the Post Processing Workbench main page there is a place for the user to enter "User options" for ppgutc.
      You do not have to enter anything in this box. Default values are appropriate for many people. However if
    you want to customize the report, here are the options and some samples of how to use them.</p>

    <table style='width:90%'>
      <tr>
        <th>SHORT FORM</th>
        <th>LONG FORM</th>
        <th>DESCRIPTION</th>
      </tr>
      <tr>
        <td style='width:3em'>-a</td>
        <td style='width:8em'>--showall</td><td>Normally ppscan shows only the first five suspected errors
        for any one test. If you want it to show all the suspected errors for the tests,
        include the <tt>-a</tt> option on the user option line</td>
      </tr>
      <tr>
        <td>-s</td><td>--skiptests</td><td>Skip selected tests. Provide a comma-separated list of the test numbers
        you do not want to run. For the first form, set the test list off with a space 
        <tt>-s 14,82</tt> and for the second form, set the list off with an equals
        sign <tt>--skiptests=14,82</tt>. Either of these will skip running tests fourteen and eighty-two.</td>
      </tr>
      <tr>
        <td>-n</td><td>--nolist</td><td>If you don't want ppscan to report on tests that pass, include
          the <tt>-n</tt> option in your option line.</td>
      </tr>
    </table>

<p>Options are entered into the User options box separated by a space.
You can only enter a letters, numbers, a hyphen, comma, space or equal sign to create your user options line.
Here are some examples:</p>

    <table style='width:90%; margin-bottom:2em;'>
      <tr>
        <th>EXAMPLE</th>
        <th>EXPLANATION</th>
      </tr>

  <tr><td><tt>-a</tt></td><td>Show all reports for all tests, even if they passed.</td></tr>
  <tr><td><tt>-a -n</tt></td><td>Show all reports for any test that fails and don't list tests that passed.</td></tr>
  <tr><td><tt>--skiptests=14 -n</tt></td><td>Skip test 14. Don't list tests that passed.</td></tr>
</table>
DOCS
);
