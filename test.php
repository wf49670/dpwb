<!doctype html>
<html lang="en">
  <head>
	<meta charset="utf-8">
	<meta name=viewport content="width=device-width, initial-scale=1">
    <title>testing Zip upload/scan</title>
  </head>

  <body>

      <form action="test_action.php" method="POST" enctype="multipart/form-data">
         Zip file: <input type="file" name="zipfile" /><br/>
         <input type="submit" name="upload"/>
      </form>

  </body>
</html>

