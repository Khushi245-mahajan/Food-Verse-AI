"""Analysis history. Stored only in the browser session (st.session_state): it is lost on refresh."""
import datetime as dt
import pandas as pd

COLUMNS = ["time", "module", "item", "category", "kcal_mid", "source", "note"]
MAX_RECORDS = 200


def make_record(module, item, category="", kcal_mid=None, source="", note=""):
    return {"time": dt.datetime.now().strftime("%Y-%m-%d %H:%M"), "module": module, "item": item,
            "category": category, "kcal_mid": kcal_mid, "source": source, "note": note}


def records_to_df(records) -> pd.DataFrame:
    return pd.DataFrame(records, columns=COLUMNS)


def df_to_json(df: pd.DataFrame) -> str:
    return df.to_json(orient="records", indent=2)


def _store():
    import streamlit as st
    return st.session_state.setdefault("history", [])


def add(*args, **kwargs):
    store = _store()
    store.append(make_record(*args, **kwargs))
    del store[:-MAX_RECORDS]


def get_df() -> pd.DataFrame:
    return records_to_df(_store())


def clear():
    _store().clear()
