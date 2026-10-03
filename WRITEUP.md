# HW1 writeup

**Name:** Claire Kuno
**Date:** 2026-09-17

Every placeholder below gets your answer, told to Claude or typed in here yourself. Every number
you give comes from a script in this repo; say which one. Claude may format tables and figures
here; the words are yours.

## Part 0. Predictions

Give these to Claude before any analysis runs. One sentence each, plus one sentence on why you
think so.

**(1) A movie you know well, and what its three most-used tags will be:** Dirty Dancing and its tags would be dance, romance, and music.

**(1) Why you think so:** The movie is about a romance between Baby, a wealthy girl on vacation with her family, and Johnny, her dance instructor at the vacation resort. Their relationship grows through their many shared dances paired with a wonderful soundtrack.

**(2) Out of every 100 people who rated movies here, how many ever added a tag?** 15

**(2) Why you think so:** I think it would be a small number of people, and I would only except real cinephiles to rate a movie. But, the site is for people who like movies. So, I would say between 10 and 20 percent.

**(3) Can one person's tags take over a movie's tag list? Yes or no:** Yes

**(3) Why you think so:** I think if they use words that are commonly used across multiple movies. A rare tag would not be too helpful in cross checking themes to build a recommendation.

## Part 1. Whose data is this?

Code: `part1_data.py`.

**My rule for cutting 32 million ratings to 5 million** (written before reading `data/make_compact.py`)**:** Keep movies with at least 20 ratings, users with at least 20 ratings, and movies with at least 20 tags.

**One rule I considered and rejected, and why:** I considered making the rule a threshold higher, or adding the number of ratings per user. But, we can assume empty ratings with enough data from other users. So, I left it out.

**One interesting thing from `data/README.md`:** One interesting thing from data/README.md, was the fact that the density of the ratings for movies in the dataset sounds very small at 0.19%. It goes to show how recommendation systems do not have a lot of information to work with.

**How the script's rule differs from mine, and what each keeps that the other drops:** The script's rule differs from my slot by focusing on user eligibility instead of density of ratings per movie. I think it does a good job at checking eligible tags per movie.

**First check. Which of Claude's numbers, the different route you took, and whether it matched** (one good target: 6 tags are the literal text `NA`, which pandas drops unless told not to)**:** The first of the 'two checks' automatically drops NAs with pandas, so the number of tags under the literal name 'NA' were found using helpers. The second route opens data/tags.csv.gz directly and counts and sums the tags 'NA'. Both routes produced the same result.

**Second check. Which of Claude's numbers, the different route you took, and whether it matched:** The number was 15.625% consistent across both checks. The first route takes the length of ratings and divides it by the number of all ratings in MovieLens. The second route directly opens data/ratings.csv.gz and manually sums up the number of rows in ratings. Then, it divides it by 32000204. It also checks to ensure that len(ratings) is the same number as the manual count. So, it produces the same result.

## Part 2. What tags best describe a movie?

Code: `part2_tags.py`.

**My movie, and why I picked it:** Dirty Dancing. I chose this movie because it is a favorite of mine.

**Its most misleading tag in the count-ordered list, and why it misleads:** '80's classic' is not wrong, but it could be misleading as this tag alludes to its release in the 1980s. But, the movie is set to take place in 1963.

**What I learned about how MovieLens collects ratings and tags, from rating and tagging my movie myself (about 100 words):** I learned that MovieLens collects ratings and tags from user-based input. It doesn't check whether the given tags are misleading, it trusts its users. I have gone on the actual site to view how the tags are displayed to allow a user to filter through to what kinds of movies they are interested in. I have learned that tags exist in phrases, not only single adjectives.

### Up close

One sentence on the figure written before you saw it and one after. The two tables are where the
details below come from. Say which script made them.

**The figure, when the tags and the ratings arrived. What I expected:** I honestly think month would not matter for Dirty Dancing because its not related to seasons, maybe a spike in the summer time because it takes place in the summer?
**The figure, what it shows:** The figure shows the spread of user ratings compared to user tags for the movie Dirty Dancing. With the timespan on the x, we can see the yearly progression (decipherable as months) of ratings and tags. The figure hows significant increase in tags throughout the years over ratings. It goes to show that users are favoring tagging over rating.

**Two interesting details I learned up close that the counts did not show:** One interesting detail I learned is that taggers generally rate the movie higher than the mean. It goes to show that interest plays a large role in user interaction. Another interesting detail was from the tag 'cheesy'. It showed a low tagger mean of 2.11 and everyone else 3.19. This goes to reveal how some taggers are interacting with a movie they did not find interesting, perhaps to better the recommendations they receive going forward.

**Anything up close that contradicted something I had already written down. Which one, what the data showed, and what you now think. Or "nothing yet":** I think attributing a movie to a time period is tricky when you are trying to compare when it was released, when it was popular, or when the movie takes place. I find contradictions in my own rankings of the tags as I put 1960s at the very bottom (when the movie takes place) versus the 80s (when the movie came up and was perceived to be popular).

### My definition

**My `score(movie, tag)`** (one or two sentences, precise enough that a classmate could code it)**:** It does the most work by merging words that begin with the same four letters. It ensures that there are no duplicates of the same word like dance and dancing.

**One definition I considered and rejected, and why:** One definition I considered was to just look at popularity. I think my original goal of finding distinct tags was to choose tags that were descriptions of the movie. I wanted to avoid names falling to the top of the list, or scene specific tag applications. I realized that there were some descriptions such as 'dark comedy' for Fargo that incoporated multiple words that captured a good sense of the movie, so I adapted my prompts.

**Which tags I merged as the same tag, which I kept apart, and why:** I would merge tags such as dance and dancing, because they mean the same thing. I would choose the shorter of each. So, if tags have the same four letters to begin with, I would merge them. Make sure capital and lowercase letters count as the same. When two tags merge, it should keep the count of the shorter tag. For a tag with fewer than four letters, it would not be considered in the merge, but stay with its original tag popularity count and considered to win. It would remain as a contender for 'best' tag, it would keep its original tag count. The tag with the shortest length will be the only one that remains. Its score would remain the count for the shortest tag. It will take the average tag count of the two and keep it in lowercase format. It should keep whichever one is more popular in tag count. I like the concept of the four-letter merge because it reduces redundancy in the tags. I find it to better produce an encompassing result of a list for tags.

**Why my definition, in about 150 words. Name one thing it gains and one thing it loses:**

My definition gains the benefit of reducing redundancy and highlighting popularity. It may lose generalization of the movie's feeling with tags that are specific to movie release or famous actors.

### The judge

The two slots below are read by scripts, so write them as bare lines: one item to a line, the
movieId first, no bullets and no numbering. A movie line looks like `296, Pulp Fiction (1994)`.
An order line looks like `296: nonlinear, hit men, dark comedy, ...`, the tags best first.

**My ten movies:**

1088, Dirty Dancing (1987)
60397, Mamma Mia! (2008)
593, Silence of the Lambs, The (1991)
608, Fargo (1996)
6377, Finding Nemo (2003)
1201, Good, the Bad and the Ugly, The (Buono, il brutto, il cattivo, Il) (1966)
6539, Pirates of the Caribbean: The Curse of the Black Pearl (2003)
194448, Green Book (2018)
4262, Scarface (1983)
6711, Lost in Translation (2003)

**My own order of the ten most-used tags, written before looking at any data: my movie from step 1, then my nine others from step 4:**

1088: 80's classic, dancing, dance, romance, Patrick Swayze, music, cheesy, teen movie, coming of age, 1960s
60397: musical, Musical, ABBA, Greece, Meryl Streep, Amanda Seyfried, Colin Firth, Pierce Brosnan, Island, music:ABBA
593: disturbing, cannibalism, suspense, psychology, psychological, serial killer, Jodie Foster, Anthony Hopkins, great acting, excellent script
608: crime, quirky, Frances McDormand, Steve Buscemi, dark comedy, dark humor, strong female, Coen Brothers, witty, black comedy
6377: animation, heartwarming, Disney, funny, Pixar, father-son relationship, underwater, ocean, short-term memory loss, talking animals
1201: western, classic, spaghetti western, Clint Eastwood, music, epic, Sergio Leone, Ennio Morricone, complex characters, atmospheric
6539: pirates, adventure, funny, treasure, action, johnny depp, Johnny Depp, comedy, fantasy, sword fight
194448: touching, friendship, heartwarming, segregation, musician, racism, social commentary, Viggo Mortensen, great acting, based on a true story
4262: mafia, gangsters, crime, drugs, violence, Al Pacino, atmospheric, organized crime, corruption, classic
6711: bittersweet, loneliness, Melancholic, Japan, Scarlett Johansson, Bill Murray, atmospheric, reflective, complex characters, visually appealing

**One criterion I considered for the judge and rejected, and why** (the one I used is in `judge/criterion.md`)**:** One criterion I reject is taking out descriptions of tags that contain more than one word. Because some tags include phrases that help the user contextualize plot.

**Agreement. The number `agreement.py` gives for your `score()`, for popularity and for your own order, and which of the three came closest to the judge:** The score() was 2.19, the popularity was 2.17, my own order was 1.9, and the best possible was 3.92. The best possible ranking was a 3.92 meaning that for each movie, that is the highest score a movie could get based on the judge's ratings. Out of the three, my score() came closest to the judge.

**How the judge skill is built: the files it is made of and what each one does (about 150 words):**

The judge skill seems to be built off of my inputs on this homework. It is curated to speak through a facilitator (directed through SKILL.md, system.md, criterion.md, and judge.py) to create outputs that get written into ratings_movies.csv. It gives me an interpretation of what my words direct into Claude.

**What happens when I run `/judge`, from the first check to the CSV (about 150 words):**

The first check to the csv uses criterion.md to rate movies in movies.csv. Then, it rolls through the 110 movies and forms ratings from 1-5 on each tag rating, holding it in ratings_movies.csv. It ensures that no movies or tags come up short.

**Why a skill: what a skill like this gives you that a script or a prompt alone does not, and where you would use one next (about 100 words):**

The skill ensures that the judge stays in line of the prompts I feed into criterion.md. It makes sure that the judge produces an output that fall under the expectations of the README.md and system.md. I would use a skill like this when I am trying to produce a system that will be used by other people's inputs. I think it tests the prompts and code under different user directions making it foolproof.

### The viewer and the disagreements

**One thing `movie_results.html` showed me that was useful, and one thing about it that got in my way:** I found the comparison table of my scores and the judge's score super helpful as it helped me see differences in our methods. But, I thought having all of the tags displayed was unnecessary.

Then three improvements. For each: what the page would not let you see, what you had Claude
change, and what the changed page shows that the first draft did not.

**Improvement 1:** The page wouldn't let me see comparisons across the list. So, I had it change the layout of how the terms were displayed to be side by side. The changed page shows the lists side by side.

**Improvement 2:** The page wouldn't let me see only the important information by putting in long lists of all of the data. I had them change this by deleting it fully. The changes made it so that the page was easier to navigate.

**Improvement 3:** The page doesn't show direct comparisons across all of the lists. I asked it to highlight terms that matched across all the lists. It made it nice to see how the different lists ranked the same tags.

Then the three disagreements. A disagreement is a movie and a tag where your `score()` and the
judge are furthest apart. For each: the movie and the tag, where your `score()` put it and where
the judge put it, and what you think accounts for the gap.

**Disagreement 1:** I disagree with Dirty Dancing's music tag. My score put the tag 1, while the judge put it at 15. The judge's list accounts for this with 'great soundtrack' scoring highly.

**Disagreement 2:** I disagree with Silence of the Lambs 'investigation' tag. My score put it at 11 while the judge put it at 51. Nothing accounts to cover the plot of this movie. But, other tags like 'disturbing' or 'suspense' make up for it.

**Disagreement 3:** In Fargo, 'loneliness' is ranked 31st on my score while the judge ranked it 4th. I think this tag is not very encompassing of the themes in the movie and you can see it's unpopularity in the count score.

**One other high-level pattern in the results, and what you think is behind it:** A pattern I see is that at least two tags appear to be common among the top 10 across all the generated lists. I think behind it is the popularity, or count of each tag and that ensures that those terms stay in higher ranks.

## Predictions revisited

**Which of my three predictions were wrong, and what I make of each miss:** Honestly, my predictions were wrong with the data being well dispersed across user inputs. But, I think it is interesting that there are 772 movies where one person made more than half of the tag applications. I am assuming it comes from unpopular movies. This data comes from part1_data.py.

## Part 3. What tags best describe a user?

Code: `part3_users.py`.

The slot below is read by a script, so write it as bare lines: one rating to a line, no bullets
and no numbering, the movieId first and the rating last, as in `296, Pulp Fiction (1994), 4.5`.

**My 20 ratings:**

1088, Dirty Dancing (1987), 5.0
60397, Mamma Mia! (2008), 5.0
593, Silence of the Lambs, The (1991), 5.0
608, Fargo (1996), 5.0
6377, Finding Nemo (2003), 4.0
1201, Good, the Bad and the Ugly, The (Buono, il brutto, il cattivo, Il) (1966), 4.0
6539, Pirates of the Caribbean: The Curse of the Black Pearl (2003), 5.0
194448, Green Book (2018), 5.0
4262, Scarface (1983), 5.0
6711, Lost in Translation (2003), 4.0
2628, Star Wars: Episode I - The Phantom Menace (1999), 5.0
5378, Star Wars: Episode II - Attack of the Clones (2002), 5.0
33493, Star Wars: Episode III - Revenge of the Sith (2005), 5.0
260, Star Wars: Episode IV - A New Hope (1977), 5.0
1196, Star Wars: Episode V - The Empire Strikes Back (1980), 5.0
1210, Star Wars: Episode VI - Return of the Jedi (1983), 5.0
122886, Star Wars: Episode VII - The Force Awakens (2015), 5.0
179819, Star Wars: The Last Jedi (2017), 5.0
208205, Star Wars: The Rise of Skywalker (2019), 5.0
1197, Princess Bride, The (1987), 5.0

**My `score(user, tag)`, in a sentence, and why I started there (about 100 words):**

My score looks at other users compared to me and finds similar users based on raw ratings of other movies. The score is computed for one person against everyone instead of all users against each other. It counts each person once per tag (lowercased and merged to avoid redundancy) and weighs how similar they are to me. I picked it because I am looking for tags that are personalized.

**What my score says about me: my top ten tags, and whether they describe my taste (about 100 words):**

| tag | score |
| --- | --- |
| sci-fi | 242.98 |
| great soundtrack | 237.74 |
| dark comedy | 231.56 |
| visually appealing | 196.01 |
| psychology | 193.43 |
| space | 189.79 |
| action | 186.32 |
| atmospheric | 184.50 |
| twist ending | 180.41 |
| classic | 173.42 |

Source: `part3_users.py`, section (2).

It makes sense because I put in all of the Star Wars movies. Yes, it describes the taste of the twenty movies I inputted. It makes sense to me. They capture the dark, sci-fi themes of a lot of the majority of my movies.

**What my user viewer shows and why I chose that (about 100 words):**

My viewer shows my tags side by side next to the top ten tags by users across all people. I chose it to see how cosine similarity could show up or influence my tags. I chose that to show how my taste differs from the top tagged tags, but not super. I think it captures how a lot of the movies I mentioned were action movies. But, my list and my judge's recommended list reveals the diversity in movie genre (ie. romance).

**What I put in the description column for a person, and why (about 150 words):**

The description contains the label, movies, stars, and tags per user. I chose the description I gave the judge because I wanted it to prioritize the conciseness I was aiming for in my results while also considering tag counts to make the list feel recognizable to the tags I saw from all of the movies.

**My criterion for people: what it asks the judge to do that the movie criterion did not (about 60 words):**

My criterion for people asks the judge to make concise labels and to be aware of rare tags and adjectives. My movies criterion just looked for conciseness and capturing the movie's feelings.

**The user-tag pairs I chose to judge, how many, and why those (about 100 words):**

I chose those people to provide a contrast of similar users and to also make the scope of users smaller by asking to look for tags applied by more than 30 people. My file has 41 people who are grouped into a similar userbase and a dissimilar user base. My 46 tags are chosen by whether 30 or more people picked them and to include tags across at least 10 of my twenty movies. The combination created 1886 pairs.

**Improvement 1: what I changed in the scoring function, what the judge and the viewer showed before and after (about 150 words):**

I changed the criterion on how many tags my score() looks at to matched the pool of tags the judge was looking at. It changed my score() to better reflect the diversity of movie tags, instead of just looking at Star Wars.

**Improvement 2: the same (about 150 words):**

I changed the merge rule by adding things like 'great soundtrack' and music to go together, or classic and cult film. This opens up space for a more larger variety of tag applications. It changed my list to include some that are on the judge's list. It made it feel closer to the judge's list by adding violence and adventure to the mix.

## Part 4. Working with Claude

Give these to Claude the way you gave it the rest. Graded on the catch and the candor, not on
making Claude look good or bad.

**A moment where Claude was wrong or overconfident, how you caught it, and where it
happened. Name the part and the step, so the moment can be found:** I caught it when it was suggesting things for me to input as criterion in the terminal. It was not a bad suggestion, but I feel like that was thinking I could have done on my part. Part 3, the criterion_users.md step!

**One call where you overrode Claude, and why:** There were many points where I seem to have misunderstood what variables I was working with. Claude told me this: Part 3, the description slot. Claude said the descriptions contain no tag counts. I kept "considering tag counts." I misunderstood the description label.

**What you would hand to Claude sooner next time:** I would hand over to Claude understanding the makeup of the different variables the judge looked at versus my own wranglings (my score()) and such.

**Did Claude name the misleading tag in Part 2 step 1 before you did? What happened:** No, I realized that Dirty Dancing is released in the 80s, but takes place in the 60s which makes it misleading.

**The figure. Would asking Claude "what does this show?" have produced your sentence, and what
would have been missing from it:** No, asking you have not produced that sentence. It would have missed the fact that months and years were displayed in a confusing way where it was tagged by year, but the variable was named months.

**Hours spent:** About 10 hours

**Anyone who helped you, or "no one":** No one
