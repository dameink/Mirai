import os


BASE_DIR = "data/users"


def get_user_dir(user_id):
    if not user_id:
        raise ValueError("user_id is required")

    user_dir = os.path.join(BASE_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)

    return user_dir


def get_user_file(user_id, filename):
    return os.path.join(
        get_user_dir(user_id),
        filename
    )