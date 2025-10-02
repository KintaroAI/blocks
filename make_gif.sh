ffmpeg -framerate 30 -start_number 500 -i output/frame_%06d.png -vf "fps=30,palettegen" output/palette.png
ffmpeg -framerate 30 -start_number 500 -i output/frame_%06d.png -i output/palette.png -filter_complex "fps=30[x];[x][1:v]paletteuse" output.gif
