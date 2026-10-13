"""Overview page for the InsightSphere application."""

import streamlit as st


def render_overview() -> None:
    """Render the approved InsightSphere overview page."""

    # Welcome section
    st.markdown(
        """
        <div style="margin-bottom: 1.2rem;">
            <h1 style="
                color: #243B53;
                font-size: 2rem;
                font-weight: 750;
                margin-bottom: 0.35rem;
            ">
                Welcome to InsightSphere
            </h1>
            <p style="
                color: #718096;
                font-size: 1rem;
                margin-top: 0;
            ">
                Your data workspace for exploration, search, AI, and reporting.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Primary workflow panel
    st.markdown(
        """
        <div class="insight-hero">
            <div style="
                color: #3978C5;
                font-size: 0.78rem;
                font-weight: 700;
                letter-spacing: 1px;
                text-transform: uppercase;
                margin-bottom: 0.6rem;
            ">
                GET STARTED
            </div>
            <h2>Start with your data</h2>
            <p>
                Bring your data into one workspace. Validate and prepare it,
                explore the results, and use search or AI to uncover insights.
            </p>
            <div style="
                display: flex;
                flex-wrap: wrap;
                gap: 0.65rem;
                margin-top: 1.2rem;
            ">
                <span style="
                    background: white;
                    border: 1px solid #D7E7F5;
                    border-radius: 8px;
                    padding: 0.55rem 0.85rem;
                    color: #285E9E;
                    font-weight: 600;
                ">01 &nbsp; Upload</span>
                <span style="
                    background: white;
                    border: 1px solid #D7E7F5;
                    border-radius: 8px;
                    padding: 0.55rem 0.85rem;
                    color: #285E9E;
                    font-weight: 600;
                ">02 &nbsp; Validate</span>
                <span style="
                    background: white;
                    border: 1px solid #D7E7F5;
                    border-radius: 8px;
                    padding: 0.55rem 0.85rem;
                    color: #285E9E;
                    font-weight: 600;
                ">03 &nbsp; Explore</span>
                <span style="
                    background: white;
                    border: 1px solid #D7E7F5;
                    border-radius: 8px;
                    padding: 0.55rem 0.85rem;
                    color: #285E9E;
                    font-weight: 600;
                ">04 &nbsp; Ask AI</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Quick-access heading
    st.markdown(
        """
        <div style="margin: 1.5rem 0 1rem;">
            <h2 style="
                color: #243B53;
                font-size: 1.35rem;
                margin-bottom: 0.3rem;
            ">Your workspace</h2>
            <p style="color: #718096; margin-top: 0;">
                Choose how you want to work with your data.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Quick-access cards
    card_columns = st.columns(3)

    cards = [
        {
            "icon": "↥",
            "title": "Upload Data",
            "description": (
                "Load CSV, Excel, JSON, PDF, DOCX, and other supported sources "
                "into the standardized ingestion pipeline."
            ),
            "target": "Upload Data",
        },
        {
            "icon": "▦",
            "title": "Explore Data",
            "description": (
                "Inspect ingested data, review its structure, and prepare "
                "it for analysis and visualization."
            ),
            "target": "Explore Data",
        },
        {
            "icon": "⌕",
            "title": "Search",
            "description": (
                "Find relevant information across indexed documents "
                "using the search capabilities."
            ),
            "target": "Search",
        },
        {
            "icon": "✧",
            "title": "Ask AI",
            "description": (
                "Ask questions about your documents and receive answers "
                "grounded in retrieved context."
            ),
            "target": "Ask AI",
        },
        {
            "icon": "▥",
            "title": "Dashboards",
            "description": (
                "Connect analytical outputs to reporting and business "
                "intelligence dashboards."
            ),
            "target": "Dashboards",
        },
        {
            "icon": "◷",
            "title": "Activity & Status",
            "description": (
                "Review pipeline activity, ingestion outcomes, and "
                "processing status."
            ),
            "target": "Activity & Status",
        },
    ]

    for index, card in enumerate(cards):
        column = card_columns[index % 3]

        with column:
            st.markdown(
                f"""
                <div class="insight-card">
                    <div class="insight-icon">{card["icon"]}</div>
                    <h3>{card["title"]}</h3>
                    <p>{card["description"]}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button(
                f"Open {card['title']} →",
                key=f"overview_{card['target']}",
                use_container_width=True,
            ):
                st.session_state["insightsphere_navigation"] = card["target"]
                st.rerun()

    # Approved closing banner — wording must remain unchanged
    st.markdown(
        """
        <div class="insight-footer">
            <h3>One platform. Multiple ways to work.</h3>
            <p>
                Your data supports exploration, search, AI, and reporting.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )