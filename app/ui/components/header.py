"""InsightSphere application header."""

import streamlit as st


def render_header() -> None:
    """Render the InsightSphere brand header."""

    # Brand mark and application name
    logo_col, brand_col = st.columns([0.7, 10], vertical_alignment="center")

    with logo_col:
        st.markdown(
            """
            <div style="
                display: flex;
                align-items: center;
                justify-content: center;
                width: 42px;
                height: 42px;
                border-radius: 12px;
                background-color: #3978C5;
                color: #FFFFFF;
                font-size: 1.4rem;
                font-weight: 800;
            ">I</div>
            """,
            unsafe_allow_html=True,
        )

    with brand_col:
        st.markdown(
            """
            <div style="
                font-size: 1.45rem;
                font-weight: 750;
                color: #243B53;
                letter-spacing: -0.5px;
            ">InsightSphere</div>
            <div style="
                font-size: 0.88rem;
                color: #718096;
            ">One workspace for all your data.</div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <hr style="
            border: none;
            border-top: 1px solid #DCE5F0;
            margin-top: 0.75rem;
            margin-bottom: 1.5rem;
        ">
        """,
        unsafe_allow_html=True,
    )