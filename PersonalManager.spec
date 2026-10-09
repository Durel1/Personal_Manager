# Build on Windows: python -m PyInstaller --clean --noconfirm PersonalManager.spec
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files

root = Path(SPECPATH)
datas = collect_data_files('customtkinter')
datas += collect_data_files('reportlab',includes=['fonts/*.ttf'])
a = Analysis([str(root/'main.py')],pathex=[str(root)],binaries=[],datas=datas,
             hiddenimports=['matplotlib.backends.backend_tkagg','openpyxl','reportlab.pdfbase.ttfonts'],
             hookspath=[],hooksconfig={},runtime_hooks=[],excludes=[],noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz,a.scripts,[],exclude_binaries=True,name='PersonalManager',debug=False,
          bootloader_ignore_signals=False,strip=False,upx=False,console=False,icon=str(root/'icone.ico'))
coll = COLLECT(exe,a.binaries,a.datas,strip=False,upx=False,name='PersonalManager')
