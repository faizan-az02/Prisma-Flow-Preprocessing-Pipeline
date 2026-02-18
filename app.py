import os
import uuid
import io
import time
import logging
from datetime import timedelta

import pandas as pd
from flask import (
    Flask,
    flash,
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


def _df_head_html(df: pd.DataFrame, max_cols: int = 50) -> str:
    preview = df.head()
    if preview.shape[1] > max_cols:
        preview = preview.iloc[:, :max_cols]
    return preview.to_html(index=False, classes="df-table", border=0, escape=True)

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
        has_logs=os.path.exists(LOG_PATH) and os.path.getsize(LOG_PATH) > 0,
    )


@app.post("/upload")
def upload():
    _cleanup_store()
    file = request.files.get("file")
    if not file or not file.filename:
        flash("Please choose a CSV file to upload.", "error")
        return redirect(url_for("index"))

    if not _allowed_file(file.filename):
        flash("Only .csv files are supported.", "error")
        return redirect(url_for("index"))

    original_name = secure_filename(file.filename)
    raw_bytes = file.read()
    if not raw_bytes:
        flash("Uploaded file is empty.", "error")
        return redirect(url_for("index"))
    if len(raw_bytes) > _STORE_MAX_BYTES:
        flash("File too large (max 50MB).", "error")
        return redirect(url_for("index"))

    try:
        df = _read_csv_safely_bytes(raw_bytes)
    except Exception as e:
        flash(f"Failed to read CSV: {e}", "error")
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
        "processed_preview_html": None,
        "processed_bytes": None,
    }

    flash("Upload successful. Preview shown below.", "success")
    return redirect(url_for("index"))


@app.post("/run/default")
def run_default():
    _cleanup_store()
    token = _get_token()
    if not token:
        flash("Upload a CSV first.", "error")
        return redirect(url_for("index"))

    try:
        df = _read_csv_safely_bytes(_STORE[token]["raw_bytes"])
    except Exception as e:
        flash(f"Failed to read uploaded CSV: {e}", "error")
        return redirect(url_for("index"))

    processed_df = prismaflow_pipeline(
        df,
        target_col=None,
        manual_columns=None,
        outlier_skipping=None,
        columns_to_keep=None,
        output_file=None,
        return_df=True,
    )
    if processed_df is None:
        flash("Pipeline failed. Check logs.txt for details.", "error")
        return redirect(url_for("index"))

    try:
        processed_bytes = processed_df.to_csv(index=False).encode("utf-8")
    except Exception as e:
        flash(f"Failed to generate processed CSV: {e}", "error")
        return redirect(url_for("index"))

    _STORE[token]["processed_preview_html"] = _df_head_html(processed_df)
    _STORE[token]["processed_bytes"] = processed_bytes
    flash("Default preprocessing complete. Download is ready.", "success")
    return redirect(url_for("index"))


@app.post("/run/custom")
def run_custom():
    _cleanup_store()
    token = _get_token()
    if not token:
        flash("Upload a CSV first.", "error")
        return redirect(url_for("index"))

    try:
        df = _read_csv_safely_bytes(_STORE[token]["raw_bytes"])
    except Exception as e:
        flash(f"Failed to read uploaded CSV: {e}", "error")
        return redirect(url_for("index"))

    target_col = (request.form.get("target_col") or "").strip() or None
    manual_columns = request.form.getlist("manual_columns") or None
    outlier_skipping = request.form.getlist("outlier_skipping") or None
    columns_to_keep = request.form.getlist("columns_to_keep") or None

    try:
        processed_df = prismaflow_pipeline(
            df,
            target_col=target_col,
            manual_columns=manual_columns,
            outlier_skipping=outlier_skipping,
            columns_to_keep=columns_to_keep,
            output_file=None,
            return_df=True,
        )
    except Exception as e:
        flash(f"Pipeline error: {e}", "error")
        return redirect(url_for("index"))

    if processed_df is None:
        flash("Pipeline failed. Check logs.txt for details.", "error")
        return redirect(url_for("index"))

    try:
        processed_bytes = processed_df.to_csv(index=False).encode("utf-8")
    except Exception as e:
        flash(f"Failed to generate processed CSV: {e}", "error")
        return redirect(url_for("index"))

    _STORE[token]["processed_preview_html"] = _df_head_html(processed_df)
    _STORE[token]["processed_bytes"] = processed_bytes
    flash("Custom preprocessing complete. Download is ready.", "success")
    return redirect(url_for("index"))


@app.get("/download")
def download():
    _cleanup_store()
    token = _get_token()
    if not token:
        flash("Upload a CSV and run preprocessing first.", "error")
        return redirect(url_for("index"))
    processed_bytes = _STORE[token].get("processed_bytes")
    if not processed_bytes:
        flash("Run preprocessing first.", "error")
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
        flash("No logs available yet. Run preprocessing first.", "error")
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

