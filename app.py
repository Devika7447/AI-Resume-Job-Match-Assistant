import os
import json
import io
from datetime import datetime
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import textwrap

# Load utilities
import utils.db_helper as db_helper
import utils.parser as parser
import utils.analyzer as analyzer
import utils.compiler as compiler

# Load Environment Variables
load_dotenv()
DEFAULT_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# -----------------------------
# Streamlit Page Config
# -----------------------------
st.set_page_config(
    page_title="CareerPilot AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Initialize Session State
# -----------------------------
def init_session_state():
    if "api_key" not in st.session_state:
        st.session_state.api_key = DEFAULT_API_KEY
    if "resume_text" not in st.session_state:
        st.session_state.resume_text = ""
    if "resume_name" not in st.session_state:
        st.session_state.resume_name = ""
    if "parsed_resume" not in st.session_state:
        st.session_state.parsed_resume = None
    if "job_description" not in st.session_state:
        st.session_state.job_description = ""
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None
    if "rewritten_resume" not in st.session_state:
        st.session_state.rewritten_resume = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "mock_interview" not in st.session_state:
        st.session_state.mock_interview = {
            "active": False,
            "questions": [],
            "current_index": 0,
            "answers": [],
            "feedback": []
        }
    if "active_page" not in st.session_state:
        st.session_state.active_page = "Dashboard"
    if "selected_template" not in st.session_state:
        st.session_state.selected_template = "VIT Academic Risk"

init_session_state()

# Configure API key dynamically if overridden in UI
if st.session_state.api_key:
    import google.generativeai as genai
    genai.configure(api_key=st.session_state.api_key)
    analyzer.API_KEY = st.session_state.api_key
    parser.API_KEY = st.session_state.api_key

# -----------------------------
# Premium UI Theme (CSS Injection)
# -----------------------------
st.markdown(
    """
    <style>
    /* Tahoma font family is system-safe, no import needed */
    
    /* Core Background and Typography (with premium Dot Field Grid and Ambient Glow) */
    .stApp {
        background-color: #05080A !important;
        background-image: 
            radial-gradient(rgba(255, 255, 255, 0.07) 1px, transparent 1px),
            radial-gradient(1200px 600px at 0% 0%, rgba(0, 212, 200, 0.15), transparent 60%), 
            radial-gradient(800px 400px at 100% 0%, rgba(20, 227, 211, 0.06), transparent 50%),
            radial-gradient(600px 600px at 50% 100%, rgba(0, 184, 184, 0.05), transparent 50%) !important;
        background-size: 28px 28px, 100% 100%, 100% 100%, 100% 100% !important;
        background-attachment: fixed !important;
        color: #ffffff !important;
        font-family: Tahoma, Geneva, Verdana, sans-serif !important;
    }
    
    /* Hide default Streamlit elements but keep header for sidebar toggle */
    header {
        background-color: transparent !important;
        background: transparent !important;
    }
    footer {visibility: hidden !important;}
    
    /* Hide specific header action items */
    button[data-testid="stHeaderDeployButton"],
    div[data-testid="stMainMenu"] {
        display: none !important;
    }
    
    /* Style the expand button (visible when sidebar is closed) */
    button[data-testid="collapsedSidebarCodegen"],
    button[aria-label="Expand sidebar"] {
        background-color: rgba(11, 15, 17, 0.8) !important;
        border: 1px solid rgba(0, 212, 200, 0.4) !important;
        color: #00D4C8 !important;
        border-radius: 4px !important;
        padding: 6px 10px !important;
        position: fixed !important;
        left: 15px !important;
        top: 15px !important;
        z-index: 999999 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.2s ease !important;
    }
    button[data-testid="collapsedSidebarCodegen"]:hover,
    button[aria-label="Expand sidebar"]:hover {
        background-color: rgba(0, 212, 200, 0.1) !important;
        border-color: #00D4C8 !important;
        transform: scale(1.05) !important;
    }
    
    /* Style the collapse button inside the sidebar */
    button[data-testid="stSidebarCollapse"],
    button[aria-label="Close sidebar"] {
        background-color: transparent !important;
        border: 1.5px solid transparent !important;
        color: #A8A8A8 !important;
        border-radius: 4px !important;
        transition: all 0.2s ease !important;
    }
    button[data-testid="stSidebarCollapse"]:hover,
    button[aria-label="Close sidebar"]:hover {
        color: #00D4C8 !important;
        border: 1.5px solid rgba(0, 212, 200, 0.3) !important;
        background-color: rgba(255, 255, 255, 0.02) !important;
    }
    
    /* Sidebar Overrides with Glassmorphism matching the JeniKhant Design */
    section[data-testid="stSidebar"] {
        background-color: rgba(10, 15, 17, 0.45) !important;
        backdrop-filter: blur(25px) !important;
        -webkit-backdrop-filter: blur(25px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    
    div[data-testid="stSidebarUserContent"], div[data-testid="stSidebar"] {
        background-color: transparent !important;
        background: transparent !important;
    }
    
    /* Remove padding from sidebar content container to allow edge-to-edge layout */
    div[data-testid="stSidebarUserContent"] {
        padding-left: 0px !important;
        padding-right: 0px !important;
        padding-top: 0px !important;
    }
    
    /* Minimize margins between elements in sidebar */
    div[data-testid="stSidebar"] div.element-container {
        margin-top: 0px !important;
        margin-bottom: 0px !important;
        padding-top: 0px !important;
        padding-bottom: 0px !important;
    }
    
    /* Profile Header Styling (from uploaded picture) */
    .profile-header {
        display: flex;
        align-items: center;
        padding: 24px 20px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 10px;
    }
    .avatar-container {
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .avatar-circle {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: linear-gradient(135deg, #00D4C8 0%, #00B8B8 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.9rem;
        color: #05080A;
        box-shadow: 0 0 12px rgba(0, 212, 200, 0.25);
    }
    .profile-info {
        margin-left: 12px;
        flex-grow: 1;
    }
    .profile-name {
        font-size: 0.9rem;
        font-weight: 600;
        color: #ffffff;
        line-height: 1.2;
    }
    .profile-subtitle {
        font-size: 0.72rem;
        color: #A8A8A8;
        margin-top: 2px;
    }
    .profile-arrow {
        font-size: 0.65rem;
        color: #888888;
        margin-left: 8px;
    }
    
    .sidebar-category {
        font-size: 0.7rem;
        font-weight: 600;
        color: #6E7985;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 15px;
        margin-bottom: 6px;
        padding-left: 20px;
    }
    
    /* Divider between menu categories */
    .sidebar-divider {
        height: 1px;
        background-color: rgba(255, 255, 255, 0.08);
        margin: 12px 0;
        width: 100%;
    }
    
    /* Navigation Buttons styled like a list in ruled book, with material icons */
    div[data-testid="stSidebar"] button {
        background-color: transparent !important;
        color: #A8A8A8 !important;
        border: 1.5px solid transparent !important;
        border-radius: 0px !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 10px 20px !important; /* Edge padding aligning with categories */
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease-in-out !important;
        width: 100% !important;
        box-shadow: none !important;
        transform: none !important;
        margin-bottom: 0px !important;
    }
    
    /* Adjust spacing between icon and text in Streamlit button */
    div[data-testid="stSidebar"] button [data-testid="stIcon"] {
        color: #A8A8A8 !important;
        margin-right: 10px !important;
        transition: color 0.2s ease-in-out !important;
    }
    
    /* Hover state: Displays a rounded teal border outline and teal text/icon */
    div[data-testid="stSidebar"] button:hover {
        color: #00D4C8 !important;
        border: 1.5px solid #00D4C8 !important;
        border-radius: 6px !important;
        background-color: rgba(0, 212, 200, 0.02) !important;
    }
    div[data-testid="stSidebar"] button:hover [data-testid="stIcon"] {
        color: #00D4C8 !important;
    }
    
    /* Active menu item has solid teal outline and text */
    div[data-testid="stSidebar"] button[kind="primary"],
    div[data-testid="stSidebar"] button[data-testid="baseButton-primary"] {
        background-color: transparent !important;
        color: #00D4C8 !important;
        font-weight: 600 !important;
        border: 1.5px solid #00D4C8 !important;
        border-radius: 6px !important;
    }
    div[data-testid="stSidebar"] button[kind="primary"] [data-testid="stIcon"],
    div[data-testid="stSidebar"] button[data-testid="baseButton-primary"] [data-testid="stIcon"] {
        color: #00D4C8 !important;
    }
    
    /* Layout Cards & Containers */
    div[data-testid="stVerticalBlockBorderWrapper"], .card-container, .kpi-card-circular, .suggestion-card {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.04) !important;
        border-radius: 12px !important;
        padding: 20px !important;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2) !important;
        transition: all 0.2s ease-in-out !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover, .card-container:hover, .kpi-card-circular:hover, .suggestion-card:hover {
        border-color: rgba(0, 212, 200, 0.3) !important;
        box-shadow: 0 10px 30px rgba(0, 212, 200, 0.08) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Circular progress indicator layout */
    .kpi-card-circular {
        text-align: center;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
        padding: 16px !important;
    }
    
    .kpi-title {
        font-size: 0.65rem;
        font-weight: 600;
        color: #A8A8A8;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    
    .kpi-subtitle {
        font-size: 0.75rem;
        font-weight: 500;
        margin-top: 2px;
        color: #A8A8A8;
    }
    
    /* Section Headers */
    .section-header-styled {
        font-size: 0.95rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 16px;
        border-left: 2px solid #00D4C8;
        padding-left: 10px;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    
    /* Custom Drag-and-Drop zone uploader */
    div[data-testid="stFileUploader"] {
        background-color: #151515 !important;
        border: 2px dashed rgba(0, 212, 200, 0.2) !important;
        border-radius: 16px !important;
        padding: 24px !important;
        transition: border-color 0.2s ease !important;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: #00D4C8 !important;
    }
    
    /* Input field overrides */
    div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea, div[data-testid="stSelectbox"] select {
        background-color: #151515 !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 8px !important;
        font-size: 0.9rem !important;
    }
    div[data-testid="stTextInput"] input:focus, div[data-testid="stTextArea"] textarea:focus {
        border-color: #00D4C8 !important;
        box-shadow: 0 0 10px rgba(0, 212, 200, 0.15) !important;
    }
    
    /* Progress bar overrides */
    div[data-testid="stProgress"] > div > div > div {
        background: linear-gradient(135deg, #00D4C8 0%, #00B8B8 100%) !important;
        border-radius: 4px !important;
    }
    
    /* Button styles */
    button[kind="secondary"] {
        background-color: #151515 !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 8px !important;
        padding: 8px 18px !important;
        font-size: 0.85rem !important;
        transition: all 0.15s ease !important;
    }
    button[kind="secondary"]:hover {
        border-color: #00D4C8 !important;
        color: #00D4C8 !important;
    }
    button[kind="primary"] {
        background: linear-gradient(135deg, #00D4C8 0%, #00B8B8 100%) !important;
        color: #0A0A0A !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        box-shadow: 0 4px 15px rgba(0, 212, 200, 0.15) !important;
        transition: all 0.15s ease !important;
    }
    button[kind="primary"]:hover {
        background: linear-gradient(135deg, #00B8B8 0%, #00D4C8 100%) !important;
        box-shadow: 0 4px 20px rgba(0, 212, 200, 0.35) !important;
        transform: scale(1.02);
    }
    
    /* Chip Badges */
    .skill-badge {
        display: inline-block;
        padding: 4px 12px;
        margin: 4px;
        border-radius: 12px;
        font-weight: 500;
        font-size: 0.8rem;
    }
    .badge-matched {
        background-color: rgba(0, 212, 200, 0.08);
        color: #00D4C8;
        border: 1px solid rgba(0, 212, 200, 0.2);
    }
    .badge-missing {
        background-color: transparent;
        color: #A8A8A8;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .badge-recommended {
        background-color: rgba(255, 255, 255, 0.02);
        color: #A8A8A8;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Chip List items */
    .list-item-matched {
        color: #ffffff;
        font-size: 0.88rem;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
    }
    .list-item-matched::before {
        content: "";
        display: inline-block;
        width: 6px;
        height: 6px;
        background-color: #00D4C8;
        border-radius: 50%;
        margin-right: 10px;
    }
    .list-item-missing {
        color: #A8A8A8;
        font-size: 0.88rem;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
    }
    .list-item-missing::before {
        content: "";
        display: inline-block;
        width: 6px;
        height: 6px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        margin-right: 10px;
    }
    
    /* Stacked cards */
    .suggestion-card {
        background-color: #151515;
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 12px;
        transition: border-color 0.2s ease;
    }
    .suggestion-card:hover {
        border-color: #00D4C8;
    }
    .suggestion-priority {
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        color: #00D4C8;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }
    
    /* Chat layout styling */
    .chat-bubble-user {
        background-color: #151515;
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px 12px 0 12px;
        padding: 14px 18px;
        margin-bottom: 12px;
        max-width: 80%;
        margin-left: auto;
        font-size: 0.9rem;
    }
    .chat-bubble-assistant {
        background-color: #111111;
        border: 1px solid rgba(255, 255, 255, 0.02);
        border-radius: 12px 12px 12px 0;
        padding: 14px 18px;
        margin-bottom: 12px;
        max-width: 80%;
        font-size: 0.9rem;
    }
    
    div.block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Sidebar Navigation Links
# -----------------------------
profile_html = """
<div class="profile-header">
    <div class="avatar-container">
        <div class="avatar-circle">CP</div>
    </div>
    <div class="profile-info">
        <div class="profile-name">CareerPilot.ai</div>
        <div class="profile-subtitle">My Workspace</div>
    </div>
    <div class="profile-arrow">▼</div>
</div>
"""
st.sidebar.markdown(profile_html, unsafe_allow_html=True)

# Main Dashboard Button
is_dash = st.session_state.active_page == "Dashboard"
if st.sidebar.button("Dashboard", key="nav_Dashboard", type="primary" if is_dash else "secondary", icon=":material/dashboard:"):
    st.session_state.active_page = "Dashboard"
    st.rerun()

st.sidebar.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

# Category: ANALYZE
st.sidebar.markdown('<div class="sidebar-category">Analyze</div>', unsafe_allow_html=True)
nav_items_analyze = {
    "Resume Analysis": ":material/analytics:",
    "Skill Analysis": ":material/psychology:",
    "AI Suggestions": ":material/auto_awesome:",
    "Resume Rewriter": ":material/edit_note:",
    "Cover Letter": ":material/mail:"
}
for label, icon in nav_items_analyze.items():
    is_active = st.session_state.active_page == label
    if st.sidebar.button(label, key=f"nav_{label}", type="primary" if is_active else "secondary", icon=icon):
        st.session_state.active_page = label
        st.rerun()

st.sidebar.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

# Category: COACH & PREP
st.sidebar.markdown('<div class="sidebar-category">Coach & Prep</div>', unsafe_allow_html=True)
nav_items_coach = {
    "Career Assistant": ":material/forum:",
    "Interview Preparation": ":material/quiz:"
}
for label, icon in nav_items_coach.items():
    is_active = st.session_state.active_page == label
    if st.sidebar.button(label, key=f"nav_{label}", type="primary" if is_active else "secondary", icon=icon):
        st.session_state.active_page = label
        st.rerun()

st.sidebar.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

# Category: GENERATOR
st.sidebar.markdown('<div class="sidebar-category">Generator</div>', unsafe_allow_html=True)
nav_items_generator = {
    "Resume Generator": ":material/description:",
    "Templates": ":material/dashboard_customize:",
    "LaTeX Generator": ":material/terminal:",
    "Download PDF": ":material/download:"
}
for label, icon in nav_items_generator.items():
    is_active = st.session_state.active_page == label
    if st.sidebar.button(label, key=f"nav_{label}", type="primary" if is_active else "secondary", icon=icon):
        st.session_state.active_page = label
        st.rerun()

st.sidebar.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

# Category: TRACKING & CONFIG
st.sidebar.markdown('<div class="sidebar-category">Tracking & Config</div>', unsafe_allow_html=True)
nav_items_tracking = {
    "Resume History": ":material/history:",
    "Career Analytics": ":material/bar_chart:",
    "Settings": ":material/settings:"
}
for label, icon in nav_items_tracking.items():
    is_active = st.session_state.active_page == label
    if st.sidebar.button(label, key=f"nav_{label}", type="primary" if is_active else "secondary", icon=icon):
        st.session_state.active_page = label
        st.rerun()

# -----------------------------
# Navigation State Helpers
# -----------------------------
def go_to_page(page_name):
    st.session_state.active_page = page_name
    st.rerun()

def requires_analysis(redirect_page="Resume Analysis"):
    if not st.session_state.parsed_resume or not st.session_state.analysis_result:
        st.warning("Please upload a resume and job description to run an analysis first.")
        if st.button("Go to Resume Analysis", type="primary"):
            go_to_page(redirect_page)
        st.stop()

# -----------------------------
# SVG Progress Ring Helper
# -----------------------------
def render_circular_progress(score, label, subtitle):
    circumference = 251.2
    dashoffset = circumference * (1 - score / 100.0)
    return f"""
    <div class="kpi-card-circular">
        <div class="kpi-title">{label}</div>
        <div style="margin: 15px 0;">
            <svg width="86" height="86" viewBox="0 0 100 100">
                <defs>
                    <linearGradient id="tealGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#00D4C8" />
                        <stop offset="100%" stop-color="#00B8B8" />
                    </linearGradient>
                </defs>
                <circle cx="50" cy="50" r="40" stroke="rgba(255,255,255,0.02)" stroke-width="6" fill="transparent" />
                <circle cx="50" cy="50" r="40" stroke="url(#tealGrad)" stroke-width="6" fill="transparent"
                        stroke-dasharray="251.2" stroke-dashoffset="{dashoffset}" stroke-linecap="round"
                        style="filter: drop-shadow(0 0 4px rgba(0, 212, 200, 0.4));" />
                <text x="50" y="56" fill="#ffffff" font-size="20" font-weight="700" text-anchor="middle">{score}%</text>
            </svg>
        </div>
        <div class="kpi-subtitle" style="color: #00D4C8;">{subtitle}</div>
    </div>
    """

def render_kpi_numeric(value, label, subtitle):
    return f"""
    <div class="kpi-card-circular">
        <div class="kpi-title">{label}</div>
        <div style="font-size: 2.5rem; font-weight: 700; color: #ffffff; margin: 16px 0; line-height: 1;">
            <span style="background: linear-gradient(135deg, #00D4C8 0%, #00B8B8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; filter: drop-shadow(0 0 4px rgba(0,212,200,0.25));">{value}</span>
        </div>
        <div class="kpi-subtitle" style="color: #00D4C8;">{subtitle}</div>
    </div>
    """

# Helper to style Plotly figures consistently
def style_plotly_chart(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Tahoma", color="#A8A8A8"),
        margin=dict(l=10, r=10, t=15, b=10),
        xaxis=dict(showgrid=False, color="#444444"),
        yaxis=dict(showgrid=True, gridcolor='#222222', color="#444444"),
    )
    return fig

# -----------------------------
# Back to Dashboard Helper
# -----------------------------
def render_back_button():
    col_back, _ = st.columns([1.5, 8.5])
    with col_back:
        if st.button("← Back to Dashboard", key="global_back_btn_" + st.session_state.active_page.replace(" ", "_"), type="secondary"):
            st.session_state.active_page = "Dashboard"
            st.rerun()
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# VIEW: DASHBOARD (Default / Home Command Center)
# -----------------------------------------------------------------------------
if st.session_state.active_page == "Dashboard":
    db = db_helper.load_db()
    history = db.get("resume_history", [])
    
    # Header Section
    col_dh1, col_dh2 = st.columns([2, 1])
    with col_dh1:
        st.markdown('<h1 style="margin: 0; font-weight: 700; letter-spacing: -0.03em; color:#ffffff;">Welcome Back</h1>', unsafe_allow_html=True)
        st.markdown('<p style="color:#A8A8A8; font-size:0.95rem; margin-top:2px;">CareerPilot AI Command Center</p>', unsafe_allow_html=True)
    with col_dh2:
        col_dhb1, col_dhb2 = st.columns(2)
        with col_dhb1:
            if st.button("New Analysis", key="dh_new_btn", use_container_width=True):
                st.session_state.parsed_resume = None
                st.session_state.analysis_result = None
                st.session_state.rewritten_resume = None
                go_to_page("Resume Analysis")
        with col_dhb2:
            if st.button("Settings", key="dh_settings_btn", use_container_width=True):
                go_to_page("Settings")
                
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    
    # If no analysis exists yet, show a welcome landing zone in the dashboard
    if not st.session_state.analysis_result:
        with st.container(border=True):
            st.markdown('<div style="text-align: center; padding: 40px 10px;">', unsafe_allow_html=True)
            st.markdown('<h2 style="font-weight: 700; color: #ffffff; margin-top: 0;">Get Started with CareerPilot AI</h2>', unsafe_allow_html=True)
            st.markdown('<p style="color:#A8A8A8; font-size: 0.95rem; margin-bottom: 25px;">Upload your resume and paste your target job description to audit your credentials and generate PDF packages.</p>', unsafe_allow_html=True)
            if st.button("Begin Resume Optimization", type="primary"):
                go_to_page("Resume Analysis")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        res = st.session_state.analysis_result
        
        # ROW 1: 7 KPI Cards (ATS Score, Keyword Coverage, Resume Quality, Matched, Missing, Tech, Soft)
        kpi_cols = st.columns(7)
        with kpi_cols[0]:
            st.markdown(render_circular_progress(res["ats_score"], "ATS Score", "Excellent Match" if res["ats_score"]>=80 else "Good Match"), unsafe_allow_html=True)
        with kpi_cols[1]:
            st.markdown(render_circular_progress(res["keyword_coverage"], "Keyword Coverage", "Good Coverage" if res["keyword_coverage"]>=70 else "Weak Coverage"), unsafe_allow_html=True)
        with kpi_cols[2]:
            st.markdown(render_circular_progress(res["resume_quality_score"], "Resume Quality", "Excellent" if res["resume_quality_score"]>=80 else "Good"), unsafe_allow_html=True)
        with kpi_cols[3]:
            st.markdown(render_kpi_numeric(len(res["matched_skills"]), "Matched Skills", "Out of 20"), unsafe_allow_html=True)
        with kpi_cols[4]:
            st.markdown(render_kpi_numeric(len(res["missing_skills"]), "Missing Skills", "Important Gaps"), unsafe_allow_html=True)
        with kpi_cols[5]:
            st.markdown(render_kpi_numeric(res["technical_skills_count"], "Technical Skills", "In Resume"), unsafe_allow_html=True)
        with kpi_cols[6]:
            st.markdown(render_kpi_numeric(res["soft_skills_count"], "Soft Skills", "In Resume"), unsafe_allow_html=True)
            
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        
        # ROW 2: Main Grid Split (Left 2/3, Right 1/3)
        col_grid_left, col_grid_right = st.columns([2, 1.1])
        
        with col_grid_left:
            # Sub-row 1: Match Score Progress & Recent Analysis
            col_sl1, col_sl2 = st.columns(2)
            with col_sl1:
                with st.container(border=True):
                    st.markdown('<div class="section-header-styled">Resume Progress</div>', unsafe_allow_html=True)
                    if history:
                        df_hist = pd.DataFrame(history)
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=df_hist["version"],
                            y=df_hist["score"],
                            mode="lines+markers",
                            line=dict(color='#00D4C8', width=2),
                            marker=dict(size=6, color='#00B8B8'),
                            fill='tozeroy',
                            fillcolor='rgba(0, 212, 200, 0.03)'
                        ))
                        fig = style_plotly_chart(fig)
                        fig.update_layout(height=180)
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                    else:
                        st.write("No progress logs recorded.")
            with col_sl2:
                with st.container(border=True):
                    st.markdown('<div class="section-header-styled">Recent Analysis</div>', unsafe_allow_html=True)
                    if history:
                        df_table = pd.DataFrame(history).tail(3).iloc[::-1]
                        table_html = (
                            "<table style='width:100%; border-collapse:collapse; font-size:0.85rem; color:#A8A8A8; text-align:left;'>"
                            "<thead>"
                            "<tr style='border-bottom:1px solid rgba(255,255,255,0.05); color:#555555;'>"
                            "<th style='padding:6px 2px;'>Version</th>"
                            "<th style='padding:6px 2px;'>ATS Score</th>"
                            "<th style='padding:6px 2px;'>Date</th>"
                            "</tr>"
                            "</thead>"
                            "<tbody>"
                        )
                        for idx, row in df_table.iterrows():
                            table_html += (
                                "<tr style='border-bottom:1px solid rgba(255,255,255,0.02);'>"
                                f"<td style='padding:8px 2px; font-weight:500; color:#ffffff;'>{row['version']}</td>"
                                f"<td style='padding:8px 2px; color:#00D4C8; font-weight:600;'>{row['score']}%</td>"
                                f"<td style='padding:8px 2px; color:#555555;'>{row['timestamp'][:10]}</td>"
                                "</tr>"
                            )
                        table_html += "</tbody></table>"
                        st.markdown(table_html, unsafe_allow_html=True)
                    else:
                        st.write("No prior logs logged.")
                
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            
            # Sub-row 2: Quick Actions & Application Tracker
            col_ql1, col_ql2 = st.columns([1, 1])
            with col_ql1:
                with st.container(border=True):
                    st.markdown('<div class="section-header-styled">Quick Actions</div>', unsafe_allow_html=True)
                    col_btn_qa1, col_btn_qa2 = st.columns(2)
                    with col_btn_qa1:
                        if st.button("Resume Analysis", key="qa_upload", use_container_width=True):
                            go_to_page("Resume Analysis")
                        if st.button("Rewrite Text", key="qa_rewrite", use_container_width=True):
                            go_to_page("Resume Rewriter")
                    with col_btn_qa2:
                        if st.button("Career Coach", key="qa_coach", use_container_width=True):
                            go_to_page("Career Assistant")
                        if st.button("Prep Interviews", key="qa_prep", use_container_width=True):
                            go_to_page("Interview Preparation")
            with col_ql2:
                with st.container(border=True):
                    st.markdown('<div class="section-header-styled">Application Tracker</div>', unsafe_allow_html=True)
                    apps = db.get("applications", [])
                    if apps:
                        df_apps = pd.DataFrame(apps)
                        status_counts = df_apps["status"].value_counts()
                        st.write(f"Active Logs: **{len(apps)}** | Offers Received: **{status_counts.get('Offer', 0)}** | Decided: **{status_counts.get('Rejected', 0) + status_counts.get('Offer', 0)}**")
                    else:
                        st.write("No active logs in tracker.")
                    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                    if st.button("Open Tracker", key="qa_tracker", use_container_width=True):
                        go_to_page("Career Analytics")
                
        with col_grid_right:
            with st.container(border=True):
                st.markdown('<div class="section-header-styled">Latest Suggestions</div>', unsafe_allow_html=True)
                for i, (priority, item) in enumerate(list(res["ai_suggestions"].items())[:3]):
                    st.markdown(
                        f"""
                        <div class="suggestion-card" style="padding: 12px; margin-bottom: 8px; background-color: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.04); border-radius: 12px;">
                            <div class="suggestion-priority">{priority}</div>
                            <div class="suggestion-title" style="font-size: 0.88rem;">{item['title']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                if st.button("Review All Suggestions", key="btn_view_sug_dash", use_container_width=True):
                    go_to_page("AI Suggestions")

# -----------------------------------------------------------------------------
# VIEW: RESUME ANALYSIS (File Upload & JD)
# -----------------------------------------------------------------------------
elif st.session_state.active_page == "Resume Analysis":
    render_back_button()
    st.title("Resume Analysis")
    st.markdown("Initiate career analysis by uploading your resume and pasting the job description.")
    
    col_up, col_jd = st.columns([1, 1.1])
    
    with col_up:
        st.subheader("Upload Resume File")
        
        # File uploader (CSS styled drag-and-drop container)
        uploaded_file = st.file_uploader(
            "Upload Resume",
            type=["pdf", "docx"],
            help="Supported formats: PDF, DOCX (Max: 200MB)"
        )
        
        if uploaded_file:
            st.success(f"File Selected: {uploaded_file.name}")
            try:
                with st.spinner("Extracting resume contents..."):
                    st.session_state.resume_name = uploaded_file.name
                    st.session_state.resume_text = parser.extract_resume_text(uploaded_file)
                    st.session_state.parsed_resume = parser.parse_resume_to_json(st.session_state.resume_text)
                st.info("Resume parsed successfully. Proceed by adding target Job Description details.")
            except Exception as e:
                st.error(f"Error parsing resume: {e}")
                
    with col_jd:
        st.subheader("Job Post Details")
        job_desc = st.text_area(
            "Paste Job Description",
            value=st.session_state.job_description,
            height=300,
            placeholder="Paste target job specifications here..."
        )
        st.session_state.job_description = job_desc
        
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    if st.button("Run Match Analysis", type="primary", use_container_width=True):
        if not st.session_state.parsed_resume:
            st.error("Please upload your resume file first.")
        elif not job_desc.strip():
            st.error("Please enter the target job description details.")
        elif not st.session_state.api_key:
            st.error("API Key not set. Configure it under the Settings page.")
        else:
            with st.spinner("Matching credentials with job post requirements..."):
                try:
                    st.session_state.analysis_result = analyzer.analyze_resume_vs_jd(
                        st.session_state.parsed_resume,
                        job_desc
                    )
                    # Add to history
                    db_helper.add_resume_history(
                        version_name=f"V{len(db_helper.load_db()['resume_history']) + 1} ({st.session_state.resume_name[:12]})",
                        score=st.session_state.analysis_result["ats_score"],
                        keyword_coverage=st.session_state.analysis_result["keyword_coverage"],
                        missing_count=len(st.session_state.analysis_result["missing_skills"])
                    )
                    st.success("Analysis complete!")
                    go_to_page("Dashboard")
                except Exception as e:
                    st.error(f"Analysis failed: {e}")

# -----------------------------------------------------------------------------
# VIEW: SKILL ANALYSIS
# -----------------------------------------------------------------------------
elif st.session_state.active_page == "Skill Analysis":
    render_back_button()
    requires_analysis("Resume Analysis")
    res = st.session_state.analysis_result
    
    st.title("Skill Analysis")
    st.markdown("Detailed breakdown of matching, missing, and recommended skills.")
    
    col_sa1, col_sa2 = st.columns(2)
    with col_sa1:
        skills_html = "".join([f"<span class='skill-badge badge-matched'>{skill}</span>" for skill in res["matched_skills"]])
        st.markdown(f'<div class="card-container"><div class="section-header-styled">Matched Skills</div>{skills_html}</div>', unsafe_allow_html=True)
    with col_sa2:
        skills_html = "".join([f"<span class='skill-badge badge-missing'>{skill}</span>" for skill in res["missing_skills"]])
        st.markdown(f'<div class="card-container"><div class="section-header-styled">Missing Skills</div>{skills_html}</div>', unsafe_allow_html=True)
        
    skills_html = "".join([f"<span class='skill-badge badge-recommended'>{skill}</span>" for skill in res["recommended_skills"]])
    st.markdown(f'<div class="card-container"><div class="section-header-styled">Recommended Adjacent Skills</div>{skills_html}</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# VIEW: AI SUGGESTIONS
# -----------------------------------------------------------------------------
elif st.session_state.active_page == "AI Suggestions":
    render_back_button()
    requires_analysis("Resume Analysis")
    res = st.session_state.analysis_result
    
    st.title("AI Suggestions")
    st.markdown("Prioritized improvements to maximize ATS compliance.")
    
    for i, (priority, item) in enumerate(res["ai_suggestions"].items()):
        st.markdown(
            textwrap.dedent(f"""
            <div class="card-container">
                <div class="suggestion-priority">{priority}</div>
                <div class="suggestion-title">{item['title']}</div>
                <div class="suggestion-explanation">{item['explanation']}</div>
            </div>
            """),
            unsafe_allow_html=True
        )
        col_act1, col_act2 = st.columns([1, 4])
        with col_act1:
            if st.button("Improve", key=f"sug_imp_{i}"):
                go_to_page("Resume Rewriter")

# -----------------------------------------------------------------------------
# VIEW: RESUME REWRITER
# -----------------------------------------------------------------------------
elif st.session_state.active_page == "Resume Rewriter":
    render_back_button()
    requires_analysis("Resume Analysis")
    st.title("Resume Rewriter")
    st.markdown("Rewrite resume sections dynamically using AI.")
    
    if st.button("Optimize Content Sections", type="primary"):
        with st.spinner("Rewriting sections..."):
            try:
                st.session_state.rewritten_resume = analyzer.rewrite_resume_content(
                    st.session_state.parsed_resume,
                    st.session_state.job_description
                )
                st.success("Sections optimized successfully!")
            except Exception as e:
                st.error(f"Error during rewrite: {e}")
                
    if st.session_state.rewritten_resume:
        orig = st.session_state.parsed_resume
        opt = st.session_state.rewritten_resume
        
        sec_choice = st.selectbox("Select Section to Review", ["Summary", "Experience", "Projects", "Skills"])
        
        if sec_choice == "Summary":
            col_left, col_right = st.columns(2)
            with col_left:
                text_val = orig.get("summary") or "No summary found."
                st.markdown(f'<div class="card-container"><div class="section-header-styled">Original Text</div><p style="font-size:0.9rem; line-height:1.4; color:#A8A8A8; margin:0;">{text_val}</p></div>', unsafe_allow_html=True)
            with col_right:
                text_val = opt.get("summary") or ""
                st.markdown(f'<div class="card-container"><div class="section-header-styled">AI Rewritten Text</div><pre style="background:rgba(255,255,255,0.01); border:1px solid rgba(255,255,255,0.03); padding:10px; border-radius:6px; color:#ffffff; font-family:monospace; font-size:0.85rem; white-space:pre-wrap; margin:0;">{text_val}</pre></div>', unsafe_allow_html=True)
        elif sec_choice == "Experience":
            for i, (orig_exp, opt_exp) in enumerate(zip(orig.get("experience", []), opt.get("experience", []))):
                st.markdown(f"#### Role {i+1}: {orig_exp.get('role')} at {orig_exp.get('company')}")
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    bullets = "".join([f"<li style='margin-bottom:6px;'>{pt}</li>" for pt in orig_exp.get("bullet_points", [])])
                    st.markdown(f'<div class="card-container"><div class="section-header-styled">Original Text</div><ul style="padding-left:20px; font-size:0.88rem; line-height:1.4; color:#A8A8A8; margin:0;">{bullets}</ul></div>', unsafe_allow_html=True)
                with col_e2:
                    bullets = "".join([f"<li style='margin-bottom:6px;'>{pt}</li>" for pt in opt_exp.get("bullet_points", [])])
                    st.markdown(f'<div class="card-container"><div class="section-header-styled">AI Rewritten Text</div><ul style="padding-left:20px; font-size:0.88rem; line-height:1.4; color:#ffffff; margin:0;">{bullets}</ul></div>', unsafe_allow_html=True)
                st.markdown("---")
        elif sec_choice == "Projects":
            for i, (orig_proj, opt_proj) in enumerate(zip(orig.get("projects", []), opt.get("projects", []))):
                st.markdown(f"#### Project {i+1}: {orig_proj.get('name')}")
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    bullets = "".join([f"<li style='margin-bottom:6px;'>{pt}</li>" for pt in orig_proj.get("bullet_points", [])])
                    st.markdown(f'<div class="card-container"><div class="section-header-styled">Original Text</div><ul style="padding-left:20px; font-size:0.88rem; line-height:1.4; color:#A8A8A8; margin:0;">{bullets}</ul></div>', unsafe_allow_html=True)
                with col_p2:
                    bullets = "".join([f"<li style='margin-bottom:6px;'>{pt}</li>" for pt in opt_proj.get("bullet_points", [])])
                    st.markdown(f'<div class="card-container"><div class="section-header-styled">AI Rewritten Text</div><ul style="padding-left:20px; font-size:0.88rem; line-height:1.4; color:#ffffff; margin:0;">{bullets}</ul></div>', unsafe_allow_html=True)
                st.markdown("---")
        elif sec_choice == "Skills":
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.caption("Original Structure")
                st.json(orig.get("skills"))
            with col_s2:
                st.caption("Optimized Structure")
                st.json(opt.get("skills"))

# -----------------------------------------------------------------------------
# VIEW: COVER LETTER
# -----------------------------------------------------------------------------
elif st.session_state.active_page == "Cover Letter":
    render_back_button()
    requires_analysis("Resume Analysis")
    st.title("Cover Letter")
    st.markdown("Generate a business cover letter tailored to your credentials.")
    
    company_role = st.text_input("Company Name & Target Role", placeholder="e.g. Vercel - Frontend Engineer")
    
    if st.button("Generate Tailored Letter", type="primary"):
        if not company_role.strip():
            st.error("Please enter company and role details.")
        else:
            with st.spinner("Generating..."):
                try:
                    letter = analyzer.generate_cover_letter(
                        st.session_state.resume_text,
                        st.session_state.job_description,
                        company_role
                    )
                    st.session_state.cover_letter_text = letter
                    st.success("Cover letter generated!")
                except Exception as e:
                    st.error(f"Generation error: {e}")
                    
    if "cover_letter_text" in st.session_state:
        st.subheader("Generated Cover Letter")
        st.text_area("Copiable Letter Content", value=st.session_state.cover_letter_text, height=400)
        
        col_down1, col_down2 = st.columns([1, 4])
        with col_down1:
            st.download_button(
                "Download Text File",
                data=st.session_state.cover_letter_text,
                file_name="cover_letter.txt",
                mime="text/plain",
                use_container_width=True
            )

# -----------------------------------------------------------------------------
# VIEW: CAREER ASSISTANT
# -----------------------------------------------------------------------------
elif st.session_state.active_page == "Career Assistant":
    render_back_button()
    requires_analysis("Resume Analysis")
    st.title("Career Assistant")
    st.markdown("Interact with the AI career coach chatbot loaded with your profile context.")
    
    # Prompt Chips
    st.write("Suggested Prompts:")
    prompt_cols = st.columns(4)
    sel_prompt = ""
    with prompt_cols[0]:
        if st.button("Why is my ATS score low?", use_container_width=True):
            sel_prompt = "Why is my ATS score low?"
    with prompt_cols[1]:
        if st.button("Rewrite my summary", use_container_width=True):
            sel_prompt = "Rewrite my summary."
    with prompt_cols[2]:
        if st.button("Suggest projects", use_container_width=True):
            sel_prompt = "Suggest projects."
    with prompt_cols[3]:
        if st.button("Generate interview questions", use_container_width=True):
            sel_prompt = "Generate interview questions."
            
    # Init Chat
    if not st.session_state.chat_history:
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": "Hello! I am your career assistant. Ask me questions about improving your ATS match score, writing experience bullets, or preparing for interviews."
        })
        
    for msg in st.session_state.chat_history:
        div_class = "chat-bubble-user" if msg["role"] == "user" else "chat-bubble-assistant"
        st.markdown(f'<div class="{div_class}">{msg["content"]}</div>', unsafe_allow_html=True)
        
    user_input = st.chat_input("Ask your coach...")
    if sel_prompt:
        user_input = sel_prompt
        
    if user_input:
        st.markdown(f'<div class="chat-bubble-user">{user_input}</div>', unsafe_allow_html=True)
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        with st.spinner("Thinking..."):
            try:
                response = analyzer.chat_with_coach(
                    st.session_state.chat_history,
                    st.session_state.resume_text,
                    st.session_state.job_description,
                    st.session_state.analysis_result
                )
                st.markdown(f'<div class="chat-bubble-assistant">{response}</div>', unsafe_allow_html=True)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()
            except Exception as e:
                st.error(f"Chat error: {e}")

# -----------------------------------------------------------------------------
# VIEW: INTERVIEW PREPARATION
# -----------------------------------------------------------------------------
elif st.session_state.active_page == "Interview Preparation":
    render_back_button()
    requires_analysis("Resume Analysis")
    st.title("Interview Preparation")
    st.markdown("Prepare for interviews using customized questions or enter a mock interview session.")
    
    tab_prep, tab_mock = st.tabs(["Interview Preparation Guide", "Mock Interview Simulation"])
    
    with tab_prep:
        if st.button("Generate Questions Guide", type="primary"):
            with st.spinner("Formulating questions..."):
                try:
                    qs = analyzer.generate_interview_prep(
                        st.session_state.resume_text,
                        st.session_state.job_description
                    )
                    st.session_state.prep_questions = qs
                    st.success("Prep questions generated successfully!")
                except Exception as e:
                    st.error(f"Error generating questions: {e}")
                    
        if "prep_questions" in st.session_state:
            for q in st.session_state.prep_questions:
                with st.expander(f"{q['category']} ({q['difficulty']}) - {q['question']}"):
                    st.markdown("**Suggested Answer:**")
                    st.write(q["sample_answer"])
                    
    with tab_mock:
        mock_state = st.session_state.mock_interview
        if not mock_state["active"]:
            if st.button("Start Mock Interview Simulator", type="primary"):
                with st.spinner("Starting session..."):
                    try:
                        qs = analyzer.generate_interview_prep(
                            st.session_state.resume_text,
                            st.session_state.job_description
                        )
                        if qs:
                            mock_state["active"] = True
                            mock_state["questions"] = qs[:5]
                            mock_state["current_index"] = 0
                            mock_state["answers"] = []
                            mock_state["feedback"] = []
                            st.rerun()
                    except Exception as e:
                        st.error(f"Failed to start simulator: {e}")
        else:
            idx = mock_state["current_index"]
            total = len(mock_state["questions"])
            
            if idx < total:
                q_item = mock_state["questions"][idx]
                st.subheader(f"Question {idx+1} of {total} ({q_item['category']})")
                st.info(q_item["question"])
                
                ans = st.text_area("Your Response", height=150)
                if st.button("Submit Answer", type="primary"):
                    if not ans.strip():
                        st.error("Please enter a response.")
                    else:
                        with st.spinner("Evaluating response..."):
                            model = analyzer.genai.GenerativeModel("gemini-2.5-flash")
                            eval_prompt = f"Question: {q_item['question']}\nExpected: {q_item['sample_answer']}\nAnswer Given: {ans}\nGrade out of 10 and suggest improvements."
                            feedback = model.generate_content(eval_prompt).text
                            
                            mock_state["answers"].append(ans)
                            mock_state["feedback"].append(feedback)
                            mock_state["current_index"] += 1
                            st.rerun()
            else:
                st.success("Mock Interview complete!")
                for i in range(total):
                    st.markdown(f"### Q{i+1}: {mock_state['questions'][i]['question']}")
                    st.markdown(f"**Your Answer:** {mock_state['answers'][i]}")
                    st.markdown(f"**Feedback:**\n{mock_state['feedback'][i]}")
                    st.markdown("---")
                if st.button("Restart simulator"):
                    mock_state["active"] = False
                    st.rerun()

# -----------------------------------------------------------------------------
# VIEW: RESUME GENERATOR
# -----------------------------------------------------------------------------
elif st.session_state.active_page == "Resume Generator":
    render_back_button()
    requires_analysis("Resume Analysis")
    st.title("Resume Generator")
    st.markdown("Compile LaTeX code from parsed resume details.")
    
    active_data = st.session_state.rewritten_resume or st.session_state.parsed_resume
    template_choice = st.session_state.selected_template
    
    st.info(f"Target Template: **{template_choice}**")
    
    if st.button("Generate LaTeX Code Structure", type="primary"):
        with st.spinner("Compiling LaTeX template..."):
            try:
                code = compiler.render_latex(template_choice, active_data)
                st.session_state.latex_code = code
                st.success("LaTeX compiled successfully! Proceed to 'LaTeX Generator' page to compile PDF.")
            except Exception as e:
                st.error(f"Error compiling code: {e}")
                
    if "latex_code" in st.session_state:
        edited_code = st.text_area("LaTeX Source Editor", value=st.session_state.latex_code, height=450)
        if edited_code != st.session_state.latex_code:
            st.session_state.latex_code = edited_code

# -----------------------------------------------------------------------------
# VIEW: TEMPLATES
# -----------------------------------------------------------------------------
elif st.session_state.active_page == "Templates":
    render_back_button()
    requires_analysis("Resume Analysis")
    st.title("Templates Gallery")
    st.markdown("Select from professional LaTeX resume layouts.")
    
    templates_meta = [
        {"name": "VIT Academic Risk", "desc": "Devika J Nair Style. Gray headers, mathpazo serif font, very compact and professional."},
        {"name": "Classic Lines (xprilion)", "desc": "Anubhav Singh Style. Elegant horizontal lines dividing sections, highly readable software engineering layout."},
        {"name": "PwC Modern (adcv)", "desc": "Alessandro Rossini Style. Dual-column table layout, modern margins, clean section headers."}
    ]
    
    col_t1, col_t2 = st.columns(2)
    for i, t in enumerate(templates_meta):
        with col_t1 if i % 2 == 0 else col_t2:
            with st.container(border=True):
                st.markdown(f'<div class="section-header-styled">{t["name"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<p style="color:#A8A8A8; font-size:0.88rem; min-height:50px; margin:0;">{t["desc"]}</p>', unsafe_allow_html=True)
                
                is_selected = st.session_state.selected_template == t["name"]
                if is_selected:
                    st.markdown("<p style='color:#00D4C8; font-weight:600; font-size:0.85rem; margin-top:10px; margin-bottom:0;'>Active Layout</p>", unsafe_allow_html=True)
                else:
                    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
                    if st.button(f"Use {t['name']}", key=f"sel_t_{t['name']}", use_container_width=True):
                        st.session_state.selected_template = t["name"]
                        st.success(f"Layout changed to {t['name']}")
                        st.rerun()

# -----------------------------------------------------------------------------
# VIEW: LATEX GENERATOR
# -----------------------------------------------------------------------------
elif st.session_state.active_page == "LaTeX Generator":
    render_back_button()
    requires_analysis("Resume Analysis")
    st.title("LaTeX Generator")
    st.markdown("Compile LaTeX source code directly to PDF using local system tools or public API compiles.")
    
    if "latex_code" not in st.session_state:
        st.warning("Generate LaTeX code under 'Resume Generator' before compiling.")
    else:
        if st.button("Compile PDF Document", type="primary"):
            with st.spinner("Compiling (Local/Cloud)..."):
                try:
                    try:
                        with open("debug_resume.tex", "w", encoding="utf-8") as f:
                            f.write(st.session_state.latex_code)
                    except Exception as df_err:
                        print("Failed to save debug_resume.tex:", df_err)
                    pdf_bytes, status_msg = compiler.compile_latex_to_pdf(st.session_state.latex_code)
                    st.session_state.compiled_pdf = pdf_bytes
                    st.success(status_msg)
                    go_to_page("Download PDF")
                except Exception as e:
                    st.error(f"Compilation Failed: {e}")

# -----------------------------------------------------------------------------
# VIEW: DOWNLOAD PDF
# -----------------------------------------------------------------------------
elif st.session_state.active_page == "Download PDF":
    render_back_button()
    requires_analysis("Resume Analysis")
    st.title("Download PDF & Exports")
    st.markdown("Retrieve your compiled PDF, docx, plaintext, or raw LaTeX formats.")
    
    active_data = st.session_state.rewritten_resume or st.session_state.parsed_resume
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        with st.container(border=True):
            st.markdown('<div class="section-header-styled">PDF Document</div>', unsafe_allow_html=True)
            if "compiled_pdf" in st.session_state and st.session_state.compiled_pdf:
                st.download_button(
                    "Download PDF Document",
                    data=st.session_state.compiled_pdf,
                    file_name="resume.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
            else:
                st.warning("Compile PDF first under the 'LaTeX Generator' page.")
        
        st.markdown("<div style='height:15px;'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown('<div class="section-header-styled">LaTeX Source</div>', unsafe_allow_html=True)
            if "latex_code" in st.session_state:
                st.download_button(
                    "Download .tex File",
                    data=st.session_state.latex_code,
                    file_name="resume.tex",
                    mime="text/plain",
                    use_container_width=True
                )
            else:
                st.warning("Generate LaTeX first.")
        
    with col_d2:
        with st.container(border=True):
            st.markdown('<div class="section-header-styled">Word Document</div>', unsafe_allow_html=True)
            try:
                docx_data = compiler.generate_docx(active_data)
                st.download_button(
                    "Download DOCX Document",
                    data=docx_data,
                    file_name="resume.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"DOCX export error: {e}")
        
        st.markdown("<div style='height:15px;'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown('<div class="section-header-styled">Markdown & Text</div>', unsafe_allow_html=True)
            try:
                md_text = compiler.generate_md(active_data)
                st.download_button(
                    "Download Markdown",
                    data=md_text,
                    file_name="resume.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Markdown export error: {e}")

# -----------------------------------------------------------------------------
# VIEW: RESUME HISTORY
# -----------------------------------------------------------------------------
elif st.session_state.active_page == "Resume History":
    render_back_button()
    st.title("Resume History")
    st.markdown("Track and compare your resume scores and version updates.")
    
    db = db_helper.load_db()
    history = db.get("resume_history", [])
    
    if history:
        df_hist = pd.DataFrame(history)
        st.table(df_hist[["version", "timestamp", "score", "coverage", "missing_count"]])
        
        # Version comparison tool
        st.subheader("Compare Versions")
        if len(history) >= 2:
            col_comp1, col_comp2 = st.columns(2)
            with col_comp1:
                v1_choice = st.selectbox("Version A", df_hist["version"].unique(), index=0)
            with col_comp2:
                v2_choice = st.selectbox("Version B", df_hist["version"].unique(), index=len(df_hist["version"].unique())-1)
                
            row_a = df_hist[df_hist["version"] == v1_choice].iloc[0]
            row_b = df_hist[df_hist["version"] == v2_choice].iloc[0]
            
            # Display stats comparison cards
            with st.container(border=True):
                st.markdown('<div class="section-header-styled">Score Delta</div>', unsafe_allow_html=True)
                st.markdown(
                    textwrap.dedent(f"""
                    <div style="font-size: 1.1rem; color: #ffffff;">
                        {v1_choice} Match Score: <strong>{row_a['score']}%</strong><br>
                        {v2_choice} Match Score: <strong>{row_b['score']}%</strong><br>
                        Improvement: <strong>{row_b['score'] - row_a['score']}%</strong>
                    </div>
                    """),
                    unsafe_allow_html=True
                )
        else:
            st.info("Compare details will show here once you have analyzed at least 2 versions.")
    else:
        st.info("No prior uploads logged.")

# -----------------------------------------------------------------------------
# VIEW: CAREER ANALYTICS
# -----------------------------------------------------------------------------
elif st.session_state.active_page == "Career Analytics":
    render_back_button()
    st.title("Career Analytics")
    st.markdown("Applications ledger and pipeline performance charts.")
    
    # Form to add applications
    with st.form("add_app_an"):
        col_fa1, col_fa2 = st.columns(2)
        with col_fa1:
            title = st.text_input("Job Title")
            company = st.text_input("Company")
        with col_fa2:
            date_app = st.date_input("Applied Date", datetime.today())
            status_app = st.selectbox("Pipeline Status", ["Applied", "Interviewing", "Offer", "Rejected", "Pending"])
        score_app = st.number_input("Associated Score", min_value=0, max_value=100, value=75)
        
        if st.form_submit_button("Add Log Entry", type="primary"):
            if not title.strip() or not company.strip():
                st.error("Please enter job title and company details.")
            else:
                db_helper.add_application(title, company, date_app.strftime("%Y-%m-%d"), status_app, score_app)
                st.success("Logged entry added successfully!")
                st.rerun()
                
    st.markdown("<hr style='border-color:#222222;'>", unsafe_allow_html=True)
    
    db = db_helper.load_db()
    apps = db.get("applications", [])
    if not apps:
        st.info("No job application entries logged.")
    else:
        df = pd.DataFrame(apps)
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("### Application Pipeline Distribution")
            status_counts = df["status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]
            fig_p = px.pie(status_counts, values="Count", names="Status", hole=0.4, color_discrete_sequence=px.colors.sequential.Teal)
            fig_p = style_plotly_chart(fig_p)
            st.plotly_chart(fig_p, use_container_width=True)
        with col_g2:
            st.markdown("### Match Scores by Company")
            fig_b = px.bar(df, x="company", y="score", color="status", color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_b = style_plotly_chart(fig_b)
            st.plotly_chart(fig_b, use_container_width=True)
            
        st.subheader("Applications Ledger")
        for app in apps:
            with st.expander(f"{app['title']} at {app['company']} -- Status: {app['status']}"):
                col_st1, col_st2 = st.columns(2)
                with col_st1:
                    new_st = st.selectbox(
                        "Change Status",
                        ["Applied", "Interviewing", "Offer", "Rejected", "Pending"],
                        key=f"status_an_sel_{app['id']}",
                        index=["Applied", "Interviewing", "Offer", "Rejected", "Pending"].index(app["status"])
                    )
                    if new_st != app["status"]:
                        db_helper.update_application_status(app["id"], new_st)
                        st.success("Updated status successfully!")
                        st.rerun()
                with col_st2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("Delete Log", key=f"del_an_btn_{app['id']}", use_container_width=True):
                        db_helper.delete_application(app["id"])
                        st.success("Entry deleted.")
                        st.rerun()

# -----------------------------------------------------------------------------
# VIEW: SETTINGS
# -----------------------------------------------------------------------------
elif st.session_state.active_page == "Settings":
    render_back_button()
    st.title("Settings")
    st.markdown("Configure application environment parameters.")
    
    api_key_input = st.text_input("Gemini API Key", value=st.session_state.api_key, type="password")
    if st.button("Save Settings", type="primary"):
        st.session_state.api_key = api_key_input
        st.success("Settings saved! Reloading application environment...")
        st.rerun()
