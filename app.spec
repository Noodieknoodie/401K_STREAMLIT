# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata

# Add all required package metadata
datas = []
datas += copy_metadata('streamlit')
datas += copy_metadata('importlib_metadata')
datas += copy_metadata('altair')
datas += copy_metadata('numpy')
datas += copy_metadata('pandas')
datas += copy_metadata('streamlit_extras')

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'streamlit',
        'streamlit.runtime',
        'streamlit.runtime.scriptrunner',
        'streamlit.runtime.scriptrunner.magic_funcs',
        'streamlit.runtime.caching',
        'streamlit.runtime.metrics_util',
        'streamlit_extras',
        'altair',
        'numpy',
        'pandas',
        'pages_new.main_summary.summary',
        'pages_new.client_display_and_forms.client_dashboard',
        'pages_new.manage_clients.client_management',
        'pages_new.bulk_payment.bulk_entry',
        'utils.utils',
        'utils.client_data'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='401k_payment_tracker',  # Updated name
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Keep console for error visibility
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None  # We can add an icon if you want one
)
