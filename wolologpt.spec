# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

# Collect all files from the images directory
image_files = [
    ('images/logo.jpg', 'images'),
    ('images/check.png', 'images'),
    ('images/x.png', 'images'),
    # Add any other image files here
]

# Add counter data files
counter_data_files = [
    ('counters_data/aoe2_counters_normal.json', 'counters_data'),
    ('counters_data/aoe2_counter_unique_gemini.json', 'counters_data'),
]

# Add audio files
audio_files = []
for root, dirs, files in os.walk('audio'):
    for file in files:
        audio_files.append((os.path.join(root, file), os.path.join('audio', os.path.relpath(root, 'audio'))))

a = Analysis(['main.py'],
             pathex=[],
             binaries=[],
             datas=image_files + counter_data_files + audio_files + [
                 ('user_info.json', '.'), 
                 ('config.py', '.'), 
                 ('game_actions.py', '.'), 
                 ('resource_alerts_thread.py', '.'), 
                 ('audio_manager.py', '.'), 
                 ('utils.py', '.'), 
                 ('gui_layout.py', '.'), 
                 ('ai_analysis.py', '.'), 
                 ('color_flash.py', '.'), 
                 ('api_client.py', '.')
             ],
             hiddenimports=['PyQt6', 'keyboard', 'requests', 'json', 'tkinter', 'pygame'],
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
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name='WoloLOGPT',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
          icon='images/logo.ico')
