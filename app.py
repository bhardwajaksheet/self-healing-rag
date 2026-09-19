import html
import re
import textwrap

import streamlit as st

from graph.workflow import build_graph


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Self-Healing RAG",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SAFE HTML RENDERER
# ============================================================

def ui(markup):
    """
    Render custom HTML directly using Streamlit's HTML renderer.
    """
    st.html(
        textwrap.dedent(markup).strip()
    )


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

/* ==========================================================
   GLOBAL
   ========================================================== */

.stApp {
    background:
        radial-gradient(
            circle at 8% 0%,
            rgba(99, 102, 241, 0.12),
            transparent 27%
        ),
        radial-gradient(
            circle at 95% 8%,
            rgba(14, 165, 233, 0.08),
            transparent 24%
        ),
        #070a11;
}

.block-container {
    max-width: 1400px;
    padding-top: 1.8rem;
    padding-bottom: 4rem;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    background: transparent !important;
}


/* ==========================================================
   SIDEBAR
   ========================================================== */

[data-testid="stSidebar"] {
    background: #090d15;
    border-right: 1px solid rgba(255,255,255,0.06);
}

.sidebar-brand {
    font-size: 23px;
    font-weight: 800;
    color: #f8fafc;
}

.sidebar-description {
    color: #7f8a9d;
    font-size: 13px;
    line-height: 1.6;
    margin-top: 7px;
}

.sidebar-section {
    color: #a5b4fc;
    font-size: 12px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 25px;
    margin-bottom: 13px;
}

.pipeline-item {
    display: flex;
    gap: 12px;
    margin-bottom: 18px;
}

.pipeline-number {
    width: 27px;
    height: 27px;
    min-width: 27px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(99,102,241,0.14);
    border: 1px solid rgba(129,140,248,0.25);
    color: #a5b4fc;
    font-size: 11px;
    font-weight: 800;
}

.pipeline-title {
    color: #e5e7eb;
    font-weight: 700;
    font-size: 14px;
}

.pipeline-description {
    color: #687386;
    font-size: 11px;
    margin-top: 3px;
    line-height: 1.4;
}

.stack-tag {
    display: inline-block;
    padding: 5px 9px;
    margin: 3px 3px 3px 0;
    border-radius: 7px;
    background: #101623;
    border: 1px solid rgba(255,255,255,0.06);
    color: #8994a7;
    font-size: 10px;
}


/* ==========================================================
   HERO
   ========================================================== */

.hero-title {
    font-size: 48px;
    font-weight: 850;
    letter-spacing: -2px;
    line-height: 1.05;

    background: linear-gradient(
        90deg,
        #f8fafc 0%,
        #a5b4fc 48%,
        #67e8f9 100%
    );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    color: #7d889b;
    font-size: 16px;
    margin-top: 9px;
}

.online-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;

    padding: 8px 14px;
    border-radius: 999px;

    background: rgba(34,197,94,0.07);
    border: 1px solid rgba(74,222,128,0.22);

    color: #86efac;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.4px;
}

.online-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #4ade80;
    box-shadow: 0 0 11px rgba(74,222,128,0.85);
}


/* ==========================================================
   INPUT
   ========================================================== */

.input-label {
    color: #9da8ba;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1px;
    margin-top: 30px;
    margin-bottom: 8px;
}

div[data-testid="stTextArea"] textarea {
    background: #0c111b !important;
    border: 1px solid #252e40 !important;
    border-radius: 15px !important;

    color: #f8fafc !important;

    font-size: 16px !important;
    line-height: 1.5 !important;

    padding: 16px !important;
}

div[data-testid="stTextArea"] textarea:focus {
    border-color: #6366f1 !important;

    box-shadow:
        0 0 0 1px rgba(99,102,241,0.35),
        0 0 25px rgba(99,102,241,0.08) !important;
}


/* ==========================================================
   BUTTON
   ========================================================== */

div.stButton > button {
    min-height: 50px;

    border-radius: 13px;

    border: 1px solid rgba(129,140,248,0.35);

    background:
        linear-gradient(
            135deg,
            #4f46e5,
            #6366f1
        );

    color: white;

    font-weight: 750;

    transition:
        transform 0.15s ease,
        box-shadow 0.15s ease;
}

div.stButton > button:hover {
    transform: translateY(-1px);

    box-shadow:
        0 8px 30px rgba(79,70,229,0.25);
}


/* ==========================================================
   SECTION HEADERS
   ========================================================== */

.section {
    margin-top: 34px;
    margin-bottom: 13px;
}

.section-title {
    font-size: 21px;
    font-weight: 800;
    color: #f1f5f9;
}

.section-description {
    color: #697488;
    font-size: 12px;
    margin-top: 4px;
}


/* ==========================================================
   METRICS
   ========================================================== */

.metric-card {
    background:
        linear-gradient(
            145deg,
            rgba(16,23,36,0.96),
            rgba(10,15,25,0.96)
        );

    border: 1px solid rgba(255,255,255,0.065);
    border-radius: 15px;

    padding: 18px;

    min-height: 108px;
}

.metric-label {
    color: #687489;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.metric-value {
    color: #f8fafc;
    font-size: 25px;
    font-weight: 800;
    margin-top: 10px;
}

.metric-caption {
    color: #596477;
    font-size: 10px;
    margin-top: 3px;
}


/* ==========================================================
   ANSWER
   ========================================================== */

.answer-card {
    background:
        linear-gradient(
            145deg,
            rgba(27,39,62,0.95),
            rgba(13,20,34,0.98)
        );

    border: 1px solid rgba(99,102,241,0.35);
    border-radius: 18px;

    padding: 24px;

    box-shadow:
        0 18px 55px rgba(0,0,0,0.16);
}

.answer-label {
    color: #818cf8;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 13px;
}

.answer-text {
    color: #f8fafc;
    font-size: 18px;
    line-height: 1.7;
}

.answer-text strong {
    color: #a5b4fc;
    font-weight: 800;
}

.answer-text code {
    background: rgba(129,140,248,0.12);
    color: #c7d2fe;
    padding: 2px 6px;
    border-radius: 5px;
}


/* ==========================================================
   STATUS CARDS
   ========================================================== */

.pass-card {
    background: rgba(22,101,52,0.12);
    border: 1px solid rgba(74,222,128,0.22);
    border-radius: 14px;
    padding: 16px 18px;
}

.fail-card {
    background: rgba(127,29,29,0.12);
    border: 1px solid rgba(248,113,113,0.22);
    border-radius: 14px;
    padding: 16px 18px;
}

.heal-card {
    background: rgba(120,53,15,0.12);
    border: 1px solid rgba(251,191,36,0.22);
    border-radius: 14px;
    padding: 16px 18px;
}

.status-title {
    color: #f8fafc;
    font-size: 14px;
    font-weight: 750;
}

.status-description {
    color: #7f8a9c;
    font-size: 12px;
    line-height: 1.55;
    margin-top: 5px;
}


/* ==========================================================
   EXECUTION TRACE
   ========================================================== */

.trace-wrapper {
    position: relative;
    padding-left: 7px;
}

.trace-item {
    position: relative;

    background: #0c111b;

    border: 1px solid rgba(255,255,255,0.065);
    border-radius: 14px;

    padding: 17px 18px;

    margin-bottom: 10px;
}

.trace-index {
    color: #818cf8;
    font-size: 10px;
    font-weight: 850;
    letter-spacing: 1px;
}

.trace-title {
    color: #f8fafc;
    font-size: 14px;
    font-weight: 750;
    margin-top: 4px;
}

.trace-info {
    color: #778296;
    font-size: 12px;
    margin-top: 6px;
    line-height: 1.55;
}

.trace-pass {
    border-left: 3px solid #4ade80;
}

.trace-fail {
    border-left: 3px solid #f87171;
}

.trace-heal {
    border-left: 3px solid #fbbf24;
}

.trace-neutral {
    border-left: 3px solid #818cf8;
}

.trace-arrow {
    text-align: center;
    color: #3f4a5d;
    font-size: 16px;
    margin: -3px 0 5px 0;
}


/* ==========================================================
   EVIDENCE
   ========================================================== */

.evidence-card {
    background: #0c111b;
    border: 1px solid rgba(255,255,255,0.065);
    border-radius: 14px;
    padding: 17px;
    height: 100%;
}

.evidence-title {
    color: #e5e7eb;
    font-size: 13px;
    font-weight: 750;
}

.evidence-distance {
    color: #818cf8;
    font-size: 11px;
    font-weight: 750;
}

.evidence-content {
    color: #7b8799;
    font-size: 12px;
    line-height: 1.6;
    margin-top: 11px;
}


/* ==========================================================
   FOOTER
   ========================================================== */

.footer {
    margin-top: 60px;
    padding-top: 20px;

    border-top: 1px solid rgba(255,255,255,0.045);

    text-align: center;

    color: #3f495a;
    font-size: 10px;
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================

def escape_text(value):
    return html.escape(str(value))


def verdict_pass(critique):
    return "VERDICT: PASS" in str(critique).upper()


def format_answer_markdown(answer):
    """
    Render common Markdown emphasis safely inside the
    custom answer card.
    """

    text = escape_text(answer)

    # Bold
    text = re.sub(
        r"\*\*(.+?)\*\*",
        r"<strong>\1</strong>",
        text
    )

    # Inline code
    text = re.sub(
        r"`(.+?)`",
        r"<code>\1</code>",
        text
    )

    # Line breaks
    text = text.replace("\n", "<br>")

    return text


def make_trace(trace_events):
    """
    Convert LangGraph streamed node updates into a
    human-readable execution trace.
    """

    trace = []

    for event in trace_events:

        if not isinstance(event, dict):
            continue

        for node_name, update in event.items():

            if not isinstance(update, dict):
                continue

            if node_name == "retrieve":

                scores = update.get(
                    "retrieval_scores",
                    []
                )

                best = min(scores) if scores else None

                description = (
                    f"Retrieved {len(scores)} evidence chunks"
                )

                if best is not None:
                    description += (
                        f" • Best distance: {best:.4f}"
                    )

                trace.append(
                    {
                        "type": "retrieve",
                        "title": "RETRIEVE",
                        "description": description,
                        "class": "trace-neutral",
                    }
                )

            elif node_name == "generate":

                trace.append(
                    {
                        "type": "generate",
                        "title": "GENERATE",
                        "description": (
                            "Generated an answer using "
                            "the retrieved context."
                        ),
                        "class": "trace-neutral",
                    }
                )

            elif node_name == "critic":

                critique = update.get(
                    "critique",
                    ""
                )

                passed = verdict_pass(
                    critique
                )

                reason = str(critique)

                if "REASON:" in reason:

                    reason = reason.split(
                        "REASON:",
                        1
                    )[1].strip()

                trace.append(
                    {
                        "type": "critic",
                        "title": (
                            "CRITIC  ✓ PASS"
                            if passed
                            else
                            "CRITIC  ✕ FAIL"
                        ),
                        "description": reason,
                        "class": (
                            "trace-pass"
                            if passed
                            else
                            "trace-fail"
                        ),
                    }
                )

            elif node_name == "reformulate":

                new_question = update.get(
                    "question",
                    ""
                )

                trace.append(
                    {
                        "type": "heal",
                        "title": (
                            "SELF-HEAL  ↻ REFORMULATE"
                        ),
                        "description": (
                            f"New retrieval query: "
                            f"{new_question}"
                        ),
                        "class": "trace-heal",
                    }
                )

    return trace


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    ui(
        """
        <div class="sidebar-brand">
            🧠 Self-Healing RAG
        </div>

        <div class="sidebar-description">
            A retrieval system that verifies its own evidence
            and automatically recovers from weak retrieval.
        </div>
        """
    )

    st.markdown("---")

    ui(
        """
        <div class="sidebar-section">
            Pipeline
        </div>
        """
    )

    pipeline = [
        (
            "01",
            "Retrieve",
            "Find relevant document chunks."
        ),
        (
            "02",
            "Generate",
            "Generate a grounded answer."
        ),
        (
            "03",
            "Critic",
            "Verify answer and evidence."
        ),
        (
            "04",
            "Heal",
            "Reformulate and retry when rejected."
        ),
    ]

    for number, title, description in pipeline:

        ui(
            f"""
            <div class="pipeline-item">

                <div class="pipeline-number">
                    {number}
                </div>

                <div>
                    <div class="pipeline-title">
                        {title}
                    </div>

                    <div class="pipeline-description">
                        {description}
                    </div>
                </div>

            </div>
            """
        )

    ui(
        """
        <div class="sidebar-section">
            Technology
        </div>
        """
    )

    for technology in [
        "Python",
        "LangGraph",
        "LangChain",
        "ChromaDB",
        "Gemini Embeddings",
        "Groq",
        "Streamlit",
    ]:

        ui(
            f"""
            <span class="stack-tag">
                {technology}
            </span>
            """
        )

    st.markdown("---")

    st.caption(
        "Grounded generation • No intentional hallucination"
    )


# ============================================================
# HERO
# ============================================================

hero_left, hero_right = st.columns(
    [4, 1]
)

with hero_left:

    ui(
        """
        <div class="hero-title">
            Self-Healing RAG
        </div>

        <div class="hero-subtitle">
            Retrieval&nbsp;&nbsp;•&nbsp;&nbsp;
            Verification&nbsp;&nbsp;•&nbsp;&nbsp;
            Recovery
        </div>
        """
    )

with hero_right:

    ui(
        """
        <div style="text-align:right; padding-top:8px;">

            <div class="online-pill">

                <span class="online-dot"></span>

                SYSTEM ONLINE

            </div>

        </div>
        """
    )


# ============================================================
# QUESTION INPUT
# ============================================================

ui(
    """
    <div class="input-label">
        ASK YOUR KNOWLEDGE BASE
    </div>
    """
)

question = st.text_area(
    "Question",
    placeholder=(
        "Example: What is the minimum attendance required "
        "for the semester examination?"
    ),
    height=105,
    label_visibility="collapsed",
)

run = st.button(
    "✦  Run Analysis",
    type="primary",
    use_container_width=True,
)


# ============================================================
# RUN GRAPH
# ============================================================

if run:

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

        st.stop()

    initial_state = {
        "question": question,
        "context": "",
        "answer": "",
        "critique": "",
        "attempts": 0,
        "retrieval_scores": [],
    }

    trace_events = []

    final_state = None

    with st.status(
        "Running Self-Healing RAG...",
        expanded=False
    ) as status:

        try:

            graph = build_graph()

            for state_update in graph.stream(
                initial_state,
                stream_mode="updates"
            ):

                trace_events.append(
                    state_update
                )

            # Reconstruct the final state from
            # the streamed node updates.

            final_state = dict(
                initial_state
            )

            for event in trace_events:

                if not isinstance(event, dict):
                    continue

                for node_name, update in event.items():

                    if isinstance(update, dict):

                        final_state.update(
                            update
                        )

            status.update(
                label="Analysis complete",
                state="complete",
                expanded=False
            )

        except Exception as error:

            status.update(
                label="Pipeline error",
                state="error",
                expanded=True
            )

            st.error(
                "The RAG pipeline encountered an error."
            )

            with st.expander(
                "Technical details"
            ):

                st.exception(error)

            st.stop()


    # ========================================================
    # RESULT DATA
    # ========================================================

    answer = final_state.get(
        "answer",
        ""
    )

    critique = final_state.get(
        "critique",
        ""
    )

    attempts = final_state.get(
        "attempts",
        0
    )

    scores = final_state.get(
        "retrieval_scores",
        []
    )

    context = final_state.get(
        "context",
        ""
    )

    current_question = final_state.get(
        "question",
        question
    )

    passed = verdict_pass(
        critique
    )

    best_distance = (
        min(scores)
        if scores
        else None
    )

    trace = make_trace(
        trace_events
    )


    # ========================================================
    # EXECUTION OVERVIEW
    # ========================================================

    ui(
        """
        <div class="section">

            <div class="section-title">
                Execution Overview
            </div>

            <div class="section-description">
                Runtime state of the retrieval and verification pipeline.
            </div>

        </div>
        """
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        value = (
            f"{best_distance:.4f}"
            if best_distance is not None
            else "—"
        )

        ui(
            f"""
            <div class="metric-card">

                <div class="metric-label">
                    Best Distance
                </div>

                <div class="metric-value">
                    {value}
                </div>

                <div class="metric-caption">
                    Lower = closer match
                </div>

            </div>
            """
        )

    with c2:

        ui(
            f"""
            <div class="metric-card">

                <div class="metric-label">
                    Healing Attempts
                </div>

                <div class="metric-value">
                    {attempts}
                </div>

                <div class="metric-caption">
                    Automatic retries
                </div>

            </div>
            """
        )

    with c3:

        critic_status = (
            "PASS"
            if passed
            else
            "FAIL"
        )

        ui(
            f"""
            <div class="metric-card">

                <div class="metric-label">
                    Critic
                </div>

                <div class="metric-value">
                    {critic_status}
                </div>

                <div class="metric-caption">
                    Evidence verification
                </div>

            </div>
            """
        )

    with c4:

        grounding = (
            "Grounded"
            if passed
            else
            "Unresolved"
        )

        ui(
            f"""
            <div class="metric-card">

                <div class="metric-label">
                    Grounding
                </div>

                <div class="metric-value">
                    {grounding}
                </div>

                <div class="metric-caption">
                    Final system state
                </div>

            </div>
            """
        )


    # ========================================================
    # FINAL ANSWER
    # ========================================================

    ui(
        """
        <div class="section">

            <div class="section-title">
                🎯 Final Answer
            </div>

            <div class="section-description">
                Generated from retrieved document evidence.
            </div>

        </div>
        """
    )

    if passed:

        formatted_answer = format_answer_markdown(
            answer
        )

        ui(
            f"""
            <div class="answer-card">

                <div class="answer-label">
                    Grounded response
                </div>

                <div class="answer-text">
                    {formatted_answer}
                </div>

            </div>
            """
        )

    else:

        ui(
            """
            <div class="fail-card">

                <div class="status-title">
                    ⚠ No reliable answer produced
                </div>

                <div class="status-description">
                    The system could not establish sufficient grounded
                    evidence after the available healing attempts.
                    It intentionally avoided hallucinating an answer.
                </div>

            </div>
            """
        )


    # ========================================================
    # EXECUTION TRACE
    # ========================================================

    ui(
        """
        <div class="section">

            <div class="section-title">
                🧠 Execution Trace
            </div>

            <div class="section-description">
                Actual LangGraph node execution for this request.
            </div>

        </div>
        """
    )

    if trace:

        ui(
            """
            <div class="trace-wrapper">
            """
        )

        for index, event in enumerate(trace):

            trace_class = event["class"]

            ui(
                f"""
                <div class="trace-item {trace_class}">

                    <div class="trace-index">
                        STEP {index + 1:02d}
                    </div>

                    <div class="trace-title">
                        {escape_text(event["title"])}
                    </div>

                    <div class="trace-info">
                        {escape_text(event["description"])}
                    </div>

                </div>
                """
            )

            if index < len(trace) - 1:

                ui(
                    """
                    <div class="trace-arrow">
                        ↓
                    </div>
                    """
                )

        ui(
            """
            </div>
            """
        )

    else:

        st.caption(
            "No execution trace was returned."
        )


    # ========================================================
    # SELF-HEALING SUMMARY
    # ========================================================

    if attempts > 0:

        ui(
            """
            <div class="section">

                <div class="section-title">
                    🔄 Recovery Summary
                </div>

            </div>
            """
        )

        ui(
            f"""
            <div class="heal-card">

                <div class="status-title">
                    Self-healing activated
                </div>

                <div class="status-description">
                    The system rejected an earlier result and
                    automatically reformulated the retrieval query.
                    Total healing attempts:
                    <b>{attempts}</b>.
                </div>

            </div>
            """
        )

        st.markdown(
            "**Final retrieval query**"
        )

        st.code(
            current_question,
            language="text"
        )

    else:

        ui(
            """
            <div class="pass-card">

                <div class="status-title">
                    ✓ Initial retrieval was sufficient
                </div>

                <div class="status-description">
                    The critic accepted the first generated result,
                    so no healing cycle was required.
                </div>

            </div>
            """
        )


    # ========================================================
    # CRITIC VERIFICATION
    # ========================================================

    ui(
        """
        <div class="section">

            <div class="section-title">
                🧐 Critic Verification
            </div>

        </div>
        """
    )

    if passed:

        ui(
            """
            <div class="pass-card">

                <div class="status-title">
                    ✓ Evidence verified
                </div>

                <div class="status-description">
                    The critic accepted the generated answer
                    as sufficiently supported by the retrieved context.
                </div>

            </div>
            """
        )

    else:

        ui(
            """
            <div class="fail-card">

                <div class="status-title">
                    ✕ Evidence rejected
                </div>

                <div class="status-description">
                    The critic determined that the result was not
                    sufficiently grounded in the retrieved evidence.
                </div>

            </div>
            """
        )

    with st.expander(
        "View critic reasoning"
    ):

        st.code(
            critique,
            language="text"
        )


    # ========================================================
    # RETRIEVAL ANALYSIS
    # ========================================================

    ui(
        """
        <div class="section">

            <div class="section-title">
                🔎 Retrieval Analysis
            </div>

            <div class="section-description">
                ChromaDB embedding distances for the final retrieval.
            </div>

        </div>
        """
    )

    if scores:

        score_columns = st.columns(
            len(scores)
        )

        for index, score in enumerate(scores):

            with score_columns[index]:

                ui(
                    f"""
                    <div class="metric-card">

                        <div class="metric-label">
                            Chunk {index + 1}
                        </div>

                        <div class="metric-value">
                            {score:.4f}
                        </div>

                        <div class="metric-caption">
                            Chroma distance
                        </div>

                    </div>
                    """
                )

    else:

        st.caption(
            "No retrieval scores available."
        )


    # ========================================================
    # RETRIEVED EVIDENCE
    # ========================================================

    ui(
        """
        <div class="section">

            <div class="section-title">
                📚 Retrieved Evidence
            </div>

            <div class="section-description">
                Context supplied to the generation and critic stages.
            </div>

        </div>
        """
    )

    with st.expander(
        "Inspect retrieved context"
    ):

        if context:

            st.markdown(
                context
            )

        else:

            st.caption(
                "No retrieved context available."
            )


    # ========================================================
    # DEVELOPER DIAGNOSTICS
    # ========================================================

    with st.expander(
        "🔧 Developer Diagnostics"
    ):

        st.json(
            {
                "original_question": question,
                "final_question": current_question,
                "healing_attempts": attempts,
                "retrieval_scores": scores,
                "critic": critique,
                "trace_steps": len(trace),
            }
        )


# ============================================================
# FOOTER
# ============================================================

ui(
    """
    <div class="footer">
        Self-Healing RAG
        &nbsp;•&nbsp;
        Retrieval Verification
        &nbsp;•&nbsp;
        Query Reformulation
        &nbsp;•&nbsp;
        Grounded Generation
    </div>
    """
)