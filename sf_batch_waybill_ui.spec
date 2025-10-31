# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for sf_batch_waybill_ui

使用 collect_submodules 自动收集 selenium / openpyxl 子模块，避免运行时缺少库。
可选打包 msedgedriver.exe (若与本 spec 同目录)。
构建命令 (PowerShell):
  pyinstaller --clean --onefile sf_batch_waybill_ui.spec
"""

from PyInstaller.utils.hooks import collect_submodules
import os

hidden = []
hidden += collect_submodules('selenium')
hidden += collect_submodules('openpyxl')

# 可选数据文件: EdgeDriver 若存在则一并打包
datas = []
for candidate in ['msedgedriver.exe']:
    if os.path.exists(candidate):
        datas.append((candidate, '.'))

a = Analysis(
    ['sf_batch_waybill_ui.py'],
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
    name='sf_batch_waybill_ui',
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
