# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 配置文件
用于自定义打包选项

使用方法:
    pyinstaller damage_calculator.spec
"""

block_cipher = None

# 分析需要包含的文件
a = Analysis(
    ['ui.py'],
    pathex=[],
    binaries=[],
    datas=[('characters.yml', '.')],  # 包含配置文件
    hiddenimports=['yaml'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='伤害计算器',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台（GUI程序）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='icon.ico',  # 如果有图标的话
)
