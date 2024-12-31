import streamlit as st

def render_document_viewer():
    # IMPORTANT: This approach works because:
    # 1. We use a single st.markdown call to inject both the CSS and HTML
    # 2. The position: fixed CSS completely removes the panel from the document flow
    # 3. We avoid using components.html() which creates a new iframe and breaks the layout
    # 4. All content is directly embedded in the fixed panel's HTML
    # Previous attempts failed because they tried to move Streamlit components into the panel
    # which isn't possible - the panel must be self-contained HTML
    st.markdown("""
    <style>
    .document-viewer {
        position: fixed;
        top: 0;
        right: 0;
        width: 40%;
        height: 100vh;
        background-color: #f0f2f6;
        box-shadow: -2px 0 5px rgba(0,0,0,0.1);
        padding: 1.5rem;
        overflow-y: auto;
        z-index: 999999;
        box-sizing: border-box;
    }
    </style>
    
    <div class="document-viewer">
        <h2 style="color: #ff4b4b;">📄 Test Content</h2>
        <div style="
            background-color: #e6f3ff;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            border: 2px solid #4a90e2;
        ">
            <h4 style="margin-top: 0;">This is test content in the document viewer</h4>
            <p>If you can see this blue box with text, the viewer is working! 🎉</p>
            <ul style="margin: 1rem 0;">
                <li>Test Item 1</li>
                <li>Test Item 2</li>
                <li>Test Item 3</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
