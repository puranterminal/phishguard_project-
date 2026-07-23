from app.database import get_connection


def get_user_by_id(user_id):
    """
    Find and return single user by ID.
    Returns None if not found.
    Used by auth decorators on every page load.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user
