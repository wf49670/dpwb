<?php

   if(isset($_FILES['zipfile'])){

      echo "You selected: ".$_POST["requested_test"] . "<br/>";
      flush();

      # place to save error messages
      $errors= array();

      # have a working folder for the Workbench
      $work="/home/uploads/incoming/Users/rfrank";  # temporary
      # $uploads_dir="/home/uploads/incoming";
      # $work=$uploads_dir."/"."wb";

      # unique name as workbench project number
      $wbpn = uniqid('wb'); 

      # allow only "zip" file extension
      $extensions= array("zip");  

      $finfo = finfo_open(); # don't trust user file type
      if (!$finfo) {
          echo "Opening fileinfo database failed";
          exit();
      }

      # get the information about the file
      $file_name=$_FILES['zipfile']['name'];
      $file_size=$_FILES['zipfile']['size'];
      $file_tmp=$_FILES['zipfile']['tmp_name'];
      $file_type=$_FILES['zipfile']['type'];
      # $file_ext=strtolower(end(explode('.',$_FILES['textfile']['name'])));
      $file_ext=pathinfo($file_name, PATHINFO_EXTENSION);
    
      # validate what the user sent us
      # was a file specified?
      if ($_FILES['zipfile']['size'] == 0) {
         $errors[]='error: no file was specified';
      }
      # do they claim it's an allowed type?
      if(in_array($file_ext,$extensions)=== false){
         $errors[]="Please upload a .zip file";
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
      if ($av_retval == 0) {
        echo "virus scan: PASS.<br/>";
        flush();
      } else {
        echo "virus scan failed. exiting";
        exit(1);
      }

      # we apparently have a valid zip file so we can burst it.
      if(empty($errors)==true){
                  
        # create a folder for this workbench project
        mkdir($work."/".$wbpn, 0755); # i.e. results/p8177215

        # put the user's zip file into the wbp folder
        $target_name=$work."/".$wbpn."/".$wbpn.'.zip';
        move_uploaded_file($file_tmp, $target_name);
         
        # burst
        $zipArchive = new ZipArchive();
        $result = $zipArchive->open($target_name);
        if ($result === TRUE) {
          $zipArchive ->extractTo($work."/".$wbpn);
          $zipArchive ->close();
          echo "unzipped to (user:rfrank) upload folder<br/>";
          flush();
        } else {
          echo("unable to unzip uploaded file");
          exit(1);
        }

      } else {
        # there were errors and unzip not attempted
        print_r($errors); 
      }
      finfo_close($finfo);

      # the radio buttons tell us what test they want.
      # dispatch here...

      if ($_POST["requested_test"]=="ppgutc") {

        # determine name of the uploaded -utf8 text file
        $paths = glob($work."/".$wbpn."/*-utf8.txt");
        echo "source file: ".$paths[0]."<br/>";

        # run the program here
        $scommand = 'python3 ppgutc.py' .
                     ' -i ' . $paths[0] .
                     ' -o ' . $work."/".$wbpn."/ppgutc-result.txt";
        $command = escapeshellcmd($scommand);
        echo "command: ". $command . "<br/>";
        $output = shell_exec($command);          
        echo "result is ".$wbpn."/ppgutc-result.txt in your user folder";
      } 

      if ($_POST["requested_test"]=="pplev") {

        # determine name of the uploaded -utf8 text file
        $paths = glob($work."/".$wbpn."/*-utf8.txt");
        echo("source file: ".$paths[0]."<br/>");

        # run the program here
        $scommand = 'python3 pplev.py' .
                     ' -i ' . $paths[0] .
                     ' -o ' . $work."/".$wbpn."/pplev-result.txt";
        $command = escapeshellcmd($scommand);
        echo "command: ". $command . "<br/>";
        $output = shell_exec($command);          
        echo "result is ".$wbpn."/pplev-result.txt in your user folder";
      } 

   };
?>
