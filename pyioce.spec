# -*- mode: python -*-
a = Analysis(['pyioce.py'],
             pathex=['/Users/seagill/Desktop/PyIOCe'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='pyioce',
          debug=False,
          strip=None,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='PyIOCe')
app = BUNDLE(coll,
             name='PyIOCe.app',
             icon=None)
