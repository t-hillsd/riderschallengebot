import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

# avoid storing user data next to code
DB_DIR = Path(os.environ["USERPROFILE"], "RCBot")
DB_DIR.mkdir(exist_ok=True)
DB_FILE = str(DB_DIR / "RCMaster.db")

DEFAULT_FLAIR_TEXT = "Riders Challenge Participant"


@contextmanager
def cursor():
    try:
        conn = sqlite3.connect(DB_FILE, isolation_level=None)  # auto-commit
        conn.row_factory = (
            sqlite3.Row
        )  # so you can write row["points"] instead of row[0]
        conn.set_trace_callback(print)  # debug print the queries
        yield conn.cursor()
    finally:
        conn.close()


def setup_db(c):
    c.execute(
        "CREATE TABLE IF NOT EXISTS users (user STRING PRIMARY KEY UNIQUE, points INTEGER, flair STRING);"
    )  # if you have a fixed list of valid flairs, you might want to normalise this data by keeping them in a separate table and using FOREIGN KEY


def get_points(c, user):
    if row := c.execute("SELECT points FROM users WHERE user = ?;", (user,)).fetchone():
        return row["points"]
    else:
        raise UserDoesNotExist(user)


def user_exists(c, user):
    if c.execute("SELECT 1 FROM users WHERE user = ?;", (user,)).fetchone():
        return True


def get_flair(c, user):
    if row := c.execute("SELECT flair FROM users WHERE user = ?;", (user,)):
        return row["flair"]
    else:
        raise UserDoesNotExist(user)


def create_user(c, user, points=0):
    try:
        c.execute(
            "INSERT INTO users (user, points, flair) VALUES (?, ?, ?);",
            (user, 0, DEFAULT_FLAIR_TEXT),
        )
    except sqlite3.IntegrityError:
        raise UserAlreadyExists(user)


def add_point(c, user):
    c.execute(
        "UPDATE users SET points = ? WHERE user = ?;",
        (get_points(c, user) + 1, user),
    )


# Both these exceptions are overkill as we can assume the caller will not do stupid things like request points for a non-existing user
class UserDoesNotExist(Exception):
    pass


class UserAlreadyExists(Exception):
    pass
