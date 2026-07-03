from app.models import User


def get_user_by_id(user_id):
    """
    Find and return single user by ID using ORM.
    Returns None if not found.
    Used by auth decorators on every page load.
    """
    return User.query.filter_by(id=user_id).first()
