import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.title("401K Payment Tracker")
        st.subheader("Navigation")
        
        # Navigation buttons with icons
        nav_options = [
            ('📊 Quarterly Summary', 'Quarterly Summary'),
            ('👥 Client Dashboard', 'Client Dashboard'),
            ('⚙️ Manage Clients', 'Manage Clients'),
            ('📝 Bulk Payment Entry', 'Bulk Payment Entry')
        ]
        
        for icon_label, page in nav_options:
            if st.button(icon_label, key=f"nav_{page}"):
                st.session_state.current_page = page
                if page != 'Client Dashboard':
                    st.session_state.selected_client = None

        st.markdown("""
        <style>
            .sidebar .sidebar-content {
                background-color: #f8f9fa;
            }
            .stButton>button {
                width: 100%;
                margin-bottom: 10px;
                display: flex;
                align-items: center;
                justify-content: flex-start;
            }
        </style>
        """, unsafe_allow_html=True) 