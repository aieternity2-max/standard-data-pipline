"""Shared styling for the InsightSphere Streamlit application."""

import streamlit as st


def apply_global_styles() -> None:
    """Apply the approved InsightSphere light theme."""

    st.markdown(
        """
        <style>
        /* =========================================
           1. INSIGHTSPHERE DESIGN TOKENS
        ========================================= */

        :root {
            --insight-primary: #3978C5;
            --insight-primary-dark: #285E9E;
            --insight-background: #F4F7FB;
            --insight-surface: #FFFFFF;
            --insight-sidebar: #EAF1FA;
            --insight-accent: #DDF3EF;
            --insight-text: #243B53;
            --insight-muted: #718096;
            --insight-border: #DCE5F0;
            --insight-sidebar-hover: #DCE8F7;
            --insight-sidebar-selected: #D5E5FA;
        }

        /* =========================================
           2. MAIN APPLICATION
        ========================================= */

        .stApp {
            background-color: var(--insight-background);
            color: var(--insight-text);
        }

        [data-testid="stHeader"] {
            background-color: var(--insight-surface);
        }

        .block-container {
            max-width: 1440px;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        /* Main content headings */

        .stApp h1,
        .stApp h2,
        .stApp h3,
        .stApp h4 {
            color: var(--insight-text);
        }

        /* =========================================
           3. DASHBOARD METRIC CARDS
        ========================================= */

        [data-testid="stMetric"] {
            background-color: var(--insight-surface);
            border: 1px solid var(--insight-border);
            border-radius: 12px;
            padding: 1rem;
            box-shadow: 0 3px 12px rgba(36, 59, 83, 0.035);
        }

        [data-testid="stMetricLabel"],
        [data-testid="stMetricLabel"] p,
        [data-testid="stMetricLabel"] label,
        [data-testid="stMetricLabel"] div {
            color: var(--insight-muted) !important;
        }

        [data-testid="stMetricValue"],
        [data-testid="stMetricValue"] div,
        [data-testid="stMetricValue"] p {
            color: var(--insight-text) !important;
            font-weight: 700;
        }

        [data-testid="stMetricDelta"] {
            color: var(--insight-muted);
        }

        /* =========================================
           4. SIDEBAR BACKGROUND
        ========================================= */

        [data-testid="stSidebar"] {
            background-color: var(--insight-sidebar);
            border-right: 1px solid var(--insight-border);
            color: var(--insight-text);
        }

        [data-testid="stSidebar"] > div:first-child {
            background-color: var(--insight-sidebar);
        }

        [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
            background-color: var(--insight-sidebar);
        }

        /* Sidebar headings and regular text */

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span {
            color: var(--insight-text);
        }

        /* =========================================
           5. SIDEBAR NAVIGATION
        ========================================= */

        [data-testid="stSidebar"] [role="radiogroup"] {
            gap: 0.3rem;
        }

        [data-testid="stSidebar"] [role="radiogroup"] label {
            background-color: transparent;
            border-radius: 9px;
            padding: 0.45rem 0.6rem;
            color: var(--insight-text) !important;
            transition: background-color 0.15s ease;
        }

        [data-testid="stSidebar"] [role="radiogroup"] label p,
        [data-testid="stSidebar"] [role="radiogroup"] label span,
        [data-testid="stSidebar"] [role="radiogroup"] label div {
            color: var(--insight-text) !important;
        }

        [data-testid="stSidebar"] [role="radiogroup"] label:hover {
            background-color: var(--insight-sidebar-hover);
        }

        [data-testid="stSidebar"] [role="radiogroup"] label:has(
            input[type="radio"]:checked
        ) {
            background-color: var(--insight-sidebar-selected);
            color: var(--insight-primary-dark) !important;
            font-weight: 600;
        }

        [data-testid="stSidebar"] [role="radiogroup"] label:has(
            input[type="radio"]:checked
        ) p,
        [data-testid="stSidebar"] [role="radiogroup"] label:has(
            input[type="radio"]:checked
        ) span {
            color: var(--insight-primary-dark) !important;
        }

        [data-testid="stSidebar"] [role="radiogroup"] input[type="radio"] {
            accent-color: var(--insight-primary);
        }

        [data-testid="stSidebar"] button {
            border-radius: 8px;
            color: var(--insight-text);
        }

        [data-testid="stSidebar"] hr {
            border-color: var(--insight-border);
        }

        /* =========================================
           6. BRANDING
        ========================================= */

        .insight-brand {
            font-size: 1.45rem;
            font-weight: 750;
            letter-spacing: -0.5px;
            color: var(--insight-text);
        }

        .insight-brand-mark {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 38px;
            height: 38px;
            margin-right: 10px;
            border-radius: 12px;
            background: var(--insight-primary);
            color: #FFFFFF;
            font-weight: 800;
        }

        .insight-subtitle {
            color: var(--insight-muted);
            font-size: 0.88rem;
        }

        /* =========================================
           7. WORKSPACE CARDS
        ========================================= */

        .insight-card {
            background: var(--insight-surface);
            border: 1px solid var(--insight-border);
            border-radius: 16px;
            padding: 1.25rem;
            margin-bottom: 1rem;
            min-height: 150px;
            box-shadow: 0 3px 12px rgba(36, 59, 83, 0.035);
        }

        .insight-card h3 {
            color: var(--insight-text);
            font-size: 1.08rem;
            margin: 0.5rem 0;
        }

        .insight-card p {
            color: var(--insight-muted);
            font-size: 0.92rem;
            line-height: 1.5;
        }

        .insight-icon {
            font-size: 1.5rem;
        }

        /* =========================================
           8. HERO WORKFLOW PANEL
        ========================================= */

        .insight-hero {
            background: linear-gradient(
                120deg,
                #E7F0FD,
                #E7F7F3
            );
            border: 1px solid #D7E7F5;
            border-radius: 20px;
            padding: 2rem;
            margin: 1rem 0 1.5rem;
        }

        .insight-hero h2 {
            color: var(--insight-text);
            font-size: 1.85rem;
            margin-bottom: 0.5rem;
        }

        .insight-hero p {
            color: #52677D;
            font-size: 1rem;
            line-height: 1.6;
        }

        /* =========================================
           9. CLOSING BANNER
        ========================================= */

        .insight-footer {
            background: var(--insight-surface);
            border: 1px solid var(--insight-border);
            border-radius: 16px;
            padding: 1.5rem;
            margin-top: 2rem;
            text-align: center;
        }

        .insight-footer h3 {
            color: var(--insight-text);
            margin-bottom: 0.5rem;
        }

        .insight-footer p {
            color: var(--insight-muted);
            margin-bottom: 0;
        }

        /* =========================================
           10. BUTTONS
        ========================================= */

        div.stButton > button[kind="primary"] {
            background-color: var(--insight-primary);
            border-color: var(--insight-primary);
            border-radius: 9px;
            color: #FFFFFF;
            font-weight: 600;
        }

        div.stButton > button[kind="primary"]:hover {
            background-color: var(--insight-primary-dark);
            border-color: var(--insight-primary-dark);
            color: #FFFFFF;
        }

        div.stButton > button {
            border-radius: 9px;
            border-color: var(--insight-border);
        }

        /* =========================================
           11. RESPONSIVE LAYOUT
        ========================================= */

        @media (max-width: 768px) {
            .block-container {
                padding-top: 1rem;
            }

            .insight-hero {
                padding: 1.25rem;
            }

            .insight-hero h2 {
                font-size: 1.5rem;
            }

            .insight-card {
                padding: 1rem;
            }

            [data-testid="stMetric"] {
                padding: 0.75rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )