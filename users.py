from db import DatabaseConnection
from sql_stmt import SQLStatements as sql

from hmac import compare_digest
from bcrypt import gensalt
import users_exceptions as exc
import hashlib
import secrets

class UsersManagement(DatabaseConnection):
    def __init__(self):
        DatabaseConnection.__init__(self)

    # Generates and adds token to database for specified user, then returns token
    def _create_token(self, user_id):
        token = secrets.token_urlsafe(48)
        
        cur = self.conn.cursor()
        cur.execute(
            sql.register_user_token,
            {
                "user_id":  user_id,
                "token":    token
            }
        )
        self.conn.commit()
        
        return token

    # Gets everything required to check password
    def _get_credentials(self, username):
        cur = self.conn.cursor()
        cur.execute(sql.get_user_credentials, {"username": username})
        credentials = cur.fetchone()

        if credentials is None:
            raise exc.UserDoesNotExist(username)

        return dict(credentials)
        
    # Hashes password with salt
    def _hash_password(self, password, salt):
        hashed = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100000
        )

        return hashed.hex()

    # Deletes access tokens for user, all_sessions to delete all tokens for a specified user
    def logout(self, user_id, token=None, all_sessions=False):
        cur = self.conn.cursor()
        if all_sessions:
            cur.execute(sql.delete_all_users_sessions, {"user_id": user_id})
        else:
            cur.execute(sql.delete_single_session, {"user_id": user_id, "token": token})

    # Deletes all user sessions
    def logout_everyone(self):
        cur = self.conn.cursor()
        cur.execute(sql.delete_all_sessions)


    def login(self, username, password):
        credentials = self._get_credentials(username)
        if not credentials:
            raise exc.IncorrectCredentials(username)

        hashed_password = self._hash_password(
            password,
            salt=credentials["salt"]
        )
        #Check password
        if not compare_digest(hashed_password, credentials["password_hash"]):
            raise exc.IncorrectCredentials(username)
        # Create and register token
        auth_token = self._create_token(credentials["user_id"])
        
        return auth_token

    # Checks if user token exists, and returns the user_id, username, expiration and timezone,
    # else, raise exc.InvalidToken
    def authenticate(self, token):
        cur = self.conn.cursor()
        cur.execute(sql.get_user_by_token, {"token": token})
        user = cur.fetchone()

        if user is None:
            raise exc.InvalidToken(token)
        
        return dict(user)