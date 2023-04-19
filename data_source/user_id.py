def check_user_id(user_id: str) -> bool:
    return user_id.isdigit() and 11 >= len(user_id) >= 5
