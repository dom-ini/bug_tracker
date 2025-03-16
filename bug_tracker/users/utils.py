from django.utils.http import int_to_base36


def user_id_to_url_str(user_id: int) -> str:
    return int_to_base36(user_id)
