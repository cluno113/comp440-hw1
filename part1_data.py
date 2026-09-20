"""
Part 1: whose data is this?

    uv run python part1_data.py

Write your own cut rule and your two checks before you run anything here. Doing it in that
order is what Part 1 is asking for. What this script must print, under the labels shown:

    == (a) how much ==
        Rows in each of the four files, distinct users, distinct movies, and the share of
        all 32,000,204 MovieLens ratings this set holds.

    == (b) spread ==
        Ratings per user and ratings per movie: median, minimum and maximum of each. Tag
        applications per user and per movie: the same three. How many of the users who
        rated anything ever applied a tag, as a count and as a share.

    == (c) top tags, two ways ==
        The 20 most-used tags by number of applications, and the 20 most-used tags by number
        of distinct users who applied them. Print the two lists one after the other, with
        both numbers on every row, so you can see where a tag's two ranks differ.

    == (d) two checks ==
        Two claims from (a) to (c) re-derived by a route that does not reuse the code that
        produced them, printed with both numbers side by side and the word MATCH or DIFFER.
        Targets that exist in this data: the share of all 32M ratings the set holds
        (`data/README.md` says 15.6 percent); the number of distinct users who applied a
        tag (14,019); the rating count of the least-rated kept movie (83); the 6 tag
        rows whose text is literally `NA`, which vanish if a reader is built without
        `keep_default_na=False`.

No figures are required in Part 1. `WRITEUP.md` takes one interesting thing from
`data/README.md`, your own cut rule and the rule you rejected, how `data/make_compact.py`'s
rule differs from yours, and your two checks.
"""

import csv
import gzip
from pathlib import Path

from load_data import load_all

DATA = Path(__file__).resolve().parent / "data"


def part1_data(ratings, tags, movies, links):
    print("== (a) how much ==")
    print(f"ratings.csv rows: {len(ratings)}")
    print(f"tags.csv rows: {len(tags)}")
    print(f"movies.csv rows: {len(movies)}")
    print(f"links.csv rows: {len(links)}")
    print(f"distinct users: {ratings['userId'].nunique()}")
    print(f"distinct movies: {ratings['movieId'].nunique()}")
    share = len(ratings) / 32_000_204
    print(f"share of all 32,000,204 MovieLens ratings: {share:.4%}")

    print("== (b) spread ==")
    ratings_per_user = ratings.groupby("userId").size()
    ratings_per_movie = ratings.groupby("movieId").size()
    tags_per_user = tags.groupby("userId").size()
    tags_per_movie = tags.groupby("movieId").size()
    print(f"ratings per user: median {ratings_per_user.median()}, "
          f"min {ratings_per_user.min()}, max {ratings_per_user.max()}")
    print(f"ratings per movie: median {ratings_per_movie.median()}, "
          f"min {ratings_per_movie.min()}, max {ratings_per_movie.max()}")
    print(f"tag applications per user: median {tags_per_user.median()}, "
          f"min {tags_per_user.min()}, max {tags_per_user.max()}")
    print(f"tag applications per movie: median {tags_per_movie.median()}, "
          f"min {tags_per_movie.min()}, max {tags_per_movie.max()}")
    raters = set(ratings["userId"].unique())
    taggers = set(tags["userId"].unique())
    raters_who_tagged = raters & taggers
    print(f"raters who ever applied a tag: {len(raters_who_tagged)} "
          f"({len(raters_who_tagged) / len(raters):.4%} of {len(raters)} raters)")

    print("== (c) top tags, two ways ==")
    by_applications = tags["tag"].value_counts()
    by_users = tags.groupby("tag")["userId"].nunique().sort_values(ascending=False)
    print("-- top 20 by number of applications --")
    for tag, count in by_applications.head(20).items():
        print(f"{count:6d} applications, {by_users[tag]:6d} distinct users  {tag}")
    print("-- top 20 by number of distinct users --")
    for tag, count in by_users.head(20).items():
        print(f"{count:6d} distinct users, {by_applications[tag]:6d} applications  {tag}")

    print("== (d) two checks ==")
    with gzip.open(DATA / "ratings.csv.gz", "rt", newline="") as f:
        raw_rating_rows = sum(1 for _ in csv.reader(f)) - 1  # minus header
    raw_share = raw_rating_rows / 32_000_204
    verdict = "MATCH" if raw_rating_rows == len(ratings) else "DIFFER"
    print(f"share of 32M ratings: (a) says {share:.4%} ({len(ratings)} rows), "
          f"raw line count gives {raw_share:.4%} ({raw_rating_rows} rows) -- {verdict}")

    with gzip.open(DATA / "tags.csv.gz", "rt", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        tag_col = header.index("tag")
        raw_na_count = sum(1 for row in reader if row[tag_col] == "NA")
    loaded_na_count = int((tags["tag"] == "NA").sum())
    verdict = "MATCH" if raw_na_count == loaded_na_count else "DIFFER"
    print(f"literal 'NA' tag rows: loaded frame says {loaded_na_count}, "
          f"raw line scan gives {raw_na_count} -- {verdict}")


if __name__ == "__main__":
    ratings, tags, movies, links = load_all()
    part1_data(ratings, tags, movies, links)
