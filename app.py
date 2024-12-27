# app.py
import os
import sys
import streamlit.web.bootstrap
from streamlit.web import bootstrap
from streamlit import config as _config

def run_app():
    # Set Streamlit configuration
    _config.set_option('server.address', 'localhost')
    _config.set_option('server.port', 8501)
    _config.set_option('browser.serverAddress', 'localhost')
    _config.set_option('theme.primaryColor', '#0066cc')
    
    # Get the directory containing the executable
    if getattr(sys, 'frozen', False):
        # Running as compiled
        base_dir = sys._MEIPASS
    else:
        # Running as script
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Set the working directory
    os.chdir(base_dir)
    
    # Run the Streamlit app
    args = []
    bootstrap.run(
        "pages_new/client_dashboard.py",
        "streamlit run",
        args,
        flag_options={},
    )

if __name__ == "__main__":
    run_app()
