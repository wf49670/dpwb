<?php

   function getUserIP() {
       if( array_key_exists('HTTP_X_FORWARDED_FOR', $_SERVER) && !empty($_SERVER['HTTP_X_FORWARDED_FOR']) ) {
           if (strpos($_SERVER['HTTP_X_FORWARDED_FOR'], ',')>0) {
               $addr = explode(",",$_SERVER['HTTP_X_FORWARDED_FOR']);
               return trim($addr[0]);
           } else {
               return $_SERVER['HTTP_X_FORWARDED_FOR'];
           }
       }
       else {
           return $_SERVER['REMOTE_ADDR'];
       }
   }

   if(isset($_FILES['textfile'])){

      # have a folder ready
      $work="./results/";
      $extensions= array("txt");  # allow only .txt files
      $extgood= array("txt");  # goodwords file must be .txt
      $errors= array();

      # every run has a unique descriptor
      $pid = uniqid('p'); # unique project id used for processing

      ##### process the text file #####

      $file_name=$_FILES['textfile']['name'];
      $file_size=$_FILES['textfile']['size'];
      $file_tmp=$_FILES['textfile']['tmp_name'];
      $file_type=$_FILES['textfile']['type'];
      #$file_ext=strtolower(end(explode('.',$_FILES['textfile']['name'])));
      $file_ext=pathinfo($file_name, PATHINFO_EXTENSION);

      # was a input text file specified?
      if ($_FILES['textfile']['size'] > 0) {
         # do they claim it's a .txt file?
         if(in_array($file_ext,$extensions)=== false){
            $errors[]="extension not allowed, please choose a .txt file.";
         }
         # is it small enough?
         if($file_size > 4194304){
            $errors[]='File size must be less than 4 MB';
         }
      } else {
         $errors[]='error: no file was specified';
      }

      $date = date('Y-m-d H:i:s');
      $ipaddress = getUserIP();
      file_put_contents("./results/access.log", $date." ppgutc ".$ipaddress." ".$pid." ".$file_name."\n", FILE_APPEND);

      ##### process the "verbose" checkbox #####
      $showall=false;
      if(isset($_POST['verbose']) && $_POST['verbose'] == 'Yes') {
         $showall=true;
      }

      if(empty($errors)==true){
         # no errors so far. still need to scan for viruses
         $fname1 = $pid . '.txt';  # source text input file

         /*cl_setlimits(5, 1000, 200, 0, 10485760);
         if ($malware = cl_scanfile($file_tmp)) {
           $errors[] = 'We have Malware: '.$malware.'<br>ClamAV version: '.clam_get_version(); }
         }*/

         move_uploaded_file($file_tmp, $work.$fname1);
         $fname2 = $pid . '-2.txt';  # output file

         # check uploaded file to have acceptable signature
         $filename = $work.$fname1;  # complete source file name
         $finfo = finfo_open(); # don't trust user-specified file type
         $filetype = finfo_file($finfo, $filename);
         finfo_close($finfo);
         if ( strpos($filetype,"UTF-8") === false &&
     		  strpos($filetype,"ASCII") === false &&
     		  strpos($filetype,"ISO-8859") === false	) {
            print_r("file must be UTF-8, Latin-1 or ASCII. (" . $filetype . ")");
            exit(1);
         }

         # run the program here
         $scommand = './ppgutc.py' .
                     ' -i ' . $work.$fname1 .
                     ' -o ' . $work.$fname2;

         if ($showall) {
            $scommand .= ' -a ';
         }

         $command = escapeshellcmd($scommand);
         # echo $command;  ## DEBUG
         $output = shell_exec($command);
         # echo $output;  ## DEBUG

         echo "<!doctype html>";
         echo "<html lang=\"en\">";
         echo "<head>";
         echo "<link rel=\"stylesheet\" type=\"text/css\" href=\"asylumcs.css\">";
         echo "</head>";
         echo "<body>";
         echo "<p><b>Utility: ppgutc</b></p>";

         if (file_exists("results/${fname2}")){
           echo "<p>results available: <a href='http://pgdp.org/~rfrank/results/${fname2}'>here</a>.<br/>Left click to view. Right click to download.</p>";
         } else {
           echo "<p>Whoops! Something went wrong and no output was generated.<br/>
             Please email rfrank@rfrank.net and include this filename: ${fname2}</p>";
         }    

         echo "</body>";
         echo "</html>";
      }else{
         print_r($errors);
      }

   };
?>
