
import streamlit as st
import importlib.util
import inspect
import json
import re
import tempfile
from pathlib import Path

st.set_page_config(page_title="AI Code + Input Validator", page_icon="✅", layout="centered")

st.title("AI Code + Input Validator")
st.caption("Upload a Python file, pick a function, provide JSON inputs, and validate via execution.")

# --- Helpers ---
def load_module_from_bytes(name: str, file_bytes) :
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".py")
    tmp.write(file_bytes)
    tmp.flush()
    tmp.close()
    spec = importlib.util.spec_from_file_location(name, tmp.name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, tmp.name

def get_functions(module):
    return {name: obj for name, obj in inspect.getmembers(module, inspect.isfunction) if obj.__module__ == module.__name__}

def suggest_fixes_from_exception(e_msg: str, payload: dict):
    s = payload.copy()
    low = e_msg.lower()

    # Generic patterns
    # Name alpha-only
    if ("alphabet" in low or "letters" in low) and any(k.lower()=="name" for k in payload):
        key = [k for k in payload if k.lower()=="name"][0]
        s[key] = "".join([c for c in str(payload[key]) if c.isalpha()]) or "John"

    # Age >= 18 pattern (detected via numbers in message or explicit "at least")
    age_keys = [k for k in payload if k.lower() in ("age","ages","user_age")]
    if age_keys:
        if ("age" in low and ("at least" in low or ">=" in low or "must be" in low)) or re.search(r"age.*\d+", low):
            for k in age_keys:
                try:
                    s[k] = max(int(payload.get(k, 0)), 18)
                except Exception:
                    s[k] = 18

    # Email format
    if ("email" in low and ("format" in low or "invalid" in low or "@" in low)):
        email_keys = [k for k in payload if "email" in k.lower()]
        for k in email_keys:
            s[k] = "example@gmail.com"

    # Non-empty string requirement
    if "empty" in low or "blank" in low:
        for k,v in payload.items():
            if (isinstance(v, str) and not v.strip()):
                s[k] = "sample"

    # Min length like ">= N" or "at least N characters"
    m = re.search(r"at least\s+(\d+)\s*(chars|characters)?", low)
    if m:
        need = int(m.group(1))
        for k,v in payload.items():
            if isinstance(v, str) and len(v) < need:
                s[k] = (v or "") + "x"*(need-len(v))

    # Numeric expected
    if "must be int" in low or "integer" in low:
        for k,v in payload.items():
            if isinstance(v, str) and v.isdigit():
                s[k] = int(v)

    return s

def run_function(func, payload: dict):
    try:
        result = func(**payload)
        return {
            "valid": True,
            "result": result,
            "error": None,
            "suggestion": None
        }
    except Exception as e:
        e_msg = str(e)
        suggestion = suggest_fixes_from_exception(e_msg, payload)
        return {
            "valid": False,
            "result": None,
            "error": e_msg,
            "suggestion": suggestion
        }

# --- UI ---
uploaded = st.file_uploader("Upload a Python file containing validation functions", type=["py"])

if uploaded:
    with st.spinner("Loading module..."):
        module, tmp_path = load_module_from_bytes("uploaded_module", uploaded.getvalue())
        funcs = get_functions(module)

    if not funcs:
        st.error("No functions found in the uploaded file. Define at least one function.")
    else:
        func_name = st.selectbox("Select a function to validate with", options=sorted(funcs.keys()))
        func = funcs[func_name]

        # Display signature
        st.code(f"def {func_name}{inspect.signature(func)}", language="python")

        st.write("### Provide JSON Payload")
        placeholder = {p.name: "" for p in inspect.signature(func).parameters.values()}
        sample_json = st.text_area("Input JSON", value=json.dumps(placeholder, indent=2), height=200)

        if st.button("Run Validation", use_container_width=True):
            try:
                payload = json.loads(sample_json)
            except Exception as e:
                st.error(f"Invalid JSON: {e}")
                st.stop()

            with st.spinner("Executing..."):
                result = run_function(func, payload)

            if result["valid"]:
                st.success("VALID ✅")
                st.write("**Result:**")
                st.code(str(result["result"]))
            else:
                st.error("INVALID ❌")
                st.write("**Error Message:**")
                st.code(result["error"])
                st.write("**Fix Suggestion:**")
                st.code(json.dumps(result["suggestion"], indent=2))

        st.divider()
        st.write("#### Tip")
        st.caption("Write clear exceptions in your code (e.g., 'Age must be at least 18') so suggestions get smarter.")
else:
    st.info("Upload a Python file to begin. You can start with the sample `user_validator.py`.")

st.write("---")
st.caption("Demo app for AI-driven code + input validation.")
