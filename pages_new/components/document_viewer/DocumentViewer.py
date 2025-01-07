import streamlit as st

def render_document_viewer():
    st.markdown("""
    <style>
    .document-viewer {
        position: fixed;
        top: 0;
        right: 0;
        width: 40%;
        height: 100vh;
        background-color: #262731;
        box-shadow: -2px 0 5px rgba(0,0,0,0.4);
        padding: 1.5rem;
        overflow-y: auto;
        z-index: 999999;
        box-sizing: border-box;
        color: #f4f4f4;
    }
    </style>
    
    <div class="document-viewer">
        <h2 style="color: #f97316;">📄 Test Content</h2>
        <div style="
            background-color: #313340;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            border: 1px solid #64697b;
        ">
            <h4 style="margin-top: 0; color: #f4f4f4;">This is test content in the document viewer</h4>
            <p>If you can see this dark box with text, the viewer is working! 🎉</p>
            <ul style="margin: 1rem 0; color: #f4f4f4;">
                <li>Test Item 1</li>
                <li>Test Item 2</li>
                <li>Test Item 3</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)