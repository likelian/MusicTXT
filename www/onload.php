<!DOCTYPE html>
<html>
<body>

<?php



move_uploaded_file("/var/www/html/default/a.pdf","/var/www/html/download");
header('Location: http://www.musictxt.org/index.html?success=true');


?>

</body>
</html>
