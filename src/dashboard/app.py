import streamlit as st

import pages.home as home
import pages.profile as profile
import pages.screener as screener
import pages.peers as peers
import pages.trends as trends
import pages.sectors as sectors
import pages.capital as capital
import pages.reports as reports

st.set_page_config(
    page_title="Nifty 100 Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select Screen",
    [
        "Home",
        "Company Profile",
        "Screener",
        "Peer Comparison",
        "Trend Analysis",
        "Sector Analysis",
        "Capital Allocation",
        "Annual Reports"
    ]
)

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

else:
    reports.show()