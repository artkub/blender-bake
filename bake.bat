set blender=c:\program files\blender foundation\blender\blender.exe
cd %~dp0
rmdir /S /Q .\output
mkdir .\output
"%blender%" -y -P .\bake.py %1
