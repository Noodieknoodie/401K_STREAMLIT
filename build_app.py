import PyInstaller.__main__
import os
import sys

def build_app():
    # Get the absolute path of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    PyInstaller.__main__.run([
        'app.py',  # Your main streamlit app file
        '--name=401K_Manager',
        '--onefile',
        '--windowed',
        '--add-data=pages_new;pages_new',
        '--add-data=utils;utils',
        '--add-data=DATABASE;DATABASE',
        '--hidden-import=streamlit',
        '--hidden-import=pandas',
        '--hidden-import=plotly',
        '--hidden-import=sqlite3',
        '--hidden-import=streamlit.runtime.scriptrunner',
        '--hidden-import=streamlit.runtime.scriptrunner.magic_funcs',
        '--hidden-import=streamlit.runtime.caching',
        '--hidden-import=streamlit.runtime.stats',
        '--collect-data=streamlit',
        '--collect-data=streamlit_extras',
        '--collect-all=streamlit_extras',
        '--collect-all=plotly',
        '--collect-all=pandas',
        '--noconfirm',
        '--clean',
        # Exclude unnecessary packages to reduce size
        '--exclude-module=matplotlib',
        '--exclude-module=notebook',
        '--exclude-module=jupyter',
        '--exclude-module=IPython'
    ])

if __name__ == '__main__':
    build_app() 