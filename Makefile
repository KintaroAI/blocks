# Neuro Flow - Animated Blocks & Curved Arrows
# Makefile for common tasks

.PHONY: help install run-blocks run-cerebellum clean frames gif mp4

# Default target
help:
	@echo "Available targets:"
	@echo "  install        - Install Python dependencies"
	@echo "  run-blocks     - Run the main brain visualization (blocks.py)"
	@echo "  run-cerebellum - Run the cerebellum/motor pathway visualization"
	@echo "  frames         - Generate frames for animation (saves to output/)"
	@echo "  gif            - Create animated GIF from frames"
	@echo "  mp4            - Create MP4 video from frames"
	@echo "  clean          - Remove generated files"

# Install dependencies
install:
	pip install -r requirements.txt

# Run the main brain visualization
run-blocks:
	python blocks.py

# Run the cerebellum visualization
run-cerebellum:
	python cerebellum.py

# Generate frames for animation
frames:
	mkdir -p output
	python blocks.py --save-prefix output/frame_ --frame-skip 2 --max-frames 300

# Create animated GIF
gif: frames
	./make_gif.sh

# Create MP4 video
mp4: frames
	./make_mp4.sh

# Clean up generated files
clean:
	rm -rf output/
	rm -f *.gif *.mp4
	rm -rf __pycache__/
