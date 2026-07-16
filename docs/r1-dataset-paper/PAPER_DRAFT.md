# LoLA-2016: A Preserved Ranked League of Legends Match Archive with Timelines and Kill Events

*Working draft v0 — 2026-07-15. Numbers from `reports/validate.json`,
`reports/stats.json`, and the `lola_dataset` toolkit. Prose is a first draft.*

---

## Abstract

We release **LoLA-2016**, a curated and anonymized archive of **222,652** North
American ranked solo-queue *League of Legends* matches from Pre-Season 2016
(patches 5.21–6.1). Each match carries the full 10-player roster with 40+
end-game statistics per player, four per-minute timeline segments of
gold/experience/creep and lane-differential deltas, the raw stream of
**13.1 million** (deduplicated) kill events with killer/victim/assist and
timestamp, all champion bans, and — unusually — each player's previous-season
tier (Bronze through Challenger). The window is **no longer recollectable from
Riot's API**: match-v4 was removed in 2021 and match-v5 retains only ~2 years,
so 2016 timeline and kill-event data expired years before the current API
existed. Comparable public archives preserve only end-game summaries for this
era; to our knowledge LoLA-2016 is the only surviving ranked corpus retaining
per-minute timelines and the kill-event stream at this scale with full tier
labels. We document collection, a quality audit (including a 39.5% kill-event
duplication in the raw crawl that we correct), anonymization, and licensing, and
we ship an open extraction/validation toolkit, a Datasheet, and three benchmark
tasks with baselines: draft win prediction, early-game win prediction, and a
champion matchup-structure decomposition. LoLA-2016 supports longitudinal
meta-evolution studies and skill-conditioned design analysis that
esports-only and current-patch datasets cannot.

---

## 1. Introduction

Research on MOBAs — win prediction, draft recommendation, balance, player
modeling — depends on match data, yet the public supply is skewed toward
professional esports (no amateur skill spread) or current patches (no history).
A specific and irreversible gap has opened for *historical* data: because Riot's
API retains only recent matches, the fine-grained telemetry of older patches
cannot be recollected at any price. Datasets that happened to be captured and
preserved are therefore primary sources with a shelf life the community did not
plan for.

LoLA-2016 is one such source: 222,652 ranked solo-queue matches from Pre-Season
2016, captured in 2016 and preserved since. Beyond its scale it has two
properties that current data lacks: a **per-player skill tier** on an amateur
ladder population, and a **frozen, known design window** (the Mastery/keystone
overhaul, marksman-item and jungle reworks) that acts as a natural design shock.
We contribute:

1. **The dataset**: cleaned, anonymized, columnar (Parquet), with a Datasheet.
2. **A quality audit** on the real database, including provenance-level issues
   (kill-event duplication, minute-unit durations, absent timestamps) and their
   corrections, so downstream users inherit documented data rather than folklore.
3. **An open toolkit** (`lola_dataset`: validate / stats / export) reproducing
   every number here, plus anonymization by salted hashing.
4. **Three benchmark tasks with baselines** and fixed, leakage-controlled splits.
5. **An honest treatment of licensing and recollectability**, since Riot-derived
   redistribution and the "irreplaceable" claim both require care.

## 2. Related datasets

Public LoL/MOBA datasets fall into three groups. **Esports** corpora (Oracle's
Elixir, 2014–present; PandaSkill's 2019–2024 pro set, arXiv:2501.10049) are
aggregate, public-figure, and lack amateur skill spread. **Current-patch**
community releases (e.g., GPTilt's HuggingFace event datasets, 2024–25) ship
per-minute events and kill data in Parquet — a similar *content* profile — but
only for present patches and often a single elite tier. **Historical end-game**
dumps (Kaggle `paololol`, 2014–2016) preserve summary stats and bans for our era
but **no per-minute timelines or raw kill events**. StarCraft II dataset papers
(STARDATA, AIIDE 2017; SC2EGSet, *Nature Scientific Data* 2023) and CS:GO's ESTA
(NeurIPS D&B 2022) establish the norms we follow: a datasheet, open tooling,
fixed splits, and a DOI. LoLA-2016's differentiator is not raw content but the
*combination* — timelines + kill events + full tier distribution + bans at
220k-match scale — preserved for a **historical** window that cannot be
recollected.

## 3. Dataset

### 3.1 Contents

| Table | Rows | Content |
|---|---|---|
| Match | 222,652 | patch version, duration (minutes) |
| Participant | 2,226,520 | 40+ end-game stats per player-match |
| ParticipantTimeline | 8,906,080 | 4 segments × per-minute deltas + lane diffs |
| FrameKillEvent | 13,127,488 (deduped) | killer/victim/assist, minute |
| Team / TeamBan | 445,304 / 1,330,757 | objectives, outcome / bans |

128 champions; patches 5.21.0.297, 5.22.x, 5.23.x, 5.24.x, 6.1.0.484. Previous-
season tiers span eight buckets (participant counts: Gold 597k, Silver 523k,
Platinum 446k, Diamond 341k, Unranked 200k, Bronze 65k, Master 42k, Challenger
13k).

### 3.2 Collection

Data was collected in 2016 via the then-current Riot REST API and the Cassiopeia
wrapper. Three seed players at tiers Silver, Challenger, and Diamond were
expanded by snowball sampling their match histories until quotas were reached,
then merged and deduplicated. This yields an active-player-biased, non-uniform
sample of the NA ladder during the pre-season — a scope we state plainly rather
than present as representative.

### 3.3 Quality audit

Running the `lola_dataset validate` toolkit on the 3.5 GB source database:
integrity is high — zero orphan records, and every match has exactly 10
participants, 2 teams, and a single winner. Three provenance issues are
documented and handled:

- **Kill-event duplication.** The raw crawl wrote 21,692,852 kill-event rows, of
  which **39.5%** are duplicates under the `(match_id, happen, victim)` key
  (the original analysis deduplicated by database row order, an unsafe proxy);
  we deduplicate to 13,127,488.
- **Duration units.** `duration` is stored in **minutes** (range 7–87), and the
  era predates the remake system; we flag sub-10-minute games rather than treat
  them as remakes.
- **No timestamp column.** The 2016 schema stores no match timestamp; we use
  build version plus monotonically increasing `match_id` as a chronological
  proxy, and document it.

Descriptively, blue-side win rate is 50.6% (the known slight blue advantage of
the era — a sanity signal), match duration peaks at 30–35 minutes, kill volume
peaks at 20–25 minutes, and the most-picked champions (Lucian 70,555; Lee Sin
69,697; Vayne 64,266) match the 2016 meta. The matches-per-player distribution
is right-skewed (median 2, p90 9, p99 37); 13,272 players have ≥20 games,
enough for player-sequence studies on that subset.

### 3.4 Anonymization and ethics

Summoner names are dropped; summoner IDs are replaced by a salted SHA-256 hash
(salt withheld). The raw API JSON blob (which contained names) is not
distributed. 2016 identifiers predate Riot's PUUID migration and are no longer
resolvable, so re-identification risk is low; we disclose this rather than claim
exemption. The data contains no chat or user-generated content.

### 3.5 Licensing and recollectability

We release our aggregation and schema under CC BY 4.0 while acknowledging the
underlying game data is Riot's intellectual property, and we include a
provenance-and-terms note (collected under the then-current API terms; preserved
for non-commercial research; takedown/RTBF contact provided). On
recollectability: match-v4 was removed from the API in September 2021 and
match-v5 retains roughly two years, so 2016 timeline/kill-event data expired
years before the current API — we substantiate the "cannot be recollected" claim
while scoping it precisely to the timeline+kill-event granularity that community
end-game archives do not preserve.

## 4. Benchmark tasks

All tasks use a chronological, leakage-controlled split (train on builds up to
5.24.0.254, validate on the first 20% of 5.24.0.256 by match_id, test on the
remainder plus 5.24.0.259 and 6.1.0.484), with a same-patch random split as a
control. Matches under 10 minutes are excluded.

**T1 — Draft win prediction.** From the 10 champions and bans, predict the
winner. Signed champion one-hot with logistic regression reaches 54.7%
cross-patch / 55.5% same-patch accuracy (majority 50.6%), matching the
literature's ~55% draft-only ceiling; we also report AUC, log-loss, and expected
calibration error (rarely reported in this literature), and observe that
cross-patch drift roughly triples calibration error.

**T2 — Early-game win prediction.** From the first 10 (and 20) minutes of
timeline deltas plus kill aggregates, predict the winner. (Baselines: logistic
regression / gradient boosting; reference target ~70–75% at 10 minutes.)

**T3 — Matchup-structure decomposition.** From per-(patch, tier) champion win
matrices, decompose pairwise win log-odds into a transitive strength rating and
a cyclic (counter-pick) residual via weighted HodgeRank. We provide this as an
analysis benchmark: on LoLA-2016 the genuine cyclic share is ~5% after
permutation-null correction, stable across tiers and patches — demonstrating the
dataset supports balance-structure research, not only prediction.

## 5. Usage, limitations, maintenance

LoLA-2016 suits longitudinal meta-evolution (as a fixed historical baseline),
skill-conditioned design analysis (via tier labels), balance-structure studies,
and weakly-supervised behavioral work. It is **not** suitable for inferences
about the current game (champions and systems have changed substantially) or for
player-level profiling. Limitations: single region (NA), single patch band, solo
queue (not professional), pre-season (atypical motivation), 128-champion roster,
and tier as a lagged previous-season label. The dataset is versioned on Zenodo
(DOI) with a mirror on HuggingFace; issues and takedown requests are handled via
the project repository.

## 6. Conclusion

LoLA-2016 preserves a slice of ranked *League of Legends* that the game's own
infrastructure can no longer produce, with the skill labels and timeline
granularity that make design- and balance-oriented research possible. We release
it with a documented quality audit, reproducible tooling, and benchmarks, in the
hope that "the data expired" becomes a less common obstacle to studying how these
games — and their players — actually behaved.

## References (to verify/format at submission)

- Lin, Gehring, Khalidov, Synnaeve. STARDATA. AIIDE 2017; arXiv:1708.02139.
- Białecki et al. SC2EGSet. Nature Scientific Data, 2023.
- Xenopoulos, Silva. ESTA. NeurIPS Datasets & Benchmarks 2022; arXiv:2209.09861.
- Le Guen et al. PandaSkill. arXiv:2501.10049; IEEE ToG 2025.
- Gebru et al. Datasheets for Datasets. CACM 2021.
- Riot Games. Match History Retention Change; API change log (match-v4 removal).
- He, Tran, Jiang, Burghardt, Ferrara, Zheleva, Lerman. Heterogeneous Effects of
  Software Patches in a MOBA. FDG 2021; arXiv:2110.14632.
- Companion: "Mastery and Mistrust" (design analysis on LoLA-2016).

## Appendix: reproduction

```bash
pip install -r lola_dataset/requirements.txt
python -m lola_dataset validate --db lola.db --out reports/validate.json
python -m lola_dataset stats    --db lola.db --out reports/stats.json
python -m lola_dataset export    --db lola.db --out parquet/ --salt <secret>
python benchmarks/draft_baseline.py --parquet parquet/       # T1
python analysis/matchup_structure.py --parquet parquet/      # T3
```
