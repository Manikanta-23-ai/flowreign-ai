
import json
from io import StringIO

import pandas as pd


MAX_ROWS = 100_000
MAX_COLUMNS = 100


class DataAnalysisError(Exception):
    pass


def analyze_csv(filename: str, csv_content: str) -> dict:
    if len(csv_content.encode("utf-8")) > 5_000_000:
        raise DataAnalysisError("CSV exceeds the 5 MB upload limit.")

    try:
        dataframe = pd.read_csv(StringIO(csv_content))
    except Exception as error:
        raise DataAnalysisError(
            f"Could not read CSV: {error}"
        ) from error

    if dataframe.empty:
        raise DataAnalysisError("The CSV contains no data rows.")

    if len(dataframe) > MAX_ROWS:
        raise DataAnalysisError(
            f"Dataset exceeds the {MAX_ROWS:,} row limit."
        )

    if len(dataframe.columns) > MAX_COLUMNS:
        raise DataAnalysisError(
            f"Dataset exceeds the {MAX_COLUMNS} column limit."
        )

    dataframe.columns = [
        str(column).strip() for column in dataframe.columns
    ]

    numeric_columns = dataframe.select_dtypes(
        include="number"
    ).columns.tolist()

    categorical_columns = [
        column
        for column in dataframe.columns
        if column not in numeric_columns
    ]

    missing = {
        str(column): int(count)
        for column, count in dataframe.isna().sum().items()
    }

    numeric_summary = {}

    if numeric_columns:
        numeric_summary = json.loads(
            dataframe[numeric_columns]
            .describe()
            .round(3)
            .to_json()
        )

    categorical_summary = {}

    for column in categorical_columns[:20]:
        categorical_summary[column] = json.loads(
            dataframe[column]
            .value_counts(dropna=True)
            .head(5)
            .to_json()
        )

    correlation = {}

    if len(numeric_columns) >= 2:
        correlation = json.loads(
            dataframe[numeric_columns]
            .corr()
            .round(3)
            .to_json()
        )

    preview = json.loads(
        dataframe.head(10).to_json(orient="records")
    )

    chart_columns = numeric_columns[:3]

    chart_data = json.loads(
        dataframe[chart_columns]
        .head(200)
        .to_json(orient="records")
    ) if chart_columns else []

    duplicate_rows = int(dataframe.duplicated().sum())

    return {
        "filename": filename,
        "analysis_status": "completed",
        "dataset": {
            "rows": int(len(dataframe)),
            "columns": int(len(dataframe.columns)),
            "numeric_columns": numeric_columns,
            "categorical_columns": categorical_columns,
            "duplicate_rows": duplicate_rows,
            "memory_usage_bytes": int(
                dataframe.memory_usage(deep=True).sum()
            ),
        },
        "column_types": {
            str(column): str(dtype)
            for column, dtype in dataframe.dtypes.items()
        },
        "missing_values": missing,
        "numeric_summary": numeric_summary,
        "categorical_summary": categorical_summary,
        "correlation": correlation,
        "preview": preview,
        "chart_columns": chart_columns,
        "chart_data": chart_data,
        "limitations": [
            "Statistics are calculated from the uploaded CSV.",
            "Correlations do not establish causation.",
            "No external data sources were consulted.",
            "AI-generated conclusions have not been used.",
        ],
    }
