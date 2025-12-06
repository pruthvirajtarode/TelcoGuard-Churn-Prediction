
import streamlit as st
import pandas as pd
import joblib
from datetime import datetime

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="TelcoGuard - Churn Prediction",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "TelcoGuard - Advanced Customer Churn Prediction System"}
)

# ==================== CUSTOM CSS ====================
custom_css = """
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    /* Main background - Professional dark gradient */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        min-height: 100vh;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Header styling - Professional and minimal */
    .header-container {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: white;
        padding: 50px 40px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 40px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    .header-container h1 {
        font-size: 3.5em;
        font-weight: 700;
        margin-bottom: 12px;
        letter-spacing: 2px;
        color: #3b82f6;
    }
    
    .header-container p {
        font-size: 1.1em;
        opacity: 0.85;
        font-weight: 400;
        letter-spacing: 0.5px;
        color: #cbd5e1;
    }
    
    /* Card styling - Clean and professional */
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 10px;
        padding: 24px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(59, 130, 246, 0.15);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.2);
        border-color: rgba(59, 130, 246, 0.3);
    }
    
    /* Input section styling */
    .input-section {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 12px;
        padding: 35px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        margin-bottom: 30px;
        border: 1px solid rgba(59, 130, 246, 0.15);
    }
    
    /* Button styling - Sleek and professional */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        font-size: 1em !important;
        padding: 14px 40px !important;
        border: none !important;
        border-radius: 8px !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Success alert */
    .success-box {
        background: linear-gradient(135deg, #064e3b 0%, #047857 100%);
        color: white;
        padding: 28px;
        border-radius: 10px;
        text-align: center;
        font-size: 1.2em;
        font-weight: 600;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.2);
        border: 1px solid rgba(16, 185, 129, 0.3);
        animation: slideIn 0.4s ease;
    }
    
    /* Error alert */
    .error-box {
        background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%);
        color: white;
        padding: 28px;
        border-radius: 10px;
        text-align: center;
        font-size: 1.2em;
        font-weight: 600;
        box-shadow: 0 4px 20px rgba(239, 68, 68, 0.2);
        border: 1px solid rgba(239, 68, 68, 0.3);
        animation: slideIn 0.4s ease;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Result box styling */
    .result-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 12px;
        padding: 35px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        margin-top: 30px;
        border-left: 4px solid #3b82f6;
        border: 1px solid rgba(59, 130, 246, 0.15);
    }
    
    /* Stat display */
    .stat-display {
        font-size: 2.8em;
        font-weight: 700;
        color: #3b82f6;
        margin: 15px 0;
    }
    
    /* Section title */
    .section-title {
        color: #ffffff;
        font-size: 1.7em;
        font-weight: 700;
        margin-top: 30px;
        margin-bottom: 15px;
        letter-spacing: 0.5px;
    }
    
    /* Divider */
    .divider {
        height: 2px;
        background: linear-gradient(90deg, #3b82f6 0%, transparent 100%);
        margin: 20px 0;
        border-radius: 1px;
    }
    
    /* Info text */
    .info-text {
        color: #cbd5e1;
        font-size: 0.95em;
        line-height: 1.6;
        margin-top: 10px;
    }
    
    /* Slider styling */
    .stSlider {
        padding: 20px 0;
    }
    
    /* Recommendation list */
    ul {
        color: #cbd5e1;
        padding-left: 25px;
    }
    
    ul li {
        margin-bottom: 10px;
        line-height: 1.6;
        transition: all 0.2s ease;
    }
    
    ul li:hover {
        color: #3b82f6;
        padding-left: 10px;
    }
    
    /* Premium text */
    strong {
        color: #3b82f6;
        font-weight: 600;
    }
    
    /* Banner styling */
    .banner {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 10px;
        padding: 16px;
        color: #cbd5e1;
        text-align: center;
        font-weight: 500;
    }

    /* Profile card in sidebar */
    .profile-card {
        background: linear-gradient(135deg, rgba(59,130,246,0.06) 0%, rgba(15,23,42,0.04) 100%);
        border-radius: 12px;
        padding: 18px;
        margin: 12px 8px 20px 8px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.03);
    }

    .avatar {
        width: 72px;
        height: 72px;
        border-radius: 50%;
        display: inline-block;
        line-height: 72px;
        font-size: 26px;
        color: #0f172a;
        background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
        font-weight: 700;
        margin-bottom: 8px;
        box-shadow: 0 6px 18px rgba(59,130,246,0.18);
    }

    .profile-name { color: #ffffff; font-weight: 700; font-size: 1.05em; margin-top: 6px }
    .profile-role { color: #9fb6ff; font-size: 0.85em; margin-bottom: 8px }
    .profile-email { color: #cbd5e1; font-size: 0.78em; margin-bottom: 8px }
    .profile-actions button { background: transparent; border: 1px solid rgba(255,255,255,0.06); color: #cbd5e1; padding: 8px 12px; border-radius: 8px; margin: 4px }

    /* Avatar image when uploaded */
    .avatar-img { width: 72px; height: 72px; border-radius: 50%; object-fit: cover; display: block; margin: 0 auto 8px; box-shadow: 0 6px 18px rgba(59,130,246,0.18); }

    /* Style sidebar buttons within profile card */
    [data-testid="stSidebar"] .profile-card .stButton>button {
        background: transparent !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        color: #cbd5e1 !important;
        padding: 8px 12px !important;
        border-radius: 8px !important;
        margin: 4px !important;
        font-weight: 600 !important;
    }

    [data-testid="stSidebar"] .profile-card .stButton>button:hover {
        background: rgba(59,130,246,0.08) !important;
        border-color: rgba(59,130,246,0.18) !important;
    }
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# ==================== HEADER SECTION ====================
st.markdown("""
<div class="header-container">
    <h1>TelcoGuard</h1>
    <p>Customer Churn Prediction Platform</p>
    <p style="font-size: 0.95em; margin-top: 15px; opacity: 0.8;">Enterprise-Grade Analytics</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="banner">
    <p style="color: #3b82f6; font-weight: 600; font-size: 1em;">📊 Real-Time Churn Risk Assessment</p>
</div>
""", unsafe_allow_html=True)

# ==================== USER PROFILE (SIDEBAR) ====================
if 'user' not in st.session_state:
    st.session_state.user = {
        'name': 'Alex Johnson',
        'role': 'Product Manager',
        'email': 'alex.johnson@telcoguard.com'
    }

if 'show_profile_edit' not in st.session_state:
    st.session_state.show_profile_edit = False

with st.sidebar:
    st.markdown('<div class="profile-card">', unsafe_allow_html=True)
    # Avatar (initials or uploaded image)
    name = st.session_state.user.get('name', 'User')
    initials = ''.join([p[0] for p in name.split()][:2]).upper()
    avatar_path = st.session_state.user.get('avatar_path')
    if avatar_path:
        try:
            # embed as base64
            import base64
            with open(avatar_path, 'rb') as f:
                data = f.read()
            b64 = base64.b64encode(data).decode('utf-8')
            img_tag = f'<img src="data:image/png;base64,{b64}" class="avatar-img"/>'
            st.markdown(img_tag, unsafe_allow_html=True)
        except Exception:
            st.markdown(f'<div class="avatar">{initials}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="avatar">{initials}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="profile-name">{st.session_state.user.get("name")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="profile-role">{st.session_state.user.get("role")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="profile-email">{st.session_state.user.get("email")}</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns([1,1])
    with col_a:
        if st.button('Edit Profile', key='edit_profile'):
            st.session_state.show_profile_edit = not st.session_state.show_profile_edit
    with col_b:
        if st.button('Logout', key='logout'):
            # Simulated logout for the demo
            st.session_state.user = {'name': 'Guest', 'role': 'Visitor', 'email': ''}
            st.success('Logged out')

    if st.session_state.show_profile_edit:
        with st.form('profile_form'):
            new_name = st.text_input('Full name', value=st.session_state.user.get('name'))
            new_role = st.text_input('Role', value=st.session_state.user.get('role'))
            new_email = st.text_input('Email', value=st.session_state.user.get('email'))
            upload = st.file_uploader('Upload avatar (PNG/JPG)', type=['png', 'jpg', 'jpeg'])
            save = st.form_submit_button('Save')
            if save:
                st.session_state.user['name'] = new_name
                st.session_state.user['role'] = new_role
                st.session_state.user['email'] = new_email
                # Save avatar file if uploaded
                if upload is not None:
                    import os
                    avatars_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'avatars')
                    os.makedirs(avatars_dir, exist_ok=True)
                    # create a safe filename from email or initials
                    safe_name = (new_email or initials).replace('@', '_at_').replace('.', '_')
                    ext = os.path.splitext(upload.name)[1]
                    out_path = os.path.abspath(os.path.join(avatars_dir, f"{safe_name}{ext}"))
                    with open(out_path, 'wb') as out_f:
                        out_f.write(upload.getbuffer())
                    st.session_state.user['avatar_path'] = out_path
                st.success('Profile updated')

    st.markdown('</div>', unsafe_allow_html=True)

# ==================== MAIN CONTENT ====================
st.markdown("---")

# Load the model
try:
    model = joblib.load("model/churn_model.pkl")
except FileNotFoundError:
    st.error("❌ Model file not found! Please train the model first.")
    st.stop()

# ==================== LAYOUT ====================
col1, col2 = st.columns([1, 1.2], gap="large")

with col1:
    st.markdown('<div class="section-title">📋 Customer Information</div>', unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    
    # Tenure slider with info
    st.markdown("**📅 Tenure (Months)**")
    tenure = st.slider(
        label_visibility="collapsed",
        label="Tenure",
        min_value=1,
        max_value=72,
        value=24,
        step=1,
        help="Customer's relationship duration with the company"
    )
    st.markdown(f'<p class="info-text">Selected: <strong>{tenure} months</strong> ({tenure//12} years, {tenure%12} months)</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Monthly charges slider with info
    st.markdown("**💰 Monthly Charges (₹)**")
    monthly = st.slider(
        label_visibility="collapsed",
        label="Monthly Charges",
        min_value=500,
        max_value=5000,
        value=1500,
        step=50,
        help="Average monthly billing amount"
    )
    st.markdown(f'<p class="info-text">Selected: <strong>₹{monthly:,}</strong></p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Total charges slider with info
    st.markdown("**💳 Total Charges (₹)**")
    total = st.slider(
        label_visibility="collapsed",
        label="Total Charges",
        min_value=1000,
        max_value=150000,
        value=35000,
        step=1000,
        help="Cumulative charges over the customer's tenure"
    )
    st.markdown(f'<p class="info-text">Selected: <strong>₹{total:,}</strong></p>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="section-title">📊 Analysis & Prediction</div>', unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Display metrics
    metric_col1, metric_col2, metric_col3 = st.columns(3, gap="small")
    
    with metric_col1:
        st.markdown(f"""
        <div class="metric-card">
            <p style="color: #6b7280; font-size: 0.85em; margin-bottom: 5px;">TENURE</p>
            <div class="stat-display">{tenure}</div>
            <p style="color: #6b7280; font-size: 0.8em;">months</p>
        </div>
        """, unsafe_allow_html=True)
    
    with metric_col2:
        st.markdown(f"""
        <div class="metric-card">
            <p style="color: #6b7280; font-size: 0.85em; margin-bottom: 5px;">MONTHLY</p>
            <div class="stat-display">₹{monthly}</div>
            <p style="color: #6b7280; font-size: 0.8em;">charges</p>
        </div>
        """, unsafe_allow_html=True)
    
    with metric_col3:
        st.markdown(f"""
        <div class="metric-card">
            <p style="color: #6b7280; font-size: 0.85em; margin-bottom: 5px;">TOTAL</p>
            <div class="stat-display">₹{total}</div>
            <p style="color: #6b7280; font-size: 0.8em;">charges</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Prediction button
    col_button1, col_button2 = st.columns(2, gap="small")
    
    with col_button1:
        predict_button = st.button("🔮 PREDICT", use_container_width=True, key="predict")
    
    with col_button2:
        reset_button = st.button("🔄 RESET", use_container_width=True, key="reset")
    
    if reset_button:
        st.rerun()
    
    # Display prediction results
    if predict_button:
        data = pd.DataFrame(
            [[tenure, monthly, total]],
            columns=["tenure", "monthly_charges", "total_charges"]
        )
        pred = model.predict(data)[0]
        
        # Get prediction probability if available
        try:
            pred_proba = model.predict_proba(data)[0]
            confidence = max(pred_proba) * 100
        except:
            confidence = None
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if pred == 1:
            st.markdown("""
            <div class="error-box">
                ⚠️ CHURN RISK DETECTED
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div class="result-box">
                <p style="color: #ef4444; font-weight: 600; font-size: 1.2em;">This customer is at HIGH RISK of churning.</p>
                <p class="info-text" style="margin-top: 15px;">
                    <strong>Recommendation:</strong> Implement retention strategies immediately:
                </p>
                <ul style="color: #6b7280; margin-top: 10px; padding-left: 20px;">
                    <li>Offer personalized discounts or loyalty rewards</li>
                    <li>Reach out with special retention packages</li>
                    <li>Review service quality and customer satisfaction</li>
                    <li>Consider win-back campaigns</li>
                </ul>
            """ + (f"<p class='info-text' style='margin-top: 15px;'><strong>Confidence:</strong> {confidence:.1f}%</p>" if confidence else "") + """
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="success-box">
                ✅ CUSTOMER RETENTION LIKELY
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div class="result-box">
                <p style="color: #10b981; font-weight: 600; font-size: 1.2em;">This customer is likely to STAY with the company.</p>
                <p class="info-text" style="margin-top: 15px;">
                    <strong>Recommendation:</strong> Focus on maintaining satisfaction:
                </p>
                <ul style="color: #6b7280; margin-top: 10px; padding-left: 20px;">
                    <li>Continue providing excellent customer service</li>
                    <li>Monitor satisfaction metrics regularly</li>
                    <li>Offer upsell opportunities for premium services</li>
                    <li>Maintain positive relationship engagement</li>
                </ul>
            """ + (f"<p class='info-text' style='margin-top: 15px;'><strong>Confidence:</strong> {confidence:.1f}%</p>" if confidence else "") + """
            </div>
            """, unsafe_allow_html=True)

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #cbd5e1; font-size: 0.9em; padding: 30px 20px; background: linear-gradient(135deg, rgba(59,130,246,0.05) 0%, transparent 100%); border-radius: 10px; margin-top: 30px; border: 1px solid rgba(59, 130, 246, 0.1);">
    <p style="font-weight: 600; font-size: 1.05em; margin-bottom: 10px; color: #ffffff;">TelcoGuard Platform</p>
    <p style="font-size: 0.9em; margin: 5px 0;">Advanced Churn Prediction • Enterprise Analytics</p>
    <p style="font-size: 0.85em; margin-top: 15px; opacity: 0.7;">Updated: """ + datetime.now().strftime("%B %d, %Y • %H:%M:%S") + """</p>
</div>
""", unsafe_allow_html=True)
