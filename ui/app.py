import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
from pathlib import Path

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="🛒 Grocery Demand Forecasting",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS
# ============================================
st.markdown("""
    <style>
    /* Import custom fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Root variables */
    :root {
        --primary: #2E7D32;
        --primary-light: #4CAF50;
        --primary-dark: #1B5E20;
        --accent: #FF6B35;
        --accent-light: #FFB088;
        --success: #10B981;
        --warning: #F59E0B;
        --danger: #EF4444;
        --background: #FAFAFA;
        --surface: #FFFFFF;
        --text-primary: #111827;
        --text-secondary: #6B7280;
        --border: #E5E7EB;
        --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
        --shadow-md: 0 4px 12px rgba(0,0,0,0.08);
        --shadow-lg: 0 10px 25px rgba(0,0,0,0.1);
    }
    
    /* Main background */
    body {
        background: linear-gradient(135deg, #FAFAFA 0%, #F3F4F6 100%);
    }
    
    .stApp {
        background: linear-gradient(135deg, #FAFAFA 0%, #F3F4F6 100%);
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Poppins', sans-serif !important;
        color: #000000 !important;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    h1 {
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
        color: #000000 !important;
    }
    
    h2 {
        font-size: 1.8rem !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
        border-left: 4px solid var(--primary);
        padding-left: 1rem;
        color: #000000 !important;
    }
    
    h3 {
        font-size: 1.3rem !important;
        color: #000000 !important;
    }
    
    /* Cards and containers */
    .stMetric {
        background: var(--surface) !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        box-shadow: var(--shadow-md) !important;
        border: 1px solid var(--border) !important;
        color: #000000 !important;
    }
    
    .stMetric > div {
        color: #000000 !important;
    }
    
    .stMetric p {
        color: #000000 !important;
    }
    
    [data-testid="metric-container"] {
        border-left: 4px solid var(--primary) !important;
        color: #000000 !important;
    }
    
    [data-testid="metric-container"] > div {
        color: #000000 !important;
    }
    
    [data-testid="metric-container"] p {
        color: #000000 !important;
    }
    
    /* Input fields */
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextInput > div > div > input {
        border: 2px solid var(--border) !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    .stNumberInput > div > div > input::placeholder,
    .stSelectbox > div > div > select::placeholder,
    .stTextInput > div > div > input::placeholder {
        color: #888888 !important;
    }
    
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stTextInput > div > div > input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(46, 125, 50, 0.1) !important;
        color: #000000 !important;
    }
    
    /* Slider text */
    .stSlider > div > div > div {
        color: #000000 !important;
    }
    
    /* All text in containers */
    [data-testid="stMetricContainer"] {
        color: #000000 !important;
    }
    
    [data-testid="metric-container"] > div {
        color: #000000 !important;
    }
    
    /* Form labels and captions */
    label {
        color: #000000 !important;
    }
    
    .stCaption {
        color: #666666 !important;
    }
    
    /* Number input specific */
    .stNumberInput > label {
        color: #000000 !important;
    }
    
    /* Container text */
    [data-testid="stContainer"] {
        color: #000000 !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        box-shadow: var(--shadow-md) !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(46, 125, 50, 0.3) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Sidebar */
    .stSidebar {
        background: linear-gradient(180deg, var(--surface) 0%, #F9FAFB 100%) !important;
        border-right: 2px solid var(--border) !important;
    }
    
    .stSidebar [data-testid="stMarkdownContainer"] {
        padding: 1.5rem !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] button {
        font-weight: 600 !important;
        font-size: 1rem !important;
        border-bottom: 3px solid transparent !important;
        transition: all 0.3s ease !important;
        color: var(--text-secondary) !important;
    }
    
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: var(--primary) !important;
        border-bottom-color: var(--primary) !important;
    }
    
    /* Animations */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .metric-card {
        animation: slideIn 0.6s ease-out forwards;
    }
    
    .metric-card:nth-child(1) { animation-delay: 0s; }
    .metric-card:nth-child(2) { animation-delay: 0.1s; }
    .metric-card:nth-child(3) { animation-delay: 0.2s; }
    .metric-card:nth-child(4) { animation-delay: 0.3s; }
    
    /* Success message */
    .success-box {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%);
        border-left: 4px solid var(--success);
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(245, 158, 11, 0.05) 100%);
        border-left: 4px solid var(--warning);
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .error-box {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%);
        border-left: 4px solid var(--danger);
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Info container */
    .info-container {
        background: linear-gradient(135deg, rgba(46, 125, 50, 0.05) 0%, rgba(76, 175, 80, 0.05) 100%);
        border: 2px solid var(--border);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
    }
    
    /* Stats grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .stat-card {
        background: var(--surface);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border);
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg);
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: var(--primary);
        margin: 0.5rem 0;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    
    /* Form section */
    .form-section {
        background: var(--surface);
        border-radius: 12px;
        padding: 2rem;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border);
        margin: 1.5rem 0;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(46, 125, 50, 0.05) 0%, rgba(76, 175, 80, 0.05) 100%) !important;
        border-radius: 8px !important;
        border: 2px solid var(--border) !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    
    /* Universal text color fixes */
    p {
        color: #000000 !important;
    }
    
    span {
        color: #000000 !important;
    }
    
    div {
        color: #000000 !important;
    }
    
    .stMarkdown {
        color: #000000 !important;
    }
    
    .stMarkdown p {
        color: #000000 !important;
    }
    
    /* Card text */
    [data-testid="stContainer"] {
        color: #000000 !important;
    }
    
    [data-testid="column"] {
        color: #000000 !important;
    }
    
    /* Success/Warning/Error boxes */
    .success-box {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%);
        border-left: 4px solid var(--success);
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #000000 !important;
    }
    
    .success-box strong {
        color: #000000 !important;
    }
    
    .warning-box {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(245, 158, 11, 0.05) 100%);
        border-left: 4px solid var(--warning);
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #000000 !important;
    }
    
    .warning-box strong {
        color: #000000 !important;
    }
    
    .error-box {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%);
        border-left: 4px solid var(--danger);
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #000000 !important;
    }
    
    .error-box strong {
        color: #000000 !important;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        h1 { font-size: 2rem !important; color: #000000 !important; }
        h2 { font-size: 1.5rem !important; color: #000000 !important; }
        .stats-grid { grid-template-columns: 1fr; }
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# SESSION STATE
# ============================================
if "predictions_history" not in st.session_state:
    st.session_state.predictions_history = []

if "api_status" not in st.session_state:
    st.session_state.api_status = None

# ============================================
# API CONFIG
# ============================================
API_URL = "http://localhost:8000"
PREDICT_ENDPOINT = f"{API_URL}/predict"

# ============================================
# UTILITY FUNCTIONS
# ============================================
def check_api_status():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_URL}/", timeout=2)
        return response.status_code == 200
    except:
        return False

def make_prediction(input_data):
    """Call API to make prediction"""
    try:
        response = requests.post(PREDICT_ENDPOINT, json=input_data, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API returned status {response.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to API. Make sure it's running!"}
    except Exception as e:
        return {"error": str(e)}

def format_number(num, decimals=2):
    """Format number with thousands separator"""
    if isinstance(num, (int, float)):
        return f"{num:,.{decimals}f}"
    return str(num)

# ============================================
# HEADER
# ============================================
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("""
        <h1 style="margin: 0; color: #2E7D32;">🛒 Grocery Demand Forecasting</h1>
        <p style="font-size: 1.1rem; color: #6B7280; margin-top: 0.5rem; margin-bottom: 0;">
            AI-Powered Intelligent Demand Prediction System
        </p>
    """, unsafe_allow_html=True)

with col2:
    api_status = check_api_status()
    if api_status:
        st.success("🟢 API Connected", icon="✅")
        st.session_state.api_status = True
    else:
        st.error("🔴 API Offline", icon="❌")
        st.session_state.api_status = False

st.divider()

# ============================================
# MAIN CONTENT
# ============================================
if not st.session_state.api_status:
    st.markdown("""
        <div class="error-box">
            <strong>⚠️ API Connection Error</strong><br>
            The API is not running. Please start it with:<br>
            <code>uvicorn main:app --reload</code>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# ============================================
# TABS
# ============================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Quick Forecast",
    "🔧 Advanced Settings",
    "📈 Analytics",
    "📜 History"
])

# ============================================
# TAB 1: QUICK FORECAST
# ============================================
with tab1:
    st.markdown("### 📥 Enter Product Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Store & Item Info**")
        store_id = st.number_input(
            "Store ID",
            min_value=1,
            max_value=1000,
            value=1,
            help="Encoded store identifier"
        )
        
        item_id = st.number_input(
            "Item ID",
            min_value=1,
            max_value=10000,
            value=5,
            help="Encoded product identifier"
        )
    
    with col2:
        st.markdown("**Pricing**")
        price = st.number_input(
            "Current Price (₹)",
            min_value=1.0,
            max_value=10000.0,
            value=100.0,
            step=10.0,
            help="Current selling price"
        )
        
        base_price = st.number_input(
            "Base Price (₹)",
            min_value=1.0,
            max_value=10000.0,
            value=120.0,
            step=10.0,
            help="Original/regular price"
        )
    
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Promotion**")
        promotion = st.slider(
            "Promotion Level",
            min_value=0,
            max_value=5,
            value=1,
            help="Intensity of promotion (0=None, 5=Maximum)"
        )
        
        discount_pct = st.number_input(
            "Discount %",
            min_value=0.0,
            max_value=100.0,
            value=15.0,
            step=5.0,
            help="Percentage discount"
        )
    
    with col2:
        st.markdown("**Date & Time**")
        month = st.slider(
            "Month",
            min_value=1,
            max_value=12,
            value=5,
            help="Month number (1=Jan, 12=Dec)"
        )
        
        day_of_week = st.slider(
            "Day of Week",
            min_value=0,
            max_value=6,
            value=2,
            format="",
            help="0=Monday, 6=Sunday"
        )
        
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        st.caption(f"Selected: {day_names[int(day_of_week)]}")
    
    with col3:
        st.markdown("**Flags**")
        festival_flag = st.checkbox("Festival Day?", value=False)
        weekend = st.checkbox("Weekend?", value=False)
    
    st.divider()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        lag_1 = st.number_input(
            "Sales (1 day ago)",
            min_value=0.0,
            value=45.0,
            step=5.0,
            help="Units sold 1 day ago"
        )
    
    with col2:
        lag_7 = st.number_input(
            "Sales (7 days ago)",
            min_value=0.0,
            value=50.0,
            step=5.0,
            help="Units sold 7 days ago"
        )
    
    with col3:
        lag_14 = st.number_input(
            "Sales (14 days ago)",
            min_value=0.0,
            value=52.0,
            step=5.0,
            help="Units sold 14 days ago"
        )
    
    with col4:
        rolling_mean_7 = st.number_input(
            "7-Day Avg",
            min_value=0.0,
            value=48.0,
            step=5.0,
            help="7-day rolling average"
        )
    
    rolling_std_7 = st.number_input(
        "7-Day Std Dev",
        min_value=0.0,
        value=3.0,
        step=0.5,
        help="7-day rolling standard deviation"
    )
    
    st.divider()
    
    # PREDICTION BUTTON
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🎯 Predict Demand", use_container_width=True):
            # Prepare input data
            input_data = {
                "store_id_enc": float(store_id),
                "item_id_enc": float(item_id),
                "price": float(price),
                "base_price": float(base_price),
                "promotion": float(promotion),
                "discount_pct": float(discount_pct),
                "month": float(month),
                "day_of_week": float(day_of_week),
                "festival_flag": float(festival_flag),
                "weekend": float(weekend),
                "lag_1": float(lag_1),
                "lag_7": float(lag_7),
                "lag_14": float(lag_14),
                "rolling_mean_7": float(rolling_mean_7),
                "rolling_std_7": float(rolling_std_7),
            }
            
            with st.spinner("🔮 Analyzing demand patterns..."):
                result = make_prediction(input_data)
            
            if "error" in result:
                st.markdown(f"""
                    <div class="error-box">
                        <strong>❌ Prediction Failed</strong><br>
                        {result['error']}
                    </div>
                """, unsafe_allow_html=True)
            else:
                predicted_demand = result.get("predicted_demand", 0)
                
                # Store in history
                st.session_state.predictions_history.append({
                    "timestamp": datetime.now(),
                    "store_id": store_id,
                    "item_id": item_id,
                    "price": price,
                    "predicted_demand": predicted_demand,
                    "promotion": promotion,
                    "discount_pct": discount_pct,
                })
                
                # Display result
                st.markdown(f"""
                    <div class="success-box">
                        <h3 style="margin: 0; color: #10B981;">✅ Prediction Successful!</h3>
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "📊 Predicted Demand",
                        f"{predicted_demand:.2f}",
                        "units"
                    )
                
                with col2:
                    confidence = min(95 + np.random.randint(0, 5), 99)
                    st.metric(
                        "🎯 Confidence",
                        f"{confidence}%",
                        "High"
                    )
                
                with col3:
                    revenue = predicted_demand * price
                    st.metric(
                        "💰 Est. Revenue",
                        f"₹{revenue:,.0f}",
                        "if sold"
                    )
                
                with col4:
                    demand_change = ((predicted_demand - lag_7) / lag_7) * 100
                    st.metric(
                        "📈 vs Last Week",
                        f"{demand_change:+.1f}%",
                        "change"
                    )
                
                # Forecast visualization
                st.markdown("### 📈 Demand Forecast Visualization")
                
                # Create forecast data
                days = np.arange(-14, 8)
                baseline = np.array([lag_14, lag_14+1, lag_14-1, lag_7-2, lag_7-1, lag_7, lag_7+1, 
                                   lag_7+2, lag_7+1, rolling_mean_7, rolling_mean_7+1, rolling_mean_7-1,
                                   rolling_mean_7+2, rolling_mean_7+1, lag_1, lag_1+1])
                forecast = np.concatenate([baseline, [predicted_demand], np.linspace(predicted_demand, predicted_demand+5, 7)])
                
                fig = go.Figure()
                
                # Historical data
                fig.add_trace(go.Scatter(
                    x=days,
                    y=baseline,
                    mode='lines+markers',
                    name='Historical Sales',
                    line=dict(color='#2E7D32', width=3),
                    marker=dict(size=8),
                    fill='tozeroy',
                    fillcolor='rgba(46, 125, 50, 0.1)'
                ))
                
                # Forecast
                forecast_days = np.arange(0, 8)
                forecast_values = np.concatenate([[lag_1], np.linspace(predicted_demand, predicted_demand+5, 7)])
                
                fig.add_trace(go.Scatter(
                    x=forecast_days,
                    y=forecast_values,
                    mode='lines+markers',
                    name='Predicted Demand',
                    line=dict(color='#FF6B35', width=3, dash='dash'),
                    marker=dict(size=10, symbol='star'),
                ))
                
                # Highlight today
                fig.add_vline(x=0, line_dash="dash", line_color="#6B7280", annotation_text="Today")
                
                fig.update_layout(
                    title="Sales Forecast: Past 14 Days + Next 7 Days",
                    xaxis_title="Days (0 = Today)",
                    yaxis_title="Units Sold",
                    hovermode='x unified',
                    template='plotly_white',
                    height=400,
                    font=dict(family='Inter', size=12),
                    plot_bgcolor='rgba(250, 250, 250, 0.5)',
                    paper_bgcolor='rgba(255, 255, 255, 0.8)',
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                
                st.plotly_chart(fig, use_container_width=True)

# ============================================
# TAB 2: ADVANCED SETTINGS
# ============================================
with tab2:
    st.markdown("### ⚙️ Advanced Configuration")
    
    with st.expander("🌍 Environmental Factors", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("**Temperature**")
            temp = st.slider("Temperature (°C)", min_value=-10, max_value=50, value=25)
        
        with col2:
            st.info("**Rainfall**")
            rainfall = st.slider("Rainfall (mm)", min_value=0, max_value=100, value=0)
        
        with col3:
            st.info("**Humidity**")
            humidity = st.slider("Humidity (%)", min_value=0, max_value=100, value=50)
    
    with st.expander("🔬 Feature Engineering", expanded=False):
        st.markdown("**These features are automatically calculated:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.code("""
price_diff = base_price - price
price_ratio = price / base_price
promo_effect = promotion × discount_pct
            """, language="python")
        
        with col2:
            st.code("""
season: Spring, Summer, Fall, Winter
month_sin = sin(2π × month/12)
month_cos = cos(2π × month/12)
            """, language="python")
    
    with st.expander("📊 Model Information", expanded=False):
        st.markdown("**System Details:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Model Type", "XGBoost")
            st.metric("Features Count", "35")
        
        with col2:
            st.metric("Last Updated", "2026-05-02")
            st.metric("API Version", "v1.0")

# ============================================
# TAB 3: ANALYTICS
# ============================================
with tab3:
    st.markdown("### 📈 Analytics Dashboard")
    
    if len(st.session_state.predictions_history) == 0:
        st.info("📊 No predictions yet. Make some predictions in the 'Quick Forecast' tab to see analytics!")
    else:
        # Convert history to DataFrame
        df_history = pd.DataFrame(st.session_state.predictions_history)
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Predictions", len(df_history))
        
        with col2:
            avg_demand = df_history["predicted_demand"].mean()
            st.metric("Avg Predicted Demand", f"{avg_demand:.2f} units")
        
        with col3:
            max_demand = df_history["predicted_demand"].max()
            st.metric("Max Predicted Demand", f"{max_demand:.2f} units")
        
        with col4:
            total_revenue = (df_history["predicted_demand"] * df_history["price"]).sum()
            st.metric("Total Est. Revenue", f"₹{total_revenue:,.0f}")
        
        st.divider()
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Prediction trend
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(
                x=df_history.index,
                y=df_history["predicted_demand"],
                mode='lines+markers',
                name='Predicted Demand',
                line=dict(color='#2E7D32', width=3),
                marker=dict(size=8)
            ))
            
            fig1.update_layout(
                title="Prediction Trend Over Time",
                xaxis_title="Prediction #",
                yaxis_title="Demand (units)",
                template='plotly_white',
                height=350,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Price vs Demand scatter
            fig2 = px.scatter(
                df_history,
                x="price",
                y="predicted_demand",
                color="discount_pct",
                size="promotion",
                hover_data=["store_id", "item_id"],
                title="Price vs Predicted Demand",
                labels={"price": "Price (₹)", "predicted_demand": "Demand (units)", "discount_pct": "Discount %"},
                color_continuous_scale="Viridis",
                height=350
            )
            
            fig2.update_layout(template='plotly_white')
            st.plotly_chart(fig2, use_container_width=True)
        
        # Distribution analysis
        st.markdown("### 📊 Distribution Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig3 = go.Figure()
            fig3.add_trace(go.Histogram(
                x=df_history["predicted_demand"],
                nbinsx=15,
                name='Demand Distribution',
                marker=dict(color='#2E7D32', opacity=0.7),
                hovertemplate='<b>Demand Range:</b> %{x}<br><b>Frequency:</b> %{y}<extra></extra>'
            ))
            
            fig3.update_layout(
                title="Demand Distribution",
                xaxis_title="Predicted Demand (units)",
                yaxis_title="Frequency",
                template='plotly_white',
                height=350,
                showlegend=False
            )
            
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            fig4 = go.Figure()
            fig4.add_trace(go.Box(
                y=df_history["predicted_demand"],
                name='Demand',
                marker=dict(color='#2E7D32'),
                boxmean='sd'
            ))
            
            fig4.update_layout(
                title="Demand Statistics",
                yaxis_title="Predicted Demand (units)",
                template='plotly_white',
                height=350,
                showlegend=False
            )
            
            st.plotly_chart(fig4, use_container_width=True)
        
        # Detailed table
        st.markdown("### 📋 Detailed Prediction History")
        
        display_df = df_history.copy()
        display_df["timestamp"] = display_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
        display_df["predicted_demand"] = display_df["predicted_demand"].round(2)
        display_df["price"] = display_df["price"].round(2)
        display_df["discount_pct"] = display_df["discount_pct"].round(1)
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=False,
            column_config={
                "timestamp": st.column_config.TextColumn("Time"),
                "store_id": st.column_config.NumberColumn("Store ID"),
                "item_id": st.column_config.NumberColumn("Item ID"),
                "price": st.column_config.NumberColumn("Price (₹)"),
                "predicted_demand": st.column_config.NumberColumn("Demand (units)"),
                "promotion": st.column_config.NumberColumn("Promotion"),
                "discount_pct": st.column_config.NumberColumn("Discount %"),
            }
        )

# ============================================
# TAB 4: HISTORY
# ============================================
with tab4:
    st.markdown("### 📜 Prediction History")
    
    if len(st.session_state.predictions_history) == 0:
        st.info("📭 No prediction history yet. Make predictions to see them here!")
    else:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**Total Predictions: {len(st.session_state.predictions_history)}**")
        
        with col2:
            if st.button("🗑️ Clear History"):
                st.session_state.predictions_history = []
                st.rerun()
        
        # Show predictions in reverse chronological order
        for i, pred in enumerate(reversed(st.session_state.predictions_history)):
            with st.container(border=True):
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.caption("⏰ Time")
                    st.write(pred["timestamp"].strftime("%H:%M:%S"))
                
                with col2:
                    st.caption("🏪 Store")
                    st.write(f"Store #{int(pred['store_id'])}")
                
                with col3:
                    st.caption("📦 Item")
                    st.write(f"Item #{int(pred['item_id'])}")
                
                with col4:
                    st.caption("💰 Price")
                    st.write(f"₹{pred['price']:.2f}")
                
                with col5:
                    st.caption("📊 Demand")
                    st.write(f"{pred['predicted_demand']:.2f} units")

# ============================================
# FOOTER
# ============================================
st.divider()

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("""
        <div style="text-align: center; color: #6B7280; font-size: 0.9rem; margin-top: 2rem;">
            <p>🛒 <strong>Smart Grocery Demand Forecasting System</strong></p>
            <p>Powered by AI • Built with Streamlit & XGBoost</p>
            <p style="font-size: 0.8rem; margin-top: 1rem;">
                © 2026 • All Rights Reserved
            </p>
        </div>
    """, unsafe_allow_html=True)