def load_styles():
    """Return all application CSS styles as a single string"""
    return """
        <style>
        /* Base sidebar styling */
        .sidebar .sidebar-content {
            background-color: #f8f9fa;
        }
        

        
        /* Expander styling */
        [data-testid="stExpander"] {
            width: 100% !important;
        }
        
        /* Contact card styling */
        .contact-info {
            border-bottom: 1px solid #eee;
            padding: 8px 0;
            margin-bottom: 8px;
        }
        .contact-info:last-child {
            border-bottom: none;
        }
        .contact-name {
            font-weight: bold;
            color: #1f77b4;
        }
        .contact-detail {
            margin: 2px 0;
            color: #555;
        }
        
        /* Metric container styling */
        div.block-container {
            padding-top: 1rem;
        }
        div.metric-container {
            font-size: 0.9rem !important;
        }
        [data-testid="metric-container"] {
            width: fit-content;
            margin: auto;
        }
        [data-testid="metric-container"] > div {
            width: fit-content;
            margin: auto;
        }
        [data-testid="metric-container"] label {
            font-size: 0.8rem !important;
            color: #555;
        }
        [data-testid="metric-container"] div[data-testid="metric-value"] {
            font-size: 1rem !important;
        }
        [data-testid="metric-container"] div[data-testid="metric-delta"] {
            font-size: 0.8rem !important;
        }
        
        /* Payment history table styling */
        .stDataFrame {
            font-size: 0.9rem;
        }
        .stDataFrame td {
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 200px;
        }
        .stDataFrame th {
            white-space: nowrap;
        }
        [data-testid="stDataFrameResizable"] {
            max-height: 600px;
            overflow: auto;
        }
        .payment-header {
            color: #555;
            font-size: 0.9rem;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        /* Note styling */
        .note-cell {
            display: flex;
            justify-content: center;
            align-items: center;
            width: 40px;
            margin: 0 auto;
        }
        
        .note-icon {
            cursor: pointer;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            font-size: 14px;
            transition: all 0.2s ease;
        }
        
        .note-icon.empty {
            border: 2px dashed #ccc;
            color: #ccc;
        }
        
        .note-icon.filled {
            background-color: #1f77b4;
            color: white;
            border: none;
        }
        
        .note-icon:hover {
            transform: scale(1.1);
        }
        
        /* Note popup styling */
        .note-popup {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            z-index: 1000;
            width: 300px;
        }
        
        .note-popup textarea {
            width: 100%;
            min-height: 100px;
            margin: 10px 0;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            resize: vertical;
        }
        
        .note-popup-buttons {
            display: flex;
            justify-content: flex-end;
            gap: 10px;
        }
        
        /* Make note column more compact */
        [data-testid="column"]:nth-child(9) {
            max-width: 60px !important;
            padding: 0 !important;
        }
        </style>
    """