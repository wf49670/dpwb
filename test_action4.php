<?php

   if(isset($_FILES['userfile'])){
      $errors= array();                 # place to save error messages
      $work="t";                        # have a working folder for the Workbench
      $wbpn = uniqid('wb');             # unique name as workbench project number
      $extensions= array("txt","zip");  # allow "txt" or "zip" file extension

      # get the information about the file
      $file_name=$_FILES['userfile']['name'];
      $file_size=$_FILES['userfile']['size'];
      $file_tmp=$_FILES['userfile']['tmp_name'];
      $file_type=$_FILES['userfile']['type'];
      $file_ext=pathinfo($file_name, PATHINFO_EXTENSION);

      # validate what the user sent us
      # was a file specified?
      if ($_FILES['userfile']['size'] == 0) {
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

        # if a zip file was uploaded, burst it in the project folder
        if ($file_ext=="zip") {

            # save zip to project folder
            $target_name=$work."/".$wbpn."/".$file_name;
            move_uploaded_file($file_tmp, $target_name);

            # burst
            $zipArchive = new ZipArchive();
            $result = $zipArchive->open($target_name);
            if ($result === TRUE) {
              $zipArchive ->extractTo($work."/".$wbpn);
              $zipArchive ->close();
            } else {
              print_r("unable to unzip uploaded file");
              exit(1);
            }
        } else {
            # if a text file was uploaded, store it directly in the project folder
            $target_name=$work."/".$wbpn."/".$file_name;
            move_uploaded_file($file_tmp, $target_name);
        }

      } else {
        # we had errors and cannot continue
        print_r($errors);
        exit(1);
      }

      # isolate the name of the files for this run
      $user_textfile="";
      $user_htmlfile="";
      $user_wordfile="";
      if ($file_ext=="txt") {
        $user_textfile=$target_name;
      }
      if ($file_ext=="zip") {
        foreach (glob($work."/".$wbpn."/*.txt") as $filename) {
            if (basename($filename)=="good_words.txt"){
                $user_wordfile=$filename;
            } else {
                $user_textfile=$filename;
            }
        }
        foreach (glob($work."/".$wbpn."/*.html") as $filename) {
           $user_htmlfile=$filename;
        }
      }

      # the radio buttons tell us what test they want.
      # dispatch here...

      if ($_POST["requested_test"]=="ppgutc") {

        # run the program here
        $scommand = 'python3 ppgutc.py' .
                     ' -i ' . $user_textfile .
                     ' -o ' . $work."/".$wbpn."/result.txt";
        $command = escapeshellcmd($scommand);
        #echo "command: ". $command . "<br/>";
        $output = shell_exec($command);
      }

      if ($_POST["requested_test"]=="pplev") {

        # run the program here
        $scommand = 'python3 pplev.py' .
                     ' -i ' . $user_textfile .
                     ' -o ' . $work."/".$wbpn."/result.txt";
        $command = escapeshellcmd($scommand);
        #echo "command: ". $command . "<br/>";
        $output = shell_exec($command);
      }

      if ($_POST["requested_test"]=="ppsmq") {

        # run the program here
        $scommand = 'python3 ppsmq.py' .
                     ' -i ' . $user_textfile .
                     ' -o ' . $work."/".$wbpn."/result.txt";
        $command = escapeshellcmd($scommand);
        # echo "command: ". $command . "<br/>";
        $output = shell_exec($command);
      }

      if ($_POST["requested_test"]=="ppspell") {

        # run the program here
        if ($user_wordfile!=""){
            $scommand = 'python3 ppspell.py' .
                     ' -i ' . $user_textfile .
                     ' -g ' . $user_wordfile .
                     ' -o ' . $work."/".$wbpn."/result.txt";

        } else {
            $scommand = 'python3 ppspell.py' .
                     ' -i ' . $user_textfile .
                     ' -o ' . $work."/".$wbpn."/result.txt";
        }
        $command = escapeshellcmd($scommand);
        # echo "command: ". $command . "<br/>";
        $output = shell_exec($command);
      }   

      if ($_POST["requested_test"]=="ppjeeb") {

        # run the program here
        $scommand = 'python3 ppjeeb.py' .
                     ' -i ' . $user_textfile .
                     ' -o ' . $work."/".$wbpn."/result.txt";
        $command = escapeshellcmd($scommand);
        # echo "command: ". $command . "<br/>";
        $output = shell_exec($command);
      }  

      if ($_POST["requested_test"]=="pptxt") {

        # run the program here
        $scommand = 'python3 pptxt.py' .
                     ' -i ' . $user_textfile .
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
