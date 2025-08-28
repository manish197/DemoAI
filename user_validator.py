
import re

def validate_user(name: str, age: int, email: str):
    """
    Validates user input:
    - name: alphabets only
    - age: >= 18
    - email: standard email format
    """
    if not isinstance(name, str) or not name.isalpha():
        raise ValueError("Name must only contain alphabets.")

    if not isinstance(age, int) or age < 18:
        raise ValueError("Age must be at least 18.")

    email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    if not isinstance(email, str) or not re.match(email_pattern, email):
        raise ValueError("Invalid email format.")

    return {"status": "ok", "message": "All inputs are valid!"}
