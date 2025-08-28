def suggest_fix(input_data):
    suggestion = input_data.copy()

    # Fix name: keep only letters
    if "name" in suggestion:
        suggestion["name"] = ''.join([c for c in suggestion["name"] if c.isalpha()]) or "John"

    # Fix age: ensure it's an integer ≥ 18
    if "age" in suggestion:
        try:
            age = int(suggestion["age"])
            if age < 18:
                age = 18
            suggestion["age"] = age
        except:
            suggestion["age"] = 18

    # Fix email: very basic check
    if "email" in suggestion:
        email = suggestion["email"]
        if "@" not in email or "." not in email:
            suggestion["email"] = "example@example.com"

    return suggestion
