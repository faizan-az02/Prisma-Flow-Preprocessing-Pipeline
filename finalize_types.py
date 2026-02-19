import pandas as pd
import logging
from divider import divider
from pandas.api.types import is_object_dtype, is_string_dtype
import re
import warnings

def finalize_dtypes(df, exclude_cols=None):

    logging.info("=== DTYPE FINALIZATION STARTED ===")
    exclude = set(exclude_cols or [])

    def _looks_datetime_by_name(name: str) -> bool:
        key = str(name or "").strip().lower()
        return any(
            k in key
            for k in (
                "date",
                "datetime",
                "time",
                "timestamp",
                "created",
                "updated",
                "modified",
                "dob",
            )
        )

    _dateish_hint = re.compile(
        r"(?:"
        r"\d{1,4}[-/\.]\d{1,2}[-/\.]\d{1,4}"  # 2026-02-19, 19/02/2026, 02.19.2026
        r"|\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4}"  # 2/19/26
        r"|[A-Za-z]{3,9}\s+\d{1,2}(?:,)?\s+\d{2,4}"  # Feb 19 2026, February 19, 2026
        r"|\d{1,2}\s+[A-Za-z]{3,9}\s+\d{2,4}"  # 19 Feb 2026
        r")"
    )
    _timeonly_hint = re.compile(r"^\d{1,2}:\d{2}(?::\d{2})?$")

    for col in df.columns:
        if col in exclude:
            continue
        original_dtype = df[col].dtype

        # Try numeric conversion
        if is_object_dtype(df[col]) or is_string_dtype(df[col]):
            try:
                converted = pd.to_numeric(df[col])
                df[col] = converted
                logging.info(f'Converted Column "{col}" to {df[col].dtype}')
                continue
            except:
                pass

        # Try datetime conversion
        if is_object_dtype(df[col]) or is_string_dtype(df[col]):
            try:
                s = df[col]
                # Normalize empties before scoring parse ratio
                non_empty = s.notna()
                if non_empty.sum() == 0:
                    raise ValueError("no non-empty values")

                # Only attempt datetime conversion when the column is very likely date-like:
                # - name indicates datetime OR
                # - almost all values parse as datetime in common formats
                name_hint = _looks_datetime_by_name(col)

                sample = s[non_empty].astype(str).str.strip().head(120)

                # Avoid converting "time-only" strings (temporal_features handles these separately).
                timeonly_ratio = float(sample.str.match(_timeonly_hint).mean()) if len(sample) else 0.0
                dateish_ratio = float(sample.str.contains(_dateish_hint, regex=True).mean()) if len(sample) else 0.0
                if timeonly_ratio >= 0.95 and dateish_ratio < 0.2:
                    raise ValueError("time-only column")

                # If it doesn't look date-ish and the name doesn't hint, don't even try.
                if not name_hint and dateish_ratio < 0.4:
                    raise ValueError("not date-like")

                # Try parsing with both dayfirst settings; keep the one with higher success ratio.
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=UserWarning)
                    conv0 = pd.to_datetime(s, errors="coerce", utc=True, dayfirst=False)
                    conv1 = pd.to_datetime(s, errors="coerce", utc=True, dayfirst=True)

                parsed0 = int(conv0.notna().sum())
                parsed1 = int(conv1.notna().sum())
                total = int(non_empty.sum())
                ratio0 = (parsed0 / total) if total else 0.0
                ratio1 = (parsed1 / total) if total else 0.0

                converted = conv1 if (ratio1 > ratio0 + 0.02) else conv0
                ratio = max(ratio0, ratio1)

                should_convert = (name_hint and ratio >= 0.6) or (ratio >= 0.95)
                if should_convert:
                    # Ensure we end up with a plain datetime64 dtype (no timezone)
                    df[col] = converted.dt.tz_convert(None).astype("datetime64[ns]")
                    logging.info(f'Converted column "{col}" to {df[col].dtype}')
                    continue

            except:
                pass

        # Keep remaining text columns as strings
        if is_object_dtype(df[col]) or is_string_dtype(df[col]):
            df[col] = df[col].astype("string")
            logging.info(f'Kept Column "{col}" as {df[col].dtype}')

        if df[col].dtype == original_dtype:
            logging.info(f'Column "{col}" kept as {original_dtype}')

    logging.info("=== DTYPE FINALIZATION COMPLETED ===")

    divider()

    return df
