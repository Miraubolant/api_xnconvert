@echo off
echo Ex�cution des commandes cURL pour le traitement d'images
echo ===================================================

echo Traitement 1/9: imagemagick
curl -X POST -F "image=@"D:\MV\1627_481_Secret_Tolstoy_c.jpg"" -F "width=1000" -F "height=1500" -F "format=jpg" -F "resize_mode=fit" -F "keep_ratio=true" -F "resampling=hanning" -F "crop_position=center" -F "bg_color=white" -F "bg_alpha=255" https://xnconvert.miraubolant.com/process/imagemagick -o C:\Users\victo\Desktop\imagemagick_result.jpg
echo.

echo Traitement 2/9: graphicsmagick
curl -X POST -F "image=@"D:\MV\1627_481_Secret_Tolstoy_c.jpg"" -F "width=1000" -F "height=1500" -F "format=jpg" -F "resize_mode=fit" -F "keep_ratio=true" -F "resampling=hanning" -F "crop_position=center" -F "bg_color=white" -F "bg_alpha=255" https://xnconvert.miraubolant.com/process/graphicsmagick -o C:\Users\victo\Desktop\graphicsmagick_result.jpg
echo.

echo Traitement 3/9: ffmpeg
curl -X POST -F "image=@"D:\MV\1627_481_Secret_Tolstoy_c.jpg"" -F "width=1000" -F "height=1500" -F "format=jpg" -F "resize_mode=fit" -F "keep_ratio=true" -F "resampling=hanning" -F "crop_position=center" -F "bg_color=white" -F "bg_alpha=255" https://xnconvert.miraubolant.com/process/ffmpeg -o C:\Users\victo\Desktop\ffmpeg_result.jpg
echo.

echo Traitement 4/9: pillow
curl -X POST -F "image=@"D:\MV\1627_481_Secret_Tolstoy_c.jpg"" -F "width=1000" -F "height=1500" -F "format=jpg" -F "resize_mode=fit" -F "keep_ratio=true" -F "resampling=hanning" -F "crop_position=center" -F "bg_color=white" -F "bg_alpha=255" https://xnconvert.miraubolant.com/process/pillow -o C:\Users\victo\Desktop\pillow_result.jpg
echo.

echo Traitement 5/9: opencv
curl -X POST -F "image=@"D:\MV\1627_481_Secret_Tolstoy_c.jpg"" -F "width=1000" -F "height=1500" -F "format=jpg" -F "resize_mode=fit" -F "keep_ratio=true" -F "resampling=hanning" -F "crop_position=center" -F "bg_color=white" -F "bg_alpha=255" https://xnconvert.miraubolant.com/process/opencv -o C:\Users\victo\Desktop\opencv_result.jpg
echo.

echo Traitement 6/9: imageio
curl -X POST -F "image=@"D:\MV\1627_481_Secret_Tolstoy_c.jpg"" -F "width=1000" -F "height=1500" -F "format=jpg" -F "resize_mode=fit" -F "keep_ratio=true" -F "resampling=hanning" -F "crop_position=center" -F "bg_color=white" -F "bg_alpha=255" https://xnconvert.miraubolant.com/process/imageio -o C:\Users\victo\Desktop\imageio_result.jpg
echo.

echo Traitement 7/9: skimage
curl -X POST -F "image=@"D:\MV\1627_481_Secret_Tolstoy_c.jpg"" -F "width=1000" -F "height=1500" -F "format=jpg" -F "resize_mode=fit" -F "keep_ratio=true" -F "resampling=hanning" -F "crop_position=center" -F "bg_color=white" -F "bg_alpha=255" https://xnconvert.miraubolant.com/process/skimage -o C:\Users\victo\Desktop\skimage_result.jpg
echo.

echo Traitement 8/9: utility
curl https://xnconvert.miraubolant.com/health
echo.

echo Traitement 9/9: utility
curl -X POST https://xnconvert.miraubolant.com/cleanup
echo.

echo Toutes les commandes ont �t� ex�cut�es.
pause
