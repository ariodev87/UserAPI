def user_schema(user: dict) -> dict:
    return {
        "id": str(user.get("_id")),
        "username": user.get("username"),
        "email": user.get("email"),
        "password": user.get("password")
    }