# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for sf_waybill_detail

自动收集 selenium / openpyxl 子模块，支持离线 EdgeDriver 打包。
构建命令:
  pyinstaller --clean --onefile sf_waybill_detail.spec
"""
from PyInstaller.utils.hooks import collect_submodules
import os

hidden = []
hidden += collect_submodules('selenium')
# openpyxl 在单票脚本中可能不需要，但收集不影响体积太多，避免未来扩展报错
hidden += collect_submodules('openpyxl')

datas = []
if os.path.exists('msedgedriver.exe'):
    datas.append(('msedgedriver.exe', '.'))

a = Analysis(
    ['sf_waybill_detail.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='sf_waybill_detail',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)