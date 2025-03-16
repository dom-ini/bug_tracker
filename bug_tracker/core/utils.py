import uuid


def snake_to_title_case(text: str) -> str:
    return text.replace("_", " ").replace("-", " ").capitalize()


def generate_username(prefix: str = "user_") -> str:
    return f"{prefix}{uuid.uuid4().hex[:8]}"
