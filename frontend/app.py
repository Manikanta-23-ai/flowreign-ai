
import json
import os

import requests
import streamlit as st


# --------------------------------------------------
# Configuration
# --------------------------------------------------

DEFAULT_API_URL = os.getenv(
    "FLOWREIGN_API_URL",
    "http://127.0.0.1:8000",
)

st.set_page_config(
    page_title="FlowReign AI | Command Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# Styling
# --------------------------------------------------

st.markdown(
    """
    <style>
    .stApp {
        background: #080D18;
        color: #E8EDF7;
    }

    [data-testid="stSidebar"] {
        background: #101827;
        border-right: 1px solid #26344A;
    }

    [data-testid="stMetric"] {
        background: #111C2D;
        border: 1px solid #26344A;
        padding: 18px;
        border-radius: 12px;
    }

    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
        min-height: 40px;
    }

    .hero {
        padding: 24px;
        background: linear-gradient(120deg, #14243B, #101827);
        border: 1px solid #26344A;
        border-radius: 16px;
        margin-bottom: 22px;
    }

    .muted {
        color: #9AAAC2;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# API helpers
# --------------------------------------------------

def api_request(method, endpoint, **kwargs):
    url = f"{st.session_state.api_url.rstrip('/')}{endpoint}"

    try:
        response = requests.request(
            method,
            url,
            timeout=120,
            **kwargs,
        )

        try:
            data = response.json()
        except ValueError:
            data = {"detail": response.text}

        if not response.ok:
            detail = data.get("detail", "Unknown API error")
            st.error(f"API error ({response.status_code}): {detail}")
            return None

        return data

    except requests.RequestException as error:
        st.error(f"Cannot connect to FlowReign API: {error}")
        return None


def get_workflows():
    result = api_request("GET", "/api/v1/workflows")
    return result if isinstance(result, list) else []


def get_workflow_details(workflow_id):
    return api_request(
        "GET",
        f"/api/v1/workflows/{workflow_id}",
    )


def get_tasks(workflow_id):
    result = api_request(
        "GET",
        f"/api/v1/workflows/{workflow_id}/tasks",
    )

    if isinstance(result, dict):
        return result.get("tasks", [])

    return []


def show_json(value):
    try:
        parsed = json.loads(value) if isinstance(value, str) else value
        st.json(parsed)
    except (ValueError, TypeError):
        st.write(value)


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

if "api_url" not in st.session_state:
    st.session_state.api_url = DEFAULT_API_URL

if "selected_workflow" not in st.session_state:
    st.session_state.selected_workflow = None

with st.sidebar:
    st.title("⚡ FlowReign AI")
    st.caption("Intelligence That Executes.")

    st.divider()

    st.subheader("System connection")

    st.session_state.api_url = st.text_input(
        "Backend API URL",
        value=st.session_state.api_url,
    )

    if st.button("Check API connection", use_container_width=True):
        health = api_request("GET", "/health")

        if health:
            st.success("Backend connected")
            st.json(health)

    st.divider()

    st.caption("PLATFORM")
    st.markdown("**Command Center**")
    st.markdown("Workflow Orchestration")
    st.markdown("AI Specialist Agents")
    st.markdown("Human Approval")
    st.markdown("Execution History")

    st.divider()

    st.caption("OPEN SOURCE PROJECT")
    st.caption("FlowReign AI · MVP")


# --------------------------------------------------
# Header
# --------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <h1>⚡ Command Center</h1>
        <p class="muted">
            Orchestrate business workflows, coordinate AI specialists,
            and monitor execution from one control plane.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

workflows = get_workflows()

total = len(workflows)
completed = sum(
    item.get("status") == "completed"
    for item in workflows
)
running = sum(
    item.get("status") == "running"
    for item in workflows
)
waiting = sum(
    item.get("status") == "waiting_for_approval"
    for item in workflows
)

metric1, metric2, metric3, metric4 = st.columns(4)

metric1.metric("Total workflows", total)
metric2.metric("Completed", completed)
metric3.metric("Running", running)
metric4.metric("Awaiting approval", waiting)

st.divider()


# --------------------------------------------------
# Main tabs
# --------------------------------------------------

create_tab, manage_tab, details_tab = st.tabs(
    [
        "＋ Create workflow",
        "◈ Manage workflows",
        "◎ Workflow details",
    ]
)


# --------------------------------------------------
# Create workflow
# --------------------------------------------------

with create_tab:
    st.subheader("Create a business objective")

    st.write(
        "Describe the outcome you want FlowReign AI to work toward."
    )

    with st.form("create_workflow_form"):
        objective = st.text_area(
            "Business objective",
            placeholder=(
                "Example: Analyze customer feedback, identify "
                "recurring problems, and prepare recommendations."
            ),
            height=150,
            max_chars=2000,
        )

        col1, col2 = st.columns(2)

        with col1:
            priority = st.selectbox(
                "Priority",
                ["low", "medium", "high", "critical"],
                index=1,
            )

        with col2:
            requires_approval = st.checkbox(
                "Require human approval before execution",
                value=True,
            )

        submitted = st.form_submit_button(
            "Create workflow",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if len(objective.strip()) < 5:
            st.warning("Enter an objective with at least 5 characters.")
        else:
            result = api_request(
                "POST",
                "/api/v1/workflows",
                json={
                    "objective": objective.strip(),
                    "priority": priority,
                    "requires_approval": requires_approval,
                },
            )

            if result:
                st.success("Workflow created successfully.")
                st.code(result["id"])
                st.session_state.selected_workflow = result["id"]
                st.info(
                    "Open Workflow details to generate its task plan."
                )
                st.rerun()


# --------------------------------------------------
# Manage workflows
# --------------------------------------------------

with manage_tab:
    st.subheader("Workflow registry")

    if st.button("↻ Refresh workflows"):
        st.rerun()

    if not workflows:
        st.info("No workflows found. Create your first workflow.")
    else:
        for workflow in workflows:
            workflow_id = workflow["id"]
            objective = workflow["objective"]
            current_status = workflow["status"]

            with st.container(border=True):
                left, right = st.columns([4, 1])

                with left:
                    st.markdown(f"**{objective}**")
                    st.caption(
                        f"ID: {workflow_id} | "
                        f"Priority: {workflow['priority']} | "
                        f"Status: {current_status}"
                    )

                with right:
                    if st.button(
                        "Inspect",
                        key=f"inspect_{workflow_id}",
                        use_container_width=True,
                    ):
                        st.session_state.selected_workflow = workflow_id
                        st.rerun()


# --------------------------------------------------
# Workflow details
# --------------------------------------------------

with details_tab:
    st.subheader("Workflow control and inspection")

    workflow_options = {
        f"{item['objective'][:65]} | {item['id'][:8]}": item["id"]
        for item in workflows
    }

    labels = list(workflow_options.keys())

    if labels:
        current_index = 0

        if st.session_state.selected_workflow:
            selected_id = st.session_state.selected_workflow

            for index, label in enumerate(labels):
                if workflow_options[label] == selected_id:
                    current_index = index
                    break

        selected_label = st.selectbox(
            "Select workflow",
            labels,
            index=current_index,
        )

        workflow_id = workflow_options[selected_label]
        st.session_state.selected_workflow = workflow_id

        workflow = get_workflow_details(workflow_id)

        if workflow:
            st.markdown(f"### {workflow['objective']}")

            c1, c2, c3 = st.columns(3)

            c1.metric("Status", workflow["status"])
            c2.metric("Priority", workflow["priority"])
            c3.metric(
                "Human approval",
                "Required" if workflow["requires_approval"] else "Not required",
            )

            st.caption(f"Workflow ID: {workflow_id}")

            st.divider()

            tasks = get_tasks(workflow_id)

            st.markdown("#### Task planning")

            if not tasks:
                st.info("No task plan generated yet.")

            else:
                for index, task in enumerate(tasks, start=1):
                    status_value = task["status"]

                    with st.container(border=True):
                        st.markdown(
                            f"**{index}. {task['title']}**"
                        )

                        st.caption(
                            f"Agent: {task['assigned_agent']} | "
                            f"Status: {status_value}"
                        )

                        st.write(task["description"])

                        if task.get("depends_on"):
                            st.caption(
                                "Dependencies: "
                                + ", ".join(task["depends_on"])
                            )

                        if task.get("output"):
                            with st.expander("View agent output"):
                                st.write(task["output"])

            st.divider()

            st.markdown("#### Workflow actions")

            status_value = workflow["status"]

            action1, action2, action3 = st.columns(3)

            with action1:
                if st.button(
                    "Generate plan",
                    use_container_width=True,
                    disabled=status_value in (
                        "running",
                        "completed",
                        "cancelled",
                    ),
                ):
                    result = api_request(
                        "POST",
                        f"/api/v1/workflows/{workflow_id}/plan",
                    )

                    if result:
                        st.success("Plan generated and persisted.")
                        st.rerun()

            with action2:
                if status_value == "waiting_for_approval":
                    if st.button(
                        "Approve plan",
                        type="primary",
                        use_container_width=True,
                    ):
                        result = api_request(
                            "POST",
                            f"/api/v1/workflows/{workflow_id}/approve",
                            json={
                                "approved": True,
                                "note": "Approved from FlowReign Command Center",
                            },
                        )

                        if result:
                            st.success("Workflow approved.")
                            st.rerun()

                elif status_value == "pending" and workflow["requires_approval"]:
                    st.info("Plan approved.")

            with action3:
                can_execute = (
                    status_value == "pending"
                    and bool(tasks)
                )

                if st.button(
                    "▶ Execute workflow",
                    type="primary",
                    use_container_width=True,
                    disabled=not can_execute,
                ):
                    with st.spinner(
                        "AI specialist agents are processing tasks..."
                    ):
                        result = api_request(
                            "POST",
                            f"/api/v1/workflows/{workflow_id}/execute",
                        )

                    if result:
                        st.success("Workflow execution completed.")
                        st.rerun()

            if workflow.get("result"):
                st.divider()
                st.markdown("#### Workflow report")

                with st.expander(
                    "View complete workflow result",
                    expanded=status_value == "completed",
                ):
                    show_json(workflow["result"])

    else:
        st.info("Create a workflow to start using the Command Center.")


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()

st.caption(
    "FlowReign AI | Intelligence That Executes. "
    "AI outputs require review. No external business actions "
    "are performed by this MVP."
)
