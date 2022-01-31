# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata

datas = [('config/default_config.yaml', 'PyMini/config'), ('img/arrow.png', 'PyMini/img'), ('img/pan_up.png', 'PyMini/img'), ('img/x_zoom_in.png', 'PyMini/img'), ('img/x_zoom_out.png', 'PyMini/img'), ('img/y_zoom_in.png', 'PyMini/img'), ('img/y_zoom_out.png', 'PyMini/img'), ('img/zoom_in_y.png', 'PyMini/img'), ('img/loading.gif', 'PyMini/img'), ('img/logo_bw.ico', 'PyMini/img'), ('temp/', 'PyMini/temp/')]
datas += copy_metadata('numpy')

block_cipher = None


a = Analysis(['__main__.py'],
             pathex=[],
             binaries=[],
             datas=datas,
             hiddenimports=['pkg_resources.py2_warn', 'pkg_resources.markers'],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='SimplyFirev2.1.0',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
          icon='img/logo.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='SimplyFire')
