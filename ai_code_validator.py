
# CLI runner: discovers functions in user_validator.py and runs sample payloads
import importlib.util
import inspect
import re
from pathlib import Path

def load_module_from_file(file_path):
    spec = importlib.util.spec_from_file_location("target_module", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def get_functions_from_module(module):
    return {name: obj for name, obj in inspect.getmembers(module, inspect.isfunction) if obj.__module__ == module.__name__}

def run_validation(func, data):
    print(f"\n🔎 Testing {func.__name__} with input: {data}")
    try:
        res = func(**data)
        print("✅ Validation Result: VALID")
        print(f"Reasoning/Return: {res}")
    except Exception as e:
        print("❌ Validation Result: INVALID")
        print(f"Error: {e}")

if __name__ == "__main__":
    file = Path("user_validator.py")
    module = load_module_from_file(file)
    funcs = get_functions_from_module(module)
    print(f"📂 Found functions: {list(funcs.keys())}")

    test_inputs = [
        {"name": "Manish123", "age": 15, "email": "manish@@gmail"},
        {"name": "Rahul", "age": 22, "email": "rahulgmail.com"},
        {"name": "Asha", "age": 20, "email": "asha@gmail.com"}
    ]

    for f in funcs.values():
        for t in test_inputs:
            run_validation(f, t)
