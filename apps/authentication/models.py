from flask_login import UserMixin
from apps import db, login_manager
from apps.authentication.util import hash_pass


class Users(db.Model, UserMixin):
    """
    User model for the authentication system.

    Attributes:
        id (int): Primary key for the user.
        username (str): Username for the user.
        email (str): Email address for the user.
        password (bytes): Password for the user.
    """

    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.LargeBinary)

    def __init__(self, **kwargs):
        """
        Initialize the user object.

        Args:
            **kwargs: Keyword arguments for the user attributes.
        """
        for property, value in kwargs.items():
            # Depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # The ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass(value)  # We need bytes here (not plain str)

            setattr(self, property, value)

    def __repr__(self):
        """
        Return a string representation of the user.

        Returns:
            str: Username of the user.
        """
        return str(self.username)


@login_manager.user_loader
def user_loader(id):
    """
    Load a user from the database based on their ID.

    :param id: The ID of the user to load.
    :type id: int
    :return: The user object if found, None otherwise.
    :rtype: Users or None
    """
    return Users.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    """
    Load a user from the database based on the request.

    :param request: The request object.
    :type request: object
    :return: The user object if found, None otherwise.
    :rtype: Users or None
    """
    username = request.form.get('username')
    user = Users.query.filter_by(username=username).first()
    return user if user else None
