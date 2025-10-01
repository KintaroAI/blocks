ffmpeg -framerate 30 -start_number 1 -i brain%06d.png -vf "fps=30,palettegen" palette.png
ffmpeg -framerate 30 -start_number 1 -i brain%06d.png -i palette.png -filter_complex "fps=30[x];[x][1:v]paletteuse" output.gif
