import streamlit as st
from pages import capital, home, peers, profile, reports, screener, sectors, trends

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Nifty 100 Financial Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ==========================================================
# SESSION STATE
# ==========================================================

if "page" not in st.session_state:
    st.session_state.page = "Home"


# ==========================================================
# GLOBAL CSS
# ==========================================================

st.markdown(
    """
<style>

html, body, [data-testid="stAppViewContainer"] {
    background: #0f1115 !important;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(
            circle at 15% 0%,
            rgba(70, 85, 110, 0.18),
            transparent 32%
        ),
        radial-gradient(
            circle at 85% 100%,
            rgba(50, 70, 90, 0.15),
            transparent 35%
        ),
        #0f1115 !important;
}

[data-testid="stSidebar"] {
    display: none !important;
}

[data-testid="collapsedControl"] {
    display: none !important;
}

header[data-testid="stHeader"] {
    background: transparent !important;
}

.main .block-container {
    max-width: 1500px;
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
}


/* ==========================================================
   HEADER
   ========================================================== */

.topbar {
    background: rgba(24, 27, 33, 0.94);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 18px;
    padding: 18px 22px;
    margin-bottom: 14px;
    box-shadow: 0 10px 35px rgba(0,0,0,0.25);
}

.brand-title {
    color: #f5f7fa;
    font-size: 24px;
    font-weight: 700;
    letter-spacing: -0.5px;
    margin: 0;
}

.brand-subtitle {
    color: #8d95a3;
    font-size: 11px;
    letter-spacing: 1.5px;
    margin-top: 4px;
}


/* ==========================================================
   NAVIGATION BUTTONS
   ========================================================== */

.nav-button button {
    min-height: 42px !important;
    border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    background: rgba(31,35,42,0.85) !important;
    color: #aeb5c0 !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}

.nav-button button:hover {
    background: rgba(48,53,63,0.95) !important;
    color: white !important;
    border-color: rgba(255,255,255,0.14) !important;
    transform: translateY(-1px);
}


/* ==========================================================
   MAIN CONTENT
   ========================================================== */

.dashboard-container {
    background: rgba(20,23,29,0.78);
    border: 1px solid rgba(255,255,255,0.055);
    border-radius: 18px;
    padding: 12px 20px 25px 20px;
    box-shadow: 0 12px 40px rgba(0,0,0,0.20);
}


/* ==========================================================
   METRICS
   ========================================================== */

[data-testid="stMetric"] {
    background: rgba(30,34,41,0.88) !important;
    border: 1px solid rgba(255,255,255,0.055) !important;
    border-radius: 14px !important;
    padding: 16px !important;
    box-shadow: 0 6px 20px rgba(0,0,0,0.14) !important;
}

[data-testid="stMetricLabel"] {
    color: #9098a5 !important;
}

[data-testid="stMetricValue"] {
    color: #f3f5f7 !important;
}


/* ==========================================================
   TEXT
   ========================================================== */

h1 {
    color: #f5f7fa !important;
    font-weight: 700 !important;
}

h2 {
    color: #e7eaf0 !important;
}

h3 {
    color: #d7dce3 !important;
}

p {
    color: #b5bbc5;
}


/* ==========================================================
   INPUTS
   ========================================================== */

input,
textarea {
    background-color: #1b1f26 !important;
    color: #e8ebef !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
}

[data-baseweb="select"] > div {
    background-color: #1b1f26 !important;
    border-radius: 10px !important;
    border-color: rgba(255,255,255,0.08) !important;
}


/* ==========================================================
   DATAFRAMES
   ========================================================== */

[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
}


/* ==========================================================
   BUTTONS
   ========================================================== */

.stButton > button {
    border-radius: 10px;
    background: #20242c;
    color: #dce1e7;
    border: 1px solid rgba(255,255,255,0.07);
}

.stButton > button:hover {
    background: #2b3039;
    color: white;
    border-color: rgba(255,255,255,0.15);
}


/* ==========================================================
   DIVIDERS
   ========================================================== */

hr {
    border-color: rgba(255,255,255,0.06) !important;
}


/* ==========================================================
   FOOTER
   ========================================================== */

.footer {
    text-align: center;
    color: #626a76;
    font-size: 10px;
    padding: 20px 0 5px 0;
}

</style>
""",
    unsafe_allow_html=True,
)


# ==========================================================
# HEADER
# ==========================================================

st.markdown(
    """
<div class="topbar">
    <div class="brand-title">
        📊 NIFTY 100
    </div>
    <div class="brand-subtitle">
        FINANCIAL INTELLIGENCE PLATFORM
    </div>
</div>
""",
    unsafe_allow_html=True,
)


# ==========================================================
# NAVIGATION
# ==========================================================

pages = [
    ("🏠 Home", "Home"),
    ("🏢 Profile", "Company Profile"),
    ("🔎 Screener", "Screener"),
    ("👥 Peers", "Peer Comparison"),
    ("📈 Trends", "Trend Analysis"),
    ("🏭 Sectors", "Sector Analysis"),
    ("💰 Capital", "Capital Allocation"),
    ("📄 Reports", "Annual Reports"),
]


nav_columns = st.columns(len(pages))


for column, (label, page_name) in zip(nav_columns, pages):

    with column:

        if st.button(
            label,
            key=f"nav_{page_name}",
            use_container_width=True,
        ):
            st.session_state.page = page_name
            st.rerun()


# ==========================================================
# MAIN CONTENT
# ==========================================================

st.markdown(
    '<div class="dashboard-container">',
    unsafe_allow_html=True,
)


page = st.session_state.page


if page == "Home":
    home.show()

elif page == "Company Profile":
    profile.show()

elif page == "Screener":
    screener.show()

elif page == "Peer Comparison":
    peers.show()

elif page == "Trend Analysis":
    trends.show()

elif page == "Sector Analysis":
    sectors.show()

elif page == "Capital Allocation":
    capital.show()

elif page == "Annual Reports":
    reports.show()


st.markdown(
    "</div>",
    unsafe_allow_html=True,
)


# ==========================================================
# FOOTER
# ==========================================================

st.markdown(
    """
<div class="footer">
    Nifty 100 Financial Intelligence Platform
    &nbsp;•&nbsp;
    Financial Analytics Dashboard
</div>
""",
    unsafe_allow_html=True,
)
