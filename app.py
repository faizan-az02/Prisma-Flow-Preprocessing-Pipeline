import os
import uuid
import io
import time
import logging
from datetime import timedelta

import pandas as pd
from flask import (
    Flask,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from werkzeug.utils import secure_filename

from main import prismaflow_pipeline


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(BASE_DIR, "logs.txt")

ALLOWED_EXTENSIONS = {"csv"}

PIPELINE_STEPS = [
    {"key": "manual_columns", "label": "Selected Columns Removal"},
    {"key": "drop_empty_columns", "label": "Drop Empty Columns"},
    {"key": "handle_nulls", "label": "Handle Null Values"},
    {"key": "finalize_dtypes", "label": "Finalize Data Types"},
    {"key": "handle_outliers", "label": "Handle Outliers"},
    {"key": "encoding", "label": "Encode Categorical Features"},
    {"key": "feature_selection", "label": "Feature Selection"},
    {"key": "temporal_features", "label": "Extract Temporal Features"},
    {"key": "scaling", "label": "Scaling"},
]

_STORE_TTL_SECONDS = 60 * 60  # 1 hour
_STORE_MAX_BYTES = 50 * 1024 * 1024  # 50MB
_STORE: dict[str, dict] = {}


def _allowed_file(filename: str) -> bool:
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def _read_csv_safely_bytes(data: bytes) -> pd.DataFrame:
    try:
        return pd.read_csv(io.BytesIO(data))
    except UnicodeDecodeError:
        return pd.read_csv(io.BytesIO(data), encoding="latin1")


def _df_head_html(df: pd.DataFrame, max_rows: int = 15) -> str:
    preview = df.head(max_rows)
    return preview.to_html(
        index=False,
        classes="df-table",
        border=0,
        escape=True,
        float_format=lambda x: f"{x:.2f}",
    )

def _cleanup_store() -> None:
    now = time.time()
    expired = [k for k, v in _STORE.items() if (now - float(v.get("created_at", 0))) > _STORE_TTL_SECONDS]
    for k in expired:
        _STORE.pop(k, None)


def _get_token() -> str | None:
    tok = session.get("token")
    if not tok:
        return None
    if tok not in _STORE:
        return None
    return tok

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["SECRET_KEY"] = os.environ.get("PRISMAFLOW_SECRET_KEY", "dev-secret-key-change-me")
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB
app.permanent_session_lifetime = timedelta(hours=2)

# Keep PrismaFlow's own pipeline logging intact, but don't let
# Flask/Werkzeug spam the console or the pipeline log file.
logging.getLogger("werkzeug").setLevel(logging.ERROR)
logging.getLogger("werkzeug").propagate = False
app.logger.disabled = True


@app.get("/")
def index():
    _cleanup_store()
    token = _get_token()
    state = _STORE.get(token, {}) if token else {}
    return render_template(
        "index.html",
        uploaded_filename=state.get("uploaded_filename"),
        columns=state.get("columns", []),
        preview_html=state.get("preview_html"),
        processed_preview_html=state.get("processed_preview_html"),
        has_processed=bool(state.get("processed_bytes")),
        raw_shape=state.get("raw_shape"),
        processed_shape=state.get("processed_shape"),
        metrics=state.get("metrics"),
        has_logs=os.path.exists(LOG_PATH) and os.path.getsize(LOG_PATH) > 0,
        pipeline_steps=PIPELINE_STEPS,
    )


@app.post("/upload")
def upload():
    _cleanup_store()
    file = request.files.get("file")
    if not file or not file.filename:
        return redirect(url_for("index"))

    if not _allowed_file(file.filename):
        return redirect(url_for("index"))

    original_name = secure_filename(file.filename)
    raw_bytes = file.read()
    if not raw_bytes:
        return redirect(url_for("index"))
    if len(raw_bytes) > _STORE_MAX_BYTES:
        return redirect(url_for("index"))

    try:
        df = _read_csv_safely_bytes(raw_bytes)
    except Exception as e:
        return redirect(url_for("index"))

    session.permanent = True
    token = uuid.uuid4().hex
    session["token"] = token
    _STORE[token] = {
        "created_at": time.time(),
        "uploaded_filename": original_name,
        "raw_bytes": raw_bytes,
        "columns": [str(c) for c in df.columns.tolist()],
        "preview_html": _df_head_html(df),
        "raw_shape": {"rows": int(df.shape[0]), "cols": int(df.shape[1])},
        "processed_preview_html": None,
        "processed_bytes": None,
        "processed_shape": None,
        "metrics": None,
    }

    return redirect(url_for("index"))


@app.post("/run/default")
def run_default():
    _cleanup_store()
    token = _get_token()
    if not token:
        return redirect(url_for("index"))

    try:
        df = _read_csv_safely_bytes(_STORE[token]["raw_bytes"])
    except Exception as e:
        return redirect(url_for("index"))

    processed_df = prismaflow_pipeline(
        df,
        target_col=None,
        manual_columns=None,
        columns_to_keep=None,
        output_file=None,
        return_df=True,
        collect_metrics=True,
    )
    if processed_df is None or (isinstance(processed_df, tuple) and processed_df[0] is None):
        return redirect(url_for("index"))
    if isinstance(processed_df, tuple):
        processed_df, metrics = processed_df
    else:
        metrics = None

    try:
        processed_bytes = processed_df.to_csv(index=False).encode("utf-8")
    except Exception as e:
        return redirect(url_for("index"))

    _STORE[token]["processed_preview_html"] = _df_head_html(processed_df)
    _STORE[token]["processed_bytes"] = processed_bytes
    _STORE[token]["processed_shape"] = {"rows": int(processed_df.shape[0]), "cols": int(processed_df.shape[1])}
    _STORE[token]["metrics"] = metrics
    return redirect(url_for("index"))


@app.post("/run/custom")
def run_custom():
    _cleanup_store()
    token = _get_token()
    if not token:
        return redirect(url_for("index"))

    try:
        df = _read_csv_safely_bytes(_STORE[token]["raw_bytes"])
    except Exception as e:
        return redirect(url_for("index"))

    target_col = (request.form.get("target_col") or "").strip() or None
    manual_columns = request.form.getlist("manual_columns") or None
    outlier_skipping = request.form.getlist("outlier_skipping") or None
    columns_to_keep = request.form.getlist("columns_to_keep") or None
    scaling_skipping = request.form.getlist("scaling_skipping") or None
    steps = request.form.getlist("steps") or None
    outlier_action = (request.form.get("outlier_action") or "remove").strip().lower()
    handle_outliers = outlier_action != "skip"
    outlier_drop = outlier_action != "cap"
    outlier_method = (request.form.get("outlier_method") or "iqr").strip().lower()
    raw_outlier_param = (request.form.get("outlier_param") or "").strip()
    try:
        outlier_param = float(raw_outlier_param) if raw_outlier_param != "" else None
    except Exception:
        outlier_param = None
    encoding_method = (request.form.get("encoding_method") or "label").strip().lower()
    scaling_method = (request.form.get("scaling_method") or "standard").strip().lower()
    raw_threshold = (request.form.get("null_threshold") or "").strip()
    try:
        null_threshold_percent = float(raw_threshold) if raw_threshold != "" else 5.0
    except Exception:
        null_threshold_percent = 5.0
    null_threshold = max(0.0, min(1.0, null_threshold_percent / 100.0))

    try:
        processed_df = prismaflow_pipeline(
            df,
            target_col=target_col,
            manual_columns=manual_columns,
            outlier_skipping=outlier_skipping,
            columns_to_keep=columns_to_keep,
            scaling_skipping=scaling_skipping,
            handle_outliers=handle_outliers,
            outlier_method=outlier_method,
            outlier_drop=outlier_drop,
            outlier_param=outlier_param,
            null_threshold=null_threshold,
            encoding_method=encoding_method,
            scaling_method=scaling_method,
            steps=steps,
            output_file=None,
            return_df=True,
            collect_metrics=True,
        )
    except Exception as e:
        return redirect(url_for("index"))

    if processed_df is None or (isinstance(processed_df, tuple) and processed_df[0] is None):
        return redirect(url_for("index"))
    if isinstance(processed_df, tuple):
        processed_df, metrics = processed_df
    else:
        metrics = None

    try:
        processed_bytes = processed_df.to_csv(index=False).encode("utf-8")
    except Exception as e:
        return redirect(url_for("index"))

    _STORE[token]["processed_preview_html"] = _df_head_html(processed_df)
    _STORE[token]["processed_bytes"] = processed_bytes
    _STORE[token]["processed_shape"] = {"rows": int(processed_df.shape[0]), "cols": int(processed_df.shape[1])}
    _STORE[token]["metrics"] = metrics
    return redirect(url_for("index"))


@app.get("/download")
def download():
    _cleanup_store()
    token = _get_token()
    if not token:
        return redirect(url_for("index"))
    processed_bytes = _STORE[token].get("processed_bytes")
    if not processed_bytes:
        return redirect(url_for("index"))

    base = (_STORE[token].get("uploaded_filename") or "processed").rsplit(".", 1)[0]
    download_name = f"{base}_processed.csv"
    return send_file(
        io.BytesIO(processed_bytes),
        as_attachment=True,
        download_name=download_name,
        mimetype="text/csv",
    )


@app.get("/download/logs")
def download_logs():
    if not os.path.exists(LOG_PATH) or os.path.getsize(LOG_PATH) == 0:
        return redirect(url_for("index"))
    return send_file(
        LOG_PATH,
        as_attachment=True,
        download_name="prismaflow_logs.txt",
        mimetype="text/plain",
    )


if __name__ == "__main__":
    # Debug mode prints a debugger PIN and extra server logs.
    # Keep it off by default; opt-in via PRISMAFLOW_DEBUG=1.
    debug = os.environ.get("PRISMAFLOW_DEBUG", "").strip() == "1"
    print("PrismaFlow UI running at http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=debug, use_reloader=False)

