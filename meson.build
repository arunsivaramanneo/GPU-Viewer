project('gpu-viewer',
  license: 'GPL-3.0-or-later',
  meson_version: '>=0.49.0'
)

APPLICATION_ID = 'io.github.arunsivaramanneo.GPUViewer'

subdir('data')
bin_conf = configuration_data()
bin_conf.set('datadir', get_option('prefix') / get_option('datadir'))

configure_file(
  input: 'gpu-viewer.in',
  output: 'gpu-viewer',
  configuration: bin_conf,
  install_dir: get_option('bindir')
)

install_data([ 'About_GPU_Viewer', 'Change Log.md', 'LICENSE', 'README.md' ])

install_subdir('Files',
  install_dir: get_option('datadir') / 'gpu-viewer')
install_subdir('Images',
  install_dir: get_option('datadir') / 'gpu-viewer')
