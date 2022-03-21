

all: gpu-viewer

gpu-viewer:
	flatpak-builder build online.winehub.GPUViewer.yml --force-clean --user --install
