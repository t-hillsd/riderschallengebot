import praw

import db

SUBREDDIT = "riderschallengetest"
WANTED_KEYWORDS = ["complete"]


def add_point_and_generate_flair(user):
    with db.cursor() as c:
        if db.user_exists(c, user):
            db.add_point(c, user)
            return f"{db.get_points(user)} | {db.get_flair(user)}"
        else:
            db.create_user(c, user, points=1)
            return f"1 | {db.DEFAULT_FLAIR_TEXT}"


def is_wanted_submission(reddit, post):
    has_keyword = any(k.lower() in post.title.lower() for k in WANTED_KEYWORDS)
    is_self = post.author.name == reddit.user.me.name()
    if has_keyword and not is_self:
        return True


def main():
    reddit = praw.Reddit()
    sub = reddit.subreddit(SUBREDDIT)

    for post in sub.stream.submissions():
        if post.saved or not is_wanted_submission(reddit, post):
            continue

        post.save()

        # not entirely sure what all the reddit logic here is supposed to achieve
        sub.sticky(number=2).mod.flair(text="")

        new_flair = add_point_and_generate_flair(post.author.name)

        sub.flair.set(post.author.name, text=new_flair)
        post.mod.sticky()
        post.mod.flair(text="Current Challenge")


if __name__ == "__main__":
    main()
