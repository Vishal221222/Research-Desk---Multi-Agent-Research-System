import traceback

import streamlit as st

from pipeline import run_research_pipeline


st.set_page_config(
    page_title="Research Desk",
    page_icon="📝",
    layout="centered",
)

st.markdown("""
<style>

/* Main Page */
.stApp {
    background-color: #f5f6f8;
    color: #252d35;
    font-family: "Segoe UI", Arial, sans-serif;
}

/* Main Content Width */
.block-container {
    max-width: 900px;
    padding-top: 65px;
    padding-bottom: 50px;
}

/* Main Heading */
h1 {
    font-size: 40px !important;
    font-weight: 700 !important;
    color: #253242 !important;
    letter-spacing: -1px;
    margin-bottom: 12px !important;
}

/* Subheading */
.page-subtitle {
    font-size: 16px;
    color: #737b85;
    margin-top: -5px;
    margin-bottom: 30px;
}

/* Research Form */
[data-testid="stForm"] {
    background: #ffffff !important;
    border: 1px solid #e0e4e8 !important;
    border-radius: 12px !important;
    padding: 25px !important;
    box-shadow: 0 4px 18px rgba(0,0,0,0.035);
}

/* Labels */
[data-testid="stWidgetLabel"] p {
    color: #344054 !important;
    font-size: 14px !important;
    font-weight: 600 !important;
}

/* Research Input */
[data-testid="stTextArea"] textarea {
    background: #fafbfc !important;
    color: #283443 !important;
    border-radius: 8px !important;
    font-size: 15px !important;
    padding: 14px !important;
    line-height: 1.7;
}

/* Input Border */
[data-testid="stTextArea"]
[data-baseweb="textarea"] {
    border: 1px solid #d8dee5 !important;
    border-radius: 8px !important;
    background: #fafbfc !important;
}

/* Input Focus */
[data-testid="stTextArea"]
[data-baseweb="textarea"]:focus-within {
    border-color: #62758a !important;
    box-shadow: 0 0 0 1px #62758a !important;
}

/* Run Research Button */
[data-testid="stFormSubmitButton"] button {
    background: #33465d !important;
    color: white !important;
    border: 1px solid #33465d !important;
    border-radius: 7px !important;
    padding: 10px 22px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    min-height: 43px;
    box-shadow: none !important;
}

/* Button Hover */
[data-testid="stFormSubmitButton"] button:hover {
    background: #26384d !important;
    border-color: #26384d !important;
    color: white !important;
}

/* Button Focus */
[data-testid="stFormSubmitButton"] button:focus {
    color: white !important;
    border-color: #33465d !important;
}

/* Results Heading */
h2, h3 {
    color: #293746 !important;
    font-weight: 600 !important;
}

/* Dividers */
hr {
    border-color: #e3e6ea !important;
}

/* Expandable Sections */
[data-testid="stExpander"] {
    background: #ffffff;
    border: 1px solid #e1e5e9 !important;
    border-radius: 9px !important;
}

/* Download Button */
[data-testid="stDownloadButton"] button {
    background: #ffffff !important;
    color: #33465d !important;
    border: 1px solid #cbd3dc !important;
    border-radius: 7px !important;
    font-weight: 600 !important;
}

[data-testid="stDownloadButton"] button:hover {
    background: #eef1f4 !important;
    border-color: #aebac6 !important;
    color: #26384d !important;
}

/* Captions */
[data-testid="stCaptionContainer"] {
    color: #85909c !important;
    font-size: 13px !important;
}

/* Mobile */
@media (max-width: 700px) {
    .block-container {
        padding: 25px 15px;
    }

    h1 {
        font-size: 30px !important;
    }

    [data-testid="stForm"] {
        padding: 18px !important;
    }
}

</style>
""", unsafe_allow_html=True)



def to_text(value) -> str:
    """Handle strings and common LangChain message/content return shapes."""
    if value is None:
        return ""
    if hasattr(value, "content"):
        return to_text(value.content)
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts = []
        for item in value:
            if isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
            else:
                parts.append(to_text(item))
        return "\n".join(part for part in parts if part)
    if isinstance(value, dict):
        for key in ("output", "text", "content", "report"):
            if key in value:
                return to_text(value[key])
    return str(value)


st.title("Research Desk")
st.markdown(
    '<p class="page-subtitle">Enter a topic to prepare a research report.</p>',
    unsafe_allow_html=True,
)

with st.form("research_form"):
    topic = st.text_area(
        "Research topic",
        placeholder="e.g. The impact of renewable energy on India's power sector",
        height=110,
    )
    submitted = st.form_submit_button("Run research", type="primary")

if submitted:
    topic = topic.strip()
    if not topic:
        st.warning("Please enter a research topic.")
    else:
        # Clear previous output before starting a new request.
        st.session_state.pop("result", None)
        st.session_state.pop("last_topic", None)
        with st.spinner("Research in progress. This may take a few minutes..."):
            try:
                result = run_research_pipeline(topic)
                if not isinstance(result, dict):
                    raise TypeError("The pipeline did not return a results dictionary.")
                st.session_state["result"] = result
                st.session_state["last_topic"] = topic
            except Exception:
                # Keep environment variables and API/provider errors out of the webpage.
                traceback.print_exc()
                st.error("Research could not finish. Something Went Wrong.")

if "result" in st.session_state:
    result = st.session_state["result"]
    report = to_text(result.get("report"))
    feedback = to_text(result.get("feedback"))
    search_results = to_text(result.get("search_results"))
    scraped_content = to_text(result.get("scraped_content"))

    st.divider()
    st.success("Research completed")
    st.caption(f'Topic: {st.session_state["last_topic"]}')

    st.subheader("Research report")
    if report:
        st.markdown(report)
    else:
        st.info("The writer did not return a report.")

    st.subheader("Review feedback")
    if feedback:
        st.markdown(feedback)
    else:
        st.info("The critic did not return feedback.")

    with st.expander("Search results"):
        st.text(search_results or "No search results returned.")

    with st.expander("Source content"):
        st.text(scraped_content or "No source content returned.")

    download_content = (
        f'# Research report: {st.session_state["last_topic"]}\n\n'
        f'{report}\n\n'
        f'## Review feedback\n\n{feedback}\n'
    )
    st.download_button(
        "Download report (.md)",
        data=download_content,
        file_name="research_report.md",
        mime="text/markdown",
    )

st.caption("Search · Read · Write · Review")
