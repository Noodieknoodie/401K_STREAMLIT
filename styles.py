def load_styles():
    """Return all application CSS styles as a single string"""
    return """
        <style>
        /* Base sidebar styling */
        .sidebar .sidebar-content {
            background-color: #f8f9fa;
        }
        
        /* Button styling */
        .stButton>button {
            width: 100%;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: flex-start;
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
        </style>
    """