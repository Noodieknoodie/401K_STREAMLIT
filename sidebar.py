import streamlit as st

# Handle sidebar state
if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = 'collapsed'

with st.sidebar:
    st.markdown("### COMING SOON")
