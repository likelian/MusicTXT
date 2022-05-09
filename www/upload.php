<!DOCTYPE html>
<html>
<body>

<?php



if (($_FILES['my_file']['name']!="")){
// Where the file is going to be stored
 $target_dir = "upload/";
 $file = $_FILES['my_file']['name'];
 $path = pathinfo($file);
 $filename = $path['filename'];
 $ext = $path['extension'];
 $temp_name = $_FILES['my_file']['tmp_name'];
 $path_filename_ext = $target_dir.$filename.".".$ext;

// Check if file already exists
if (file_exists($path_filename_ext)) {
 unlink($path_filename_ext);
 move_uploaded_file($temp_name,$path_filename_ext);
 header('Location: http://www.musictxt.org/index.html?success=true');
 }else{
 move_uploaded_file($temp_name,$path_filename_ext);
 header('Location: http://www.musictxt.org/index.html?success=true');
 }
}
?>

</body>
</html>
