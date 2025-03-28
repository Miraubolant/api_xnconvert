@echo off
echo Exécution des commandes cURL pour le traitement d'images
echo ===================================================

echo Traitement 1/13: imagemagick
curl -X POST -F "image=@"D:\MV\4791_026_Leman-Slim-Plume-Terre-d'Ombre-RH-M_c.png"" -F "width=1000" -F "height=1500" -F "format=jpg" -F "resize_mode=fit" -F "keep_ratio=true" -F "resampling=hanning" -F "crop_position=center" -F "bg_color=white" -F "bg_alpha=255" https://xnconvert.miraubolant.com/process/imagemagick -o C:\Users\victo\Desktop\imagemagick_result.jpg
echo.

echo Traitement 2/13: graphicsmagick
curl -X POST -F "image=@"D:\MV\4791_026_Leman-Slim-Plume-Terre-d'Ombre-RH-M_c.png"" -F "width=1000" -F "height=1500" -F "format=jpg" -F "resize_mode=fit" -F "keep_ratio=true" -F "resampling=hanning" -F "crop_position=center" -F "bg_color=white" -F "bg_alpha=255" https://xnconvert.miraubolant.com/process/graphicsmagick -o C:\Users\victo\Desktop\graphicsmagick_result.jpg
echo.

echo Traitement 3/13: ffmpeg
curl -X POST -F "image=@"D:\MV\4791_026_Leman-Slim-Plume-Terre-d'Ombre-RH-M_c.png"" -F "width=1000" -F "height=1500" -F "format=jpg" -F "resize_mode=fit" -F "keep_ratio=true" -F "resampling=hanning" -F "crop_position=center" -F "bg_color=white" -F "bg_alpha=255" https://xnconvert.miraubolant.com/process/ffmpeg -o C:\Users\victo\Desktop\ffmpeg_result.jpg
echo.

echo Traitement 4/13: vips
curl -X POST -F "image=@"D:\MV\4791_026_Leman-Slim-Plume-Terre-d'Ombre-RH-M_c.png"" -F "width=1000" -F "height=1500" -F "format=jpg" -F "resize_mode=fit" -F "keep_ratio=true" -F "resampling=hanning" -F "crop_position=center" -F "bg_color=white" -F "bg_alpha=255" https://xnconvert.miraubolant.com/process/vips -o C:\Users\victo\Desktop\vips_result.jpg
echo.

echo Traitement 5/13: pillow
curl -X POST -F "image=@"D:\MV\4791_026_Leman-Slim-Plume-Terre-d'Ombre-RH-M_c.png"" -F "width=1000" -F "height=1500" -F "format=jpg" -F "resize_mode=fit" -F "keep_ratio=true" -F "resampling=hanning" -F "crop_position=center" -F "bg_color=white" -F "bg_alpha=255" https://xnconvert.miraubolant.com/process/pillow -o C:\Users\victo\Desktop\pillow_result.jpg
echo.

echo Traitement 6/13: nconvert
curl -X POST -F "image=@"D:\MV\4791_026_Leman-Slim-Plume-Terre-d'Ombre-RH-M_c.png"" -F "width=1000" -F "height=1500" -F "format=jpg" -F "resize_mode=fit" -F "keep_ratio=true" -F "resampling=hanning" -F "crop_position=center" -F "bg_color=white" -F "bg_alpha=255" https://xnconvert.miraubolant.com/process/nconvert -o C:\Users\victo\Desktop\nconvert_result.jpg
echo.

echo Traitement 7/13: opencv
curl -X POST -F "image=@"D:\MV\4791_026_Leman-Slim-Plume-Terre-d'Ombre-RH-M_c.png"" -F "width=1000" -F "height=1500" -F "format=jpg" -F "resize_mode=fit" -F "keep_ratio=true" -F "resampling=hanning" -F "crop_position=center" -F "bg_color=white" -F "bg_alpha=255" https://xnconvert.miraubolant.com/process/opencv -o C:\Users\victo\Desktop\opencv_result.jpg
echo.

echo Traitement 8/13: imageio
curl -X POST -F "image=@"D:\MV\4791_026_Leman-Slim-Plume-Terre-d'Ombre-RH-M_c.png"" -F "width=1000" -F "height=1500" -F "format=jpg" -F "resize_mode=fit" -F "keep_ratio=true" -F "resampling=hanning" -F "crop_position=center" -F "bg_color=white" -F "bg_alpha=255" https://xnconvert.miraubolant.com/process/imageio -o C:\Users\victo\Desktop\imageio_result.jpg
echo.

echo Traitement 9/13: gimp
curl -X POST -F "image=@"D:\MV\4791_026_Leman-Slim-Plume-Terre-d'Ombre-RH-M_c.png"" -F "width=1000" -F "height=1500" -F "format=jpg" -F "resize_mode=fit" -F "keep_ratio=true" -F "resampling=hanning" -F "crop_position=center" -F "bg_color=white" -F "bg_alpha=255" https://xnconvert.miraubolant.com/process/gimp -o C:\Users\victo\Desktop\gimp_result.jpg
echo.

echo Traitement 10/13: skimage
curl -X POST -F "image=@"D:\MV\4791_026_Leman-Slim-Plume-Terre-d'Ombre-RH-M_c.png"" -F "width=1000" -F "height=1500" -F "format=jpg" -F "resize_mode=fit" -F "keep_ratio=true" -F "resampling=hanning" -F "crop_position=center" -F "bg_color=white" -F "bg_alpha=255" https://xnconvert.miraubolant.com/process/skimage -o C:\Users\victo\Desktop\skimage_result.jpg
echo.

echo Traitement 11/13: pyvips
curl -X POST -F "image=@"D:\MV\4791_026_Leman-Slim-Plume-Terre-d'Ombre-RH-M_c.png"" -F "width=1000" -F "height=1500" -F "format=jpg" -F "resize_mode=fit" -F "keep_ratio=true" -F "resampling=hanning" -F "crop_position=center" -F "bg_color=white" -F "bg_alpha=255" https://xnconvert.miraubolant.com/process/pyvips -o C:\Users\victo\Desktop\pyvips_result.jpg
echo.

echo Traitement 12/13: utility
curl https://xnconvert.miraubolant.com/health
echo.

echo Traitement 13/13: utility
curl -X POST https://xnconvert.miraubolant.com/cleanup
echo.

echo Toutes les commandes ont été exécutées.
pause
