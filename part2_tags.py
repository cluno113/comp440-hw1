"""
Part 2: what tags best describe a movie?

    uv run python part2_tags.py

Steps 1 to 4 of the handout's Part 2 live here, plus the scores and the rankings that steps 5
and 6 need. The judge itself runs through `/judge`, and its answer is read through
`agreement.py` and `results_viewer.py`. What this script must print, under the labels shown,
and what it must write:

    == (1) the obvious answer ==
        Your chosen movie's title, its rating count and its tag-application count, then
        every tag applied to it with how many times it was applied, most-applied first.
        Pick a movie with at least 500 ratings and 30 tag applications. The most misleading
        entry in that list is your sentence in `WRITEUP.md`, not this script's.

    == (2) up close ==
        The numbers behind the one required figure and the two tables, so that everything
        shown here has printed output a reader can check it against. Write, to `figures/`:

            figures/part2_when.png          when the tags arrived: tag applications over
                                            time, with the movie's ratings over time behind
                                            them.

        The figure has labeled axes and a caption naming the question it answers. Claude
        may draw and label it; the sentence in `WRITEUP.md` about what it shows is yours.

        Then two tables, each printed under its own label:

            who added each tag              the movie's heaviest taggers, how many tag
                                            applications each made, and what share of the
                                            movie's applications that is.
            how the taggers rated it        for each of the movie's top tags, how the
                                            people who applied it rated the movie, beside
                                            how everyone else rated it.

        Claude prints the tables and says what the columns are. What they show is your two
        interesting details in `WRITEUP.md`, not this script's.

    == (3) my definition ==
        Your `score` over the whole set. Write it in this file as

            score(tags_df, ratings_df, movies_df) -> DataFrame[movieId, tag, score]

        one row per movie-tag pair, higher score meaning the tag describes the movie better.
        Print its top 15 rows for your chosen movie, and the number of rows and distinct
        movies it returned over the whole set. Families you could use, none of them
        preferred: distinct users who applied the tag; a rarity weight, the count times how
        few movies carry the tag; a damped version of either; something of your own. Whatever
        you choose, `WRITEUP.md` gets what you chose, what you rejected, and why.

    == (4) cleaning ==
        Whatever cleaning your `score()` does, and its size: how many raw tag strings went
        in, how many distinct tags came out, and the five mergers that absorbed the most
        applications. If you clean nothing, print that and say why in `WRITEUP.md`.
        Merging `Sci-Fi`, `sci-fi` and `scifi` is a decision, and so is not merging them.

    == (5) scores.csv ==
        `scores.csv` in the repo root, columns `movieId,tag,score`, holding a score for every
        movie and tag the judge will be asked about. That is two sets put together:

            every movie and tag in `judge/movies.csv`, which has one row per movie and a
            `tags` column of tags joined by `|`;
            plus, for each of the ten movies in your "My ten movies" slot, every tag from
            `judge/vocabulary.txt` that appears on it, matched after stripping and
            lowercasing, which is the same rule `judge/movies.csv` used.

        The second set matters because the judge adds your ten movies to its list, and
        `agreement.py` compares exactly what the two files share: a tag you never scored is
        dropped without a number. Print how many were asked for and how many you wrote.

    == (6) the four rankings ==
        For each of the ten movies in your "My ten movies" slot, four rankings of the same tags,
        printed one after another and never in one table:

            the counts: the ten most-used tags, by how many times each was applied;
            your own order, from the `WRITEUP.md` slot you filled before seeing any data;
            the judge's order, from `judge/ratings_movies.csv`;
            your `score()`'s order.

        Print each list under its own heading, best first. `results_viewer.py` builds the same
        four lists as a page you can read. Which tag is the artifact, and what the
        disagreements mean, is your paragraph in `WRITEUP.md`.
"""

import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from agreement import my_order_lines
from load_data import load_all

REPO = Path(__file__).resolve().parent
FIGURES = REPO / "figures"


MOVIE_ID = 1088  # Dirty Dancing (1987)

# The student's rule, from the "My definition" slots in WRITEUP.md. Multi-word tags are kept
# and go through the same four-letter merge as one-word tags.
PREFIX = 4
SHOW = 5  # tags per list in section (6), the student's choice


def clean(tags_df):
    """One row per movie and raw tag string that survives, with the group it merges into.

    Columns: movieId, raw, lower, count (applications of that raw string), key (the group).
    """
    t = tags_df[["movieId", "tag"]].astype({"tag": str})
    raw = t.groupby(["movieId", "tag"]).size().rename("count").reset_index()
    raw = raw.rename(columns={"tag": "raw"})
    raw["lower"] = raw["raw"].str.lower()
    # Under four letters: not in the merge, so each is its own group.
    short = raw["lower"].str.len() < PREFIX
    raw["key"] = raw["lower"].str[:PREFIX].where(~short, "<4:" + raw["lower"])
    return raw


def score(tags_df, ratings_df, movies_df):
    return groups(tags_df)[["movieId", "tag", "score"]]


def groups(tags_df):
    """score() with the merge group kept: one row per movie and group, named by its winner."""
    raw = clean(tags_df)
    # Same word, different case: average the counts, keep it lowercase.
    words = raw.groupby(["movieId", "key", "lower"])["count"].mean().reset_index()
    # Within a group, only the shortest length remains.
    length = words["lower"].str.len()
    words = words[length == length.groupby([words.movieId, words.key]).transform("min")]
    # Different words tied for shortest: average the counts, keep the more popular name.
    # (If they are also tied on count, the alphabetically first name is kept.)
    words = words.sort_values(["movieId", "key", "count", "lower"],
                              ascending=[True, True, False, True])
    out = words.groupby(["movieId", "key"]).agg(tag=("lower", "first"),
                                                score=("count", "mean")).reset_index()
    return out[["movieId", "key", "tag", "score"]]


def ten_movies():
    """The movieIds in the "My ten movies" slot of WRITEUP.md, in the order written."""
    slot = (REPO / "WRITEUP.md").read_text(encoding="utf-8").split("**My ten movies")[-1]
    return [int(n) for n in re.findall(r"^\s*(\d+)", slot.split("\n**")[0], re.M)]


def asked_pairs():
    """Every movie and tag the judge is asked about: judge/movies.csv, plus the vocabulary
    tags on the ten movies in the "My ten movies" slot, stripped and lowercased."""
    shipped = pd.read_csv(REPO / "judge" / "movies.csv", keep_default_na=False)
    shipped = (shipped.assign(tag=shipped["tags"].str.split("|")).explode("tag")
               .rename(columns={"id": "movieId"})[["movieId", "tag"]])
    mine = ten_movies()
    words = {t.strip() for t in (REPO / "judge" / "vocabulary.txt").read_text().splitlines()}
    raw = pd.read_csv(REPO / "data" / "tags.csv.gz", keep_default_na=False)
    raw = raw.assign(tag=raw["tag"].astype(str).str.strip().str.lower())
    on_mine = raw[raw.movieId.isin(mine) & raw.tag.isin(words)][["movieId", "tag"]]
    return pd.concat([shipped, on_mine]).drop_duplicates().reset_index(drop=True)


def part2_tags(ratings, tags, movies, links):
    print("== (1) the obvious answer ==")
    title = movies.set_index("movieId").loc[MOVIE_ID, "title"]
    movie_ratings = ratings[ratings.movieId == MOVIE_ID]
    movie_tags = tags[tags.movieId == MOVIE_ID]
    print(f"{title}: {len(movie_ratings)} ratings, {len(movie_tags)} tag applications")
    for tag, count in movie_tags["tag"].value_counts().items():
        print(f"{count:4d}  {tag}")

    print("== (2) up close ==")
    r_month = pd.to_datetime(movie_ratings.timestamp, unit="s").dt.to_period("M")
    t_month = pd.to_datetime(movie_tags.timestamp, unit="s").dt.to_period("M")
    ratings_by_month = r_month.value_counts().sort_index()
    tags_by_month = t_month.value_counts().sort_index()
    full_index = pd.period_range(
        min(ratings_by_month.index.min(), tags_by_month.index.min()),
        max(ratings_by_month.index.max(), tags_by_month.index.max()),
        freq="M",
    )
    ratings_by_month = ratings_by_month.reindex(full_index, fill_value=0)
    tags_by_month = tags_by_month.reindex(full_index, fill_value=0)
    print("ratings per month: first 5")
    print(ratings_by_month.head())
    print("tag applications per month: first 5")
    print(tags_by_month.head())

    x = full_index.to_timestamp()
    fig, ax = plt.subplots(figsize=(9, 5), facecolor="#fcfcfb")
    ax.set_facecolor("#fcfcfb")
    ax.fill_between(x, ratings_by_month.values, color="#eb6834", alpha=0.35,
                     label="ratings per month")
    ax.plot(x, tags_by_month.values, color="#2a78d6", linewidth=2,
             label="tag applications per month")
    ax.set_xlabel("Month")
    ax.set_ylabel("Count per month")
    ax.grid(True, color="#e1e0d9", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#c3c2b7")
    ax.tick_params(colors="#898781")
    ax.legend(frameon=False)
    fig.suptitle(f"{title}: when did tag applications arrive, relative to ratings?",
                 fontsize=11, color="#0b0b0b")
    fig.tight_layout()
    FIGURES.mkdir(exist_ok=True)
    fig.savefig(FIGURES / "part2_when.png", dpi=150)
    plt.close(fig)
    print(f"wrote {FIGURES / 'part2_when.png'}")

    print("-- who added each tag --")
    total_apps = len(movie_tags)
    by_user = movie_tags.groupby("userId").size().sort_values(ascending=False)
    for user_id, count in by_user.head(10).items():
        print(f"user {user_id}: {count} applications, {count / total_apps:.1%} of {total_apps}")

    print("-- how the taggers rated it --")
    top_tags = movie_tags["tag"].value_counts().head(10).index
    ratings_indexed = movie_ratings.set_index("userId")["rating"]
    for tag in top_tags:
        taggers = set(movie_tags.loc[movie_tags.tag == tag, "userId"])
        tagger_ratings = ratings_indexed[ratings_indexed.index.isin(taggers)]
        other_ratings = ratings_indexed[~ratings_indexed.index.isin(taggers)]
        print(f"{tag}: taggers mean {tagger_ratings.mean():.2f} (n={len(tagger_ratings)}), "
              f"everyone else mean {other_ratings.mean():.2f} (n={len(other_ratings)})")

    print("== (3) my definition ==")
    scores = score(tags, ratings, movies)
    mine = scores[scores.movieId == MOVIE_ID].sort_values(["score", "tag"],
                                                          ascending=[False, True])
    print(f"{title}: top 15 by score()")
    for row in mine.head(15).itertuples():
        print(f"{row.score:7.1f}  {row.tag}")
    print(f"whole set: {len(scores)} rows over {scores.movieId.nunique()} movies")

    print("== (4) cleaning ==")
    raw_all = tags[["movieId", "tag"]].astype({"tag": str}).drop_duplicates()
    kept = clean(tags)
    print(f"raw movie-tag strings in: {len(raw_all)} "
          f"({raw_all.tag.nunique()} distinct strings)")
    print(f"dropped: {len(raw_all) - len(kept)}")
    print(f"movie-tag pairs out: {len(scores)} ({scores.tag.nunique()} distinct tags)")
    # A merger is a group that folded more than one raw string into one tag.
    sizes = kept.groupby(["movieId", "key"]).agg(strings=("raw", "size"),
                                                 applications=("count", "sum"),
                                                 members=("raw", lambda s: ", ".join(sorted(s))))
    sizes = sizes[sizes.strings > 1].sort_values("applications", ascending=False)
    names = movies.set_index("movieId")["title"]
    print("five mergers that absorbed the most applications:")
    for (movie_id, _), row in sizes.head(5).iterrows():
        print(f"  {names.get(movie_id, movie_id)}: {row.applications} applications "
              f"from {row.members}")

    print("== (5) scores.csv ==")
    # A tag the judge asks about by its own name gets the score of the group it merged into.
    asked = asked_pairs()
    g = groups(tags)
    member = clean(tags)
    member["tag"] = member["lower"].str.strip()
    member = member[["movieId", "tag", "key"]].drop_duplicates()
    out = (asked.merge(member, on=["movieId", "tag"], how="left")
           .merge(g[["movieId", "key", "score"]], on=["movieId", "key"], how="left"))
    written = out.dropna(subset=["score"])[["movieId", "tag", "score"]]
    written = written.drop_duplicates(["movieId", "tag"])
    written.to_csv(REPO / "scores.csv", index=False)
    print(f"asked for: {len(asked)} movie-tag pairs over {asked.movieId.nunique()} movies")
    print(f"wrote: {len(written)} rows to scores.csv")

    print("== (6) the four rankings ==")
    # Ties in the judge's and score()'s lists are broken by tag text, as in section (3).
    judge = pd.read_csv(REPO / "judge" / "ratings_movies.csv", keep_default_na=False)
    mine_order = my_order_lines()
    titles = movies.set_index("movieId")["title"]
    for movie_id in ten_movies():
        print(f"\n{titles.get(movie_id, movie_id)}")
        print("  -- the counts --")
        counts = tags[tags.movieId == movie_id]["tag"].value_counts().head(SHOW)
        for tag, n in counts.items():
            print(f"    {n:4d}  {tag}")
        print("  -- my own order --")
        for tag in mine_order.get(movie_id, [])[:SHOW]:
            print(f"    {tag}")
        print("  -- the judge's order --")
        j = judge[judge.id == movie_id].sort_values(["rating", "tag"], ascending=[False, True])
        for row in j.head(SHOW).itertuples():
            print(f"    {row.rating}  {row.tag}")
        print("  -- my score() --")
        sc = scores[scores.movieId == movie_id].sort_values(["score", "tag"],
                                                           ascending=[False, True])
        for row in sc.head(SHOW).itertuples():
            print(f"    {row.score:7.1f}  {row.tag}")


if __name__ == "__main__":
    ratings, tags, movies, links = load_all()
    part2_tags(ratings, tags, movies, links)
