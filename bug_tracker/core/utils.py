import uuid
from pathlib import Path


def snake_to_title_case(text: str) -> str:
    return text.replace("_", " ").replace("-", " ").capitalize()


def generate_username(prefix: str = "user_") -> str:
    return f"{prefix}{uuid.uuid4().hex[:8]}"


def bytes_to_mib(value: int) -> float:
    return value / (1 << 20)


def get_file_extension(filename: str) -> str:
    return Path(filename).suffix.lstrip(".").lower()
