<?php

   if(isset($_FILES['txtfile'])){

      $errors= array();           # place to save error messages
      $work="t";                  # have a working folder for the Workbench
      $wbpn = uniqid('wb');       # unique name as workbench project number
      $extensions= array("txt");  # allow only "txt" file extension

      # get the information about the file
      $file_name=$_FILES['txtfile']['name'];
      $file_size=$_FILES['txtfile']['size'];
      $file_tmp=$_FILES['txtfile']['tmp_name'];
      $file_type=$_FILES['txtfile']['type'];
      $file_ext=pathinfo($file_name, PATHINFO_EXTENSION);

      # validate what the user sent us
      # was a file specified?
      if ($_FILES['txtfile']['size'] == 0) {
         $errors[]='error: no file was specified';
      }
      # do they claim it's an allowed type?
      if(in_array($file_ext,$extensions)=== false){
         $errors[]="Please upload a .txt file";
      }
      # is it small enough?
      if($file_size > 31457280){
         $errors[]="File size must be less than 30 MB";
      }

      # does it pass the anti-virus tests
      $av_test_result = array();
      $av_retval=0;
      $cmd = "/usr/bin/clamscan -- " . escapeshellcmd($file_tmp);
      exec($cmd, $av_test_result, $av_retval);
      if ($av_retval != 0) {
        echo "virus scan failed. exiting";
        exit(1);
      }

      # if no errors, proceed
      if(empty($errors)==true){

        # create a separate folder for each workbench project
        mkdir($work."/".$wbpn, 0755);

        # put the user's file into the wbp folder with a new name
        $target_name=$work."/".$wbpn."/".$wbpn.'.txt';
        move_uploaded_file($file_tmp, $target_name);
      } else {
        # we had errors and cannot continue
        print_r($errors);
      }

      # the radio buttons tell us what test they want.
      # dispatch here...

      if ($_POST["requested_test"]=="ppgutc") {

        # run the program here
        $scommand = 'python3 ppgutc.py' .
                     ' -i ' . $target_name .
                     ' -o ' . $work."/".$wbpn."/result.txt";
        $command = escapeshellcmd($scommand);
        #echo "command: ". $command . "<br/>";
        $output = shell_exec($command);
      }

      if ($_POST["requested_test"]=="pplev") {

        # run the program here
        $scommand = 'python3 pplev.py' .
                     ' -i ' . $target_name .
                     ' -o ' . $work."/".$wbpn."/result.txt";
        $command = escapeshellcmd($scommand);
        #echo "command: ". $command . "<br/>";
        $output = shell_exec($command);
      }

      if ($_POST["requested_test"]=="ppsmq") {

        # run the program here
        $scommand = 'python3 ppsmq.py' .
                     ' -i ' . $target_name .
                     ' -o ' . $work."/".$wbpn."/result.txt";
        $command = escapeshellcmd($scommand);
        # echo "command: ". $command . "<br/>";
        $output = shell_exec($command);
      }

      echo "<!doctype html>";
      echo "<html lang=\"en\">";
      echo "<head>";
      echo "  <link rel='stylesheet' type='text/css' href='workbench.css'>";
      echo "</head>";
      echo "<body>";
      echo "<p><b>DP Workbench Results</b></p>";

      if (file_exists("${work}/${wbpn}/result.txt")){
       echo "<p>results available: <a href='${work}/${wbpn}/result.txt'>here</a>.<br/>
       Left click to view. Right click to download.</p>";
      } else {
       echo "<p>Whoops! Something went wrong and no output was generated.<br/>
         Please email rfrank@rfrank.net and include this project name: ${wbpn}</p>";
      }

      echo "</body>";
      echo "</html>";

   };
?>
