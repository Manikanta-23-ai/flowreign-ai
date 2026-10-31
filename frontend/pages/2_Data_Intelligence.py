
import os

import pandas as pd
import requests
import streamlit as st


st.set_page_config(
    page_title="FlowReign AI | Data Intelligence",
    page_icon="📊",
    layout="wide",
)

API_URL = os.getenv(
    "FLOWREIGN_API_URL",
    "http://127.0.0.1:8000",
)

st.title("📊 Data Intelligence")
st.caption(
    "Upload a CSV dataset and generate statistical insights."
)

uploaded_file = st.file_uploader(
    "Upload CSV file",
    type=["csv"],
)

if uploaded_file is not None:
    st.write(f"Selected file: **{uploaded_file.name}**")

    if st.button("Analyze dataset", type="primary"):
        try:
            csv_content = uploaded_file.getvalue().decode("utf-8-sig")

            with st.spinner("Analyzing dataset..."):
                response = requests.post(
                    f"{API_URL}/api/v1/data/analyze",
                    json={
                        "filename": uploaded_file.name,
                        "csv_content": csv_content,
                    },
                    timeout=120,
                )

            if not response.ok:
                st.error(
                    f"Analysis failed ({response.status_code}): "
                    f"{response.text}"
                )
                st.stop()

            st.session_state.data_analysis = response.json()

        except UnicodeDecodeError:
            st.error(
                "This CSV is not UTF-8 encoded. "
                "Save it as CSV UTF-8 and upload again."
            )
        except requests.RequestException as error:
            st.error(f"Backend connection failed: {error}")


result = st.session_state.get("data_analysis")

if result:
    st.divider()
    st.subheader("Dataset overview")

    dataset = result["dataset"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", dataset["rows"])
    c2.metric("Columns", dataset["columns"])
    c3.metric("Numeric columns", len(dataset["numeric_columns"]))
    c4.metric("Duplicate rows", dataset["duplicate_rows"])

    st.divider()

    st.subheader("Dataset preview")
    st.dataframe(
        pd.DataFrame(result["preview"]),
        use_container_width=True,
    )

    st.subheader("Column information")
    st.json(result["column_types"])

    st.subheader("Missing values")
    missing_df = pd.DataFrame(
        list(result["missing_values"].items()),
        columns=["Column", "Missing values"],
    )
    st.dataframe(missing_df, use_container_width=True)

    st.subheader("Numeric statistics")

    if result["numeric_summary"]:
        st.dataframe(
            pd.DataFrame(result["numeric_summary"]),
            use_container_width=True,
        )
    else:
        st.info("No numeric columns found.")

    st.subheader("Data visualizations")

    chart_columns = result["chart_columns"]

    if chart_columns and result["chart_data"]:
        chart_df = pd.DataFrame(result["chart_data"])
        st.line_chart(chart_df[chart_columns])
        st.bar_chart(chart_df[chart_columns])
    else:
        st.info("No numeric data available for charts.")

    st.subheader("Categorical distributions")

    for column, values in result["categorical_summary"].items():
        with st.expander(f"Top values: {column}"):
            st.json(values)

    if result["correlation"]:
        st.subheader("Correlation matrix")
        correlation_df = pd.DataFrame(result["correlation"])
        st.dataframe(correlation_df, use_container_width=True)

    st.divider()

    st.subheader("Export analysis")

    report_json = pd.io.json.dumps(result, indent=2)

    st.download_button(
        "Download analysis JSON",
        data=report_json,
        file_name="flowreign_data_analysis.json",
        mime="application/json",
    )

    st.caption(
        "Statistical analysis is based on the uploaded dataset. "
        "Correlation does not imply causation."
    )
