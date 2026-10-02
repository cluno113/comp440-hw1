"""User viewer: what tags best describe a user, beside what tags describe everyone.

    uv run python user_results.py            # writes user_results.html
    uv run python user_results.py --text     # the same content as plain text

The student's design. Three lists side by side: your ten best tags by `score(user, tag)` from
`part3_users.py`; the ten tags the most people applied across all users; and the judge's ten
best tags for you, from `judge/ratings_users.csv`. The first two use the same lowercasing and
four-letter merge, and both count a person once per tag. Ties in the judge's column go A to Z.
"""

import argparse
import html
from pathlib import Path

import pandas as pd

from load_data import load_all
from part3_users import ME, add_me, read_my_ratings, score, tag_groups

REPO = Path(__file__).resolve().parent
TOP = 10
JUDGE = REPO / "judge" / "ratings_users.csv"


def build():
    ratings, tags, movies, _ = load_all()
    mine, _ = read_my_ratings()
    ratings = add_me(ratings, mine)
    scores = score(ratings, tags, movies)
    me = scores[scores.userId == ME].sort_values(["score", "tag"], ascending=[False, True])
    people = (tag_groups(tags).drop_duplicates().groupby("tag").size()
              .rename("people").reset_index()
              .sort_values(["people", "tag"], ascending=[False, True]))
    judged = pd.read_csv(JUDGE, keep_default_na=False)
    judged = judged[judged["id"] == ME].sort_values(["rating", "tag"], ascending=[False, True])
    return (list(me["tag"].head(TOP)), list(people["tag"].head(TOP)),
            list(judged["tag"].head(TOP)))


def render(mine, everyone, judge):
    # Highlighted: a tag in all three columns, the student's rule.
    shared = set(mine) & set(everyone) & set(judge)

    def column(title, tags):
        items = "".join('<li class="shared">%s</li>' % html.escape(t) if t in shared
                        else "<li>%s</li>" % html.escape(t) for t in tags)
        return '<div class="col"><h2>%s</h2><ol>%s</ol></div>' % (html.escape(title), items)
    css = ("body { font-family: Helvetica, Arial, sans-serif; margin: 20px; }\n"
           ".cols { display: flex; flex-wrap: wrap; gap: 32px; }\n"
           ".col { flex: 1 1 220px; min-width: 0; }\n"
           ".shared { background: #fff1a8; }")
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            "<title>User Viewer</title>\n<style>\n%s\n</style>\n</head>\n<body>\n"
            "<h1>User Viewer</h1>\n<p><span class=\"shared\">Highlighted</span>: in all three "
            "columns.</p>\n<div class=\"cols\">\n%s\n%s\n%s\n</div>\n</body>\n</html>\n"
            % (css, column("My ten best tags, by score()", mine),
               column("Top ten tags across all users, by people", everyone),
               column("The judge's ten best tags for me", judge)))


def main():
    parser = argparse.ArgumentParser(description="Your top tags beside everyone's.")
    parser.add_argument("--out", default=str(REPO / "user_results.html"))
    parser.add_argument("--text", action="store_true")
    args = parser.parse_args()
    mine, everyone, judge = build()
    if args.text:
        print("My ten best tags, by score()")
        print("\n".join("  %2d. %s" % (i, t) for i, t in enumerate(mine, 1)))
        print("Top ten tags across all users, by people")
        print("\n".join("  %2d. %s" % (i, t) for i, t in enumerate(everyone, 1)))
        print("The judge's ten best tags for me")
        print("\n".join("  %2d. %s" % (i, t) for i, t in enumerate(judge, 1)))
        return
    Path(args.out).write_text(render(mine, everyone, judge), encoding="utf-8")
    print("wrote %s" % args.out)


if __name__ == "__main__":
    main()
