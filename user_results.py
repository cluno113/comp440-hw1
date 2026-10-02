"""User viewer: what tags best describe a user, beside what tags describe everyone.

    uv run python user_results.py            # writes user_results.html
    uv run python user_results.py --text     # the same content as plain text

The student's design. Two lists side by side: your ten best tags by `score(user, tag)` from
`part3_users.py`, and the ten tags the most people applied across all users. Both use the
same lowercasing and four-letter merge, and both count a person once per tag.
"""

import argparse
import html
from pathlib import Path

from load_data import load_all
from part3_users import ME, add_me, read_my_ratings, score, tag_groups

REPO = Path(__file__).resolve().parent
TOP = 10


def build():
    ratings, tags, movies, _ = load_all()
    mine, _ = read_my_ratings()
    ratings = add_me(ratings, mine)
    scores = score(ratings, tags, movies)
    me = scores[scores.userId == ME].sort_values(["score", "tag"], ascending=[False, True])
    people = (tag_groups(tags).drop_duplicates().groupby("tag").size()
              .rename("people").reset_index()
              .sort_values(["people", "tag"], ascending=[False, True]))
    return list(me["tag"].head(TOP)), list(people["tag"].head(TOP))


def render(mine, everyone):
    def column(title, tags):
        items = "".join("<li>%s</li>" % html.escape(t) for t in tags)
        return '<div class="col"><h2>%s</h2><ol>%s</ol></div>' % (html.escape(title), items)
    css = ("body { font-family: Helvetica, Arial, sans-serif; margin: 20px; }\n"
           ".cols { display: flex; flex-wrap: wrap; gap: 32px; }\n"
           ".col { flex: 1 1 220px; min-width: 0; }")
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            "<title>User Viewer</title>\n<style>\n%s\n</style>\n</head>\n<body>\n"
            "<h1>User Viewer</h1>\n<div class=\"cols\">\n%s\n%s\n</div>\n</body>\n</html>\n"
            % (css, column("My ten best tags, by score()", mine),
               column("Top ten tags across all users, by people", everyone)))


def main():
    parser = argparse.ArgumentParser(description="Your top tags beside everyone's.")
    parser.add_argument("--out", default=str(REPO / "user_results.html"))
    parser.add_argument("--text", action="store_true")
    args = parser.parse_args()
    mine, everyone = build()
    if args.text:
        print("My ten best tags, by score()")
        print("\n".join("  %2d. %s" % (i, t) for i, t in enumerate(mine, 1)))
        print("Top ten tags across all users, by people")
        print("\n".join("  %2d. %s" % (i, t) for i, t in enumerate(everyone, 1)))
        return
    Path(args.out).write_text(render(mine, everyone), encoding="utf-8")
    print("wrote %s" % args.out)


if __name__ == "__main__":
    main()
