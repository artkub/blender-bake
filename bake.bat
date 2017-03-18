cd %~dp0
call config.bat
call clear_output.bat
"%blender%" -y -P .\bake.py %1
