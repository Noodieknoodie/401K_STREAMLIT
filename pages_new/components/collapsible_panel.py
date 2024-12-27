import streamlit as st
from typing import Callable
from streamlit_extras.stylable_container import stylable_container

def create_collapsible_panel(panel_id: str, main_content: Callable):
    """
    Creates a simple collapsible panel with main content and side panel.
    """
    # State management
    is_expanded = st.session_state.get(f'panel_expanded_{panel_id}', False)
    
    # Layout
    if is_expanded:
        main, toggle, panel = st.columns([0.6, 0.02, 0.38])
    else:
        main, toggle = st.columns([0.98, 0.02])
    
    # Main content
    with main:
        main_content()
    
    # Toggle
    with toggle:
        if st.toggle("", value=is_expanded, key=f"toggle_{panel_id}", label_visibility="collapsed"):
            if not is_expanded:
                st.session_state[f'panel_expanded_{panel_id}'] = True
                st.rerun()
        else:
            if is_expanded:
                st.session_state[f'panel_expanded_{panel_id}'] = False
                st.rerun()
    
    # Panel content
    if is_expanded:
        with panel:
            # Override Streamlit's default right padding
            st.markdown("""
                <style>
                [data-testid="stSidebar"][aria-expanded="true"] ~ div:has(> .element-container) {
                    padding-right: 0 !important;
                }
                [data-testid="stSidebar"][aria-expanded="true"] ~ div:has(> .element-container) [data-testid="stVerticalBlock"] {
                    gap: 0 !important;
                }
                </style>
            """, unsafe_allow_html=True)
            
            # Use stylable_container for the panel
            with stylable_container(
                key=f"panel_{panel_id}",
                css_styles="""
                    {
                        background: rgba(38, 39, 48, 0.2);
                        border-left: 1px solid rgba(128, 128, 128, 0.2);
                        height: calc(100vh - 4rem);
                        position: fixed;
                        top: 4rem;
                        right: 0;
                        width: 38%;
                        overflow-y: auto;
                        padding: 1rem;
                    }
                    [data-testid="stSidebar"][aria-expanded="true"] ~ div:has(> .element-container) & {
                        width: calc(38% - 22rem);
                    }
                """
            ):
                st.markdown("### COMING SOON") 