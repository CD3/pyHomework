# -*- mode: python -*-
a = Analysis(['scripts/QuizGen.py'],
             pathex=['/home/cclark/Code/sync/projects/pyHomework'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='QuizGen',
          debug=False,
          strip=None,
          upx=True,
          console=True )
