datas=[ ('pint/default_en.txt', 'pint')
      , ('pint/constants_en.txt', 'pint')
      ]
a = Analysis(['scripts/QuizGen.py'],
             datas=datas,
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
