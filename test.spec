import sys
sys.setrecursionlimit(50000)
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['test.py'],
             pathex=['D:\\Users\\lenovo\\Desktop\\Ameth\\upwork\\Walmart bot'],
             binaries=[],
             datas=[],
             hiddenimports=['certifi'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=True,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='test',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
