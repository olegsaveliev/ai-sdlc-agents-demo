def login(email, password):
    """Login user"""
    if not email or not password:
        raise ValueError("Missing credentials")
    return {"success": True, "user_id": 123}
