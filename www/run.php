


<!DOCTYPE html>
<html>
<body>

<?php
exec('sh /var/www/private/MusicTXT_shell.sh');

header('Location: http://www.musictxt.org/index.html?success=true');
?>


</body>
</html>
