"""
Part 3: what tags best describe a user?

    uv run python part3_users.py

The handout's Part 3 is the spec. One piece is written for you, the piece that has to agree
with `WRITEUP.md` line for line: reading the 20 ratings out of your "My 20 ratings" slot and
adding you to the ratings table as a user of your own. Everything after that is yours.

You are added under userId 999999. Real userIds in `data/ratings.csv.gz` stop at 200,935, so
that number cannot be a real person's, and it is easy to pick out of a printout.

What this script must print, under the labels shown:

    == (1) my ratings ==
        How many ratings were read out of your slot, how many lines it could not read a
        rating from, and how many rows the ratings table has with yours in it. Twenty
        ratings is what the handout asks for; the script reports what it found and leaves
        the count to you.

    == (2) score(user, tag) ==
        Your `score(user, tag)` over the users you are looking at, your own row included.
        Write it in this file as

            score(ratings_df, tags_df, movies_df) -> DataFrame[userId, tag, score]

        one row per user-tag pair, higher score meaning the tag describes the user better.
        Print your own ten best tags, and the number of rows and distinct users it returned.
        What the score is, and why you started there, is yours and goes in `WRITEUP.md`.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse

from load_data import load_all

REPO = Path(__file__).resolve().parent
WRITEUP = REPO / "WRITEUP.md"

ME = 999999                 # your userId: above every real one, so it collides with nobody
SLOT = "My 20 ratings"      # the WRITEUP.md slot your ratings are read from
TARGETS = [ME]              # the people score() is computed for: one against everyone
PREFIX = 4                  # the Part 2 merge: tags sharing their first four letters
GROUP = 20                  # judge/users.csv: this many most and least similar people
ON_MINE = 10                # a judged tag is on at least this many of your twenty movies
MIN_PEOPLE = 30             # ...and was applied by at least this many people
USERS_CSV = REPO / "judge" / "users.csv"
# Improvement 2, the student's synonym groups. Each group keeps the name with more applications.
SYNONYMS = [{"great soundtrack", "music"}, {"classic", "cult film"}]


def read_my_ratings(writeup: Path = WRITEUP) -> tuple[pd.DataFrame, int]:
    """Your ratings from the "My 20 ratings" slot in WRITEUP.md, as movieId and rating.

    The same rule the judge uses for "My ten movies": every line in that slot starts with a
    movieId. The rating is the last number on the line, so the title between them is for
    people and may hold anything, the year included. Bare lines only: a bulleted or a
    numbered list reads as no ratings at all, or reads the list numbers as movieIds.

        296, Pulp Fiction (1994), 4.5

    A line whose last number is not a rating between 0.5 and 5.0 is left out and counted,
    because the year in a title is a number too: `296, Pulp Fiction (1994)` with the rating
    forgotten would otherwise be read as a rating of 1994. So is the `XXXX` an unfilled slot
    holds, which is why this is safe to run before you have written anything.

    Returns the ratings and how many lines were left out."""
    rows, skipped, inside = [], 0, False
    for line in writeup.read_text(encoding="utf-8").splitlines():
        if line.startswith("**"):            # a bold label opens the next slot
            inside = SLOT in line
            continue
        if not inside or not re.match(r"\s*\d", line):
            continue
        numbers = re.findall(r"\d+(?:\.\d+)?", line)
        rating = float(numbers[-1]) if len(numbers) > 1 else 0.0
        if not 0.5 <= rating <= 5.0:
            skipped += 1
            continue
        rows.append({"movieId": int(numbers[0].split(".")[0]), "rating": rating})
    return pd.DataFrame(rows, columns=["movieId", "rating"]), skipped


def add_me(ratings: pd.DataFrame, mine: pd.DataFrame) -> pd.DataFrame:
    """Your ratings appended to everybody else's, under userId ME.

    The timestamp is the newest one in the data: you rated these after everyone else did."""
    if mine.empty:
        return ratings
    mine = mine.assign(userId=ME, timestamp=int(ratings["timestamp"].max()))
    return pd.concat([ratings, mine[ratings.columns]], ignore_index=True)


# ------------------------------------------------------------------- yours to write ---

def tag_groups(tags: pd.DataFrame) -> pd.DataFrame:
    """Each tag application with the merged tag it counts as: userId, tag.

    The Part 2 rule, run across all tags rather than within a movie: lowercase, then merge
    tags that share their first four letters. A tag under four letters stays on its own. A
    group is named by its most-applied member; a tie goes A to Z."""
    t = tags[["userId", "tag"]].astype({"tag": str})
    t = t.assign(lower=t["tag"].str.lower())
    short = t["lower"].str.len() < PREFIX
    t["key"] = t["lower"].str[:PREFIX].where(~short, "<4:" + t["lower"])
    names = t.groupby(["key", "lower"]).size().rename("n").reset_index()
    names = (names.sort_values(["key", "n", "lower"], ascending=[True, False, True])
             .drop_duplicates("key").set_index("key")["lower"])
    return t.assign(tag=t["key"].map(names))[["userId", "tag"]]


def similarity(ratings: pd.DataFrame, user: int) -> pd.Series:
    """Cosine similarity of `user` to every other person, on raw ratings. A movie someone
    did not rate counts as empty (zero) in their vector."""
    users = pd.Index(ratings["userId"].unique())
    films = pd.Index(ratings["movieId"].unique())
    m = sparse.csr_matrix((ratings["rating"].to_numpy(),
                           (users.get_indexer(ratings["userId"]),
                            films.get_indexer(ratings["movieId"]))),
                          shape=(len(users), len(films)))
    me = m[users.get_loc(user)]
    dots = np.asarray((m @ me.T).todense()).ravel()
    norms = np.sqrt(np.asarray(m.multiply(m).sum(axis=1)).ravel())
    sims = pd.Series(dots / (norms * norms[users.get_loc(user)]), index=users)
    return sims.drop(user)


def score(ratings: pd.DataFrame, tags: pd.DataFrame, movies: pd.DataFrame):
    """What tags best describe a user: the student's rule.

    For a person and a tag, add up the cosine similarity (raw ratings) of every other
    person who applied that tag at least once. Each person counts once per tag, however
    many times they used it. Computed for the people in TARGETS, one against everyone.

    Improvement 1: only the tags the judge rates are scored (`judged_tags`), so the score
    and the judge rank the same set. Improvement 2: the tags in each SYNONYMS group count as
    one, named after the member with more applications."""
    judged = set(judged_tags(tags, ratings[ratings["userId"] == ME]))
    groups = tag_groups(tags)
    applied = groups.drop_duplicates()
    applied = applied[applied["tag"].isin(judged)]
    # Improvement 2: synonyms count as one tag, still once per person.
    uses = groups["tag"].value_counts()
    for group in SYNONYMS:
        keep = max(sorted(group), key=lambda t: uses.get(t, 0))
        applied = applied.assign(tag=applied["tag"].where(~applied["tag"].isin(group), keep))
    applied = applied.drop_duplicates()
    out = []
    for user in TARGETS:
        sims = similarity(ratings, user).rename("sim")
        rows = applied[applied["userId"] != user].join(sims, on="userId")
        got = rows.groupby("tag")["sim"].sum().rename("score").reset_index()
        out.append(got.assign(userId=user))
    return pd.concat(out, ignore_index=True)[["userId", "tag", "score"]]


def judged_tags(tags: pd.DataFrame, mine: pd.DataFrame) -> list[str]:
    """The tags the judge rates for every person: merged tags on at least ON_MINE of your
    twenty movies, applied by MIN_PEOPLE or more people."""
    g = tag_groups(tags).assign(movieId=tags["movieId"].to_numpy())
    people = g[["userId", "tag"]].drop_duplicates().groupby("tag").size()
    films = g[g.movieId.isin(mine.movieId)].groupby("tag")["movieId"].nunique()
    keep = films[films >= ON_MINE].index
    return sorted(t for t in keep if people[t] >= MIN_PEOPLE)


def write_users_csv(ratings, tags, movies, mine) -> pd.DataFrame:
    """judge/users.csv: you, your GROUP most similar people, and your GROUP least similar
    people above zero. Each description lists the movies a person shares with your twenty,
    in the order of your slot, each with their stars and the (merged) tags they applied."""
    sims = similarity(ratings, ME)
    near = sims.sort_values(ascending=False).head(GROUP).index
    far = sims[sims > 0].sort_values().head(GROUP).index
    people = [(ME, "my own")] + [(u, "similar") for u in near] + [(u, "dissimilar") for u in far]
    titles = movies.set_index("movieId")["title"]
    order = list(mine.movieId)
    g = tag_groups(tags).assign(movieId=tags["movieId"].to_numpy())
    tag_list = "|".join(judged_tags(tags, mine))
    rows = []
    for user, label in people:
        theirs = ratings[(ratings.userId == user) & ratings.movieId.isin(order)]
        stars = dict(zip(theirs.movieId, theirs.rating))
        applied = g[(g.userId == user) & g.movieId.isin(order)]
        parts = []
        for m in order:
            if m not in stars:
                continue
            on_it = sorted(set(applied.loc[applied.movieId == m, "tag"]))
            parts.append(f"{titles[m]} ({stars[m]:g}; tags: {', '.join(on_it) or 'none'})")
        rows.append({"id": user, "description": f"label: {label}; movies: {', '.join(parts)}",
                     "tags": tag_list})
    out = pd.DataFrame(rows)
    out.to_csv(USERS_CSV, index=False)
    return out


def part3_users(ratings, tags, movies, links):
    print("== (1) my ratings ==")
    mine, skipped = read_my_ratings()
    print(f'{len(mine)} rating(s) read from the "{SLOT}" slot in WRITEUP.md.')
    if not len(mine):
        print(f'Nothing was read out of the "{SLOT}" slot. It is read one rating to a line, '
              f"with no bullets and no numbering: the movieId first, then the title, then "
              f"your rating, as in `296, Pulp Fiction (1994), 4.5`.")
    if skipped:
        print(f"{skipped} line(s) in that slot had no rating between 0.5 and 5.0 at the "
              f"end and were left out.")
    ratings = add_me(ratings, mine)
    if len(mine):
        print(f"{len(ratings):,} ratings with yours in, as userId {ME}.")
    else:
        print(f"{len(ratings):,} ratings, none of them yours yet.")

    print("== (2) score(user, tag) ==")
    scores = score(ratings, tags, movies)
    top = scores[scores.userId == ME].sort_values(["score", "tag"], ascending=[False, True])
    print(f"userId {ME}: ten best tags by score()")
    for row in top.head(10).itertuples():
        print(f"{row.score:9.2f}  {row.tag}")
    print(f"{len(scores):,} rows over {scores.userId.nunique()} user(s)")

    print("== (3) judge/users.csv ==")
    users = write_users_csv(ratings, tags, movies, mine)
    print(f"wrote {len(users)} people to {USERS_CSV.relative_to(REPO)}, "
          f"{users.tags.iloc[0].count('|') + 1} tags each")


if __name__ == "__main__":
    ratings, tags, movies, links = load_all()
    part3_users(ratings, tags, movies, links)
