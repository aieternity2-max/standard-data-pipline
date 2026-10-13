"""Sidebar navigation for InsightSphere."""

import streamlit as st


NAVIGATION_ITEMS = [
    ("Overview", "⌂"),
    ("Upload Data", "⇧"),
    ("Explore Data", "▦"),
    ("Search", "⌕"),
    ("Ask AI", "✧"),
    ("Dashboards", "▥"),
    ("Activity & Status", "◷"),
    ("Settings", "⚙"),
]


def render_sidebar() -> str:
    """Render navigation and return the selected page."""

    with st.sidebar:
        st.markdown(
            """
            <div style="padding:0.75rem 0 1.25rem 0;">
                <div style="
                    color:#718096;
                    font-size:0.75rem;
                    font-weight:700;
                    letter-spacing:1px;
                    text-transform:uppercase;
                ">WORKSPACE</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        selected_page = st.radio(
            "Workspace navigation",
            options=[item[0] for item in NAVIGATION_ITEMS],
            format_func=lambda page: (
                f"{dict((name, icon) for name, icon in NAVIGATION_ITEMS)[page]}"
                f"   {page}"
            ),
            label_visibility="collapsed",
            key="insightsphere_navigation",
        )

        st.markdown("---")

        st.markdown(
            """
            <div style="
                padding:0.75rem;
                background:#FFFFFF;
                border:1px solid #DCE5F0;
                border-radius:12px;
            ">
                <div style="
                    font-size:0.82rem;
                    font-weight:700;
                    color:#243B53;
                ">Your data, connected</div>
                <div style="
                    margin-top:0.35rem;
                    font-size:0.76rem;
                    line-height:1.5;
                    color:#718096;
                ">
                    Explore information, find insights, and create reports
                    in one workspace.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return selected_page