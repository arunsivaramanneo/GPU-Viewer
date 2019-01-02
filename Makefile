

all: gpu-viewer

gpu-viewer:
	flatpak-builder build online.winehub.GPUViewer.json --force-clean --user --install