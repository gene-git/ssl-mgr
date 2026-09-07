#
# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c) 2026 Gene C <arch@sapience.com>
#
project('ssl-mgr', ['c'],
  version: files('src/version.txt'),
  meson_version: '>=1.10.0',
  default_options: [
    'c_std=c23',
    'warning_level=3',
    'b_pie=true',
    'prefix=/usr',
    'mandir=share/man',
    ],
)

d_etc = get_option('sysconfdir')
d_lib = get_option('libdir')
d_bin = get_option('bindir')
d_man = get_option('mandir')
d_share = get_option('datadir')

py_mod = import('python')
py = py_mod.find_installation(pure: false)
src_root = meson.project_source_root()
py_dep = py.dependency(embed: true)

inc_dir = []
lib_sources = []

#
# top-level files
#

#
# Python submodules
#
subdir('src/ssl_mgr')

#
# Deps
#

#
# Executables
#
configure_file(
  input: 'src/ssl_mgr/apps/sslm-mgr.py',
  output: 'sslm-mgr',
  copy: true,
  install_dir: d_bin,
  install_mode: 'rwxr-xr-x'
)
configure_file(
  input: 'src/ssl_mgr/apps/sslm-dhparm.py',
  output: 'sslm-dhparm',
  copy: true,
  install_dir: d_bin,
  install_mode: 'rwxr-xr-x'
)
configure_file(
  input: 'src/ssl_mgr/apps/sslm-info.py',
  output: 'sslm-info',
  copy: true,
  install_dir: d_bin,
  install_mode: 'rwxr-xr-x'
)
configure_file(
  input: 'src/ssl_mgr/apps/sslm-verify.py',
  output: 'sslm-verify',
  copy: true,
  install_dir: d_bin,
  install_mode: 'rwxr-xr-x'
)
configure_file(
  input: 'src/ssl_mgr/apps/sslm-tlsa-hash.py',
  output: 'sslm-tlsa-hash',
  copy: true,
  install_dir: d_bin,
  install_mode: 'rwxr-xr-x'
)

configure_file(
  input: 'src/ssl_mgr/libexec/sslm-auth-hook.py',
  output: 'sslm-auth-hook',
  copy: true,
  install_dir: d_lib / 'ssl-mgr',
  install_mode: 'rwxr-xr-x'
)


#
# Install
#
s_etc = 'src/data/etc'
s_scripts = './scripts'
s_license = 'src/data/license'
s_changelog = 'src/data/changelog'
s_docs = 'src/data/docs'
manual = 'ssl-mgr.pdf'

# 
# /etc/ssl-mgr
# 

install_subdir(
  [
    s_etc / 'examples',
  ],
  install_dir: d_etc / 'ssl-mgr',
  strip_directory: false
)


# 
# /usr/share/ssl-mgr/docs
# 
install_data(
  [
    s_docs / manual,
  ],
  install_dir: d_share / 'ssl-mgr/docs'
)

install_subdir(
  [
    s_docs / 'html',
  ],
  install_dir: d_share / 'ssl-mgr/docs',
  strip_directory: false
)

# 
# /usr/share/ssl-mgr 
# 
install_data(
  [
    'README.rst',
    s_changelog / 'Changelog.rst',
    'packaging/PKGBUILD',
    'packaging/.nvchecker.toml',
    'packaging/Changelog',
  ],
  install_dir: d_share / 'ssl-mgr'
)

# 
# /usr/share/licenses/ssl-mgr 
# 
install_data(
  [
    s_license / 'License-gpl-2.0.txt',
    s_license / 'License.rst',
  ],
  install_dir: d_share / 'licenses/ssl-mgr'
)


