<!DOCTYPE html>
<html>
<body>

<?php

if(!empty($_POST['data'])){
$data = $_POST['data'];
$fname = "a.txt";

$file = fopen("upload/" .$fname, 'w');//creates new file
fwrite($file, $data);
fclose($file);
}

exec('sh /var/www/private/MusicTXT_shell.sh');

header('Location: http://www.musictxt.org/index.html?success=true');
?>


</body>
</html>
