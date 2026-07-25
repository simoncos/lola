# LoLA-2016: A Preserved Ranked League of Legends Match Archive with Timelines and Kill Events

> **WITHDRAWN PENDING PROTOCOL-V2 RERUN (2026-07-20).** The MoA audit found
> material problems in the old kill/assist interpretation, split labels, T3
> estimand, and provenance. Numerical results and publication-readiness claims
> below are retained only as revision history and must not be cited. The active
> protocol is in `BENCHMARKS.md`; remediation status is in
> `../REMEDIATION_STATUS.md`. Raw release is deferred.

*Historical working draft v0 — 2026-07-15.*

---

## Abstract

We are preparing **LoLA-2016**, a curated and pseudonymized archive of **222,652** North
American ranked solo-queue *League of Legends* matches from Pre-Season 2016
(patches 5.21–6.1). Each match carries the full 10-player roster with 40+
end-game statistics per player, four per-minute timeline segments of
gold/experience/creep and lane-differential deltas, and a raw kill stream whose
one-row-per-assist representation is normalized into event and assist-relation
tables with killer, victim, assist, and minute, all champion bans, and — unusually — each player's previous-season
tier (Bronze through Challenger). The window is **no longer recollectable from
Riot's API**: match-v4 was removed in 2021 and match-v5 retains only ~2 years,
so 2016 timeline and kill-event data expired years before the current API
existed. Comparable public archives preserve only end-game summaries for this
era; to our knowledge LoLA-2016 is the only surviving ranked corpus retaining
per-minute timelines and the kill-event stream at this scale with full tier
labels. We document collection, a quality audit (including the crawler's
one-row-per-assist representation), pseudonymization, and licensing, and
we provide an open extraction/validation toolkit, a Datasheet, and three benchmark
tasks with baselines: draft win prediction, early-game win prediction, and
lineup-interaction prediction. LoLA-2016 supports longitudinal
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

1. **The proposed dataset**: cleaned, pseudonymized, columnar (Parquet), with a Datasheet.
2. **A quality audit** on the real database, including provenance-level issues
   (kill/assist row representation, minute-unit durations, absent timestamps) and their
   corrections, so downstream users inherit documented data rather than folklore.
3. **An open toolkit** (`lola_dataset`: validate / stats / export) reproducing
   every number after rerun, plus pseudonymization by keyed hashing.
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
| FrameKillEvent | v2 strict rerun pending | normalized event rows + distinct assist relations |
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

- **Kill/assist representation.** The crawler can write one row per assist, so
  repeated `(match_id, happen, victim)` keys are not automatically duplicate
  kills. The v2 export emits one `kill_events` row per event key plus distinct
  `kill_assists` relations, while strict validation separately reports exact
  duplicates and conflicting payloads. Real-database v2 counts are pending rerun.
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

### 3.4 Pseudonymization and ethics

Summoner names are dropped; summoner IDs are replaced by a 128-bit truncated
HMAC-SHA-256 pseudonym (key withheld). The raw API JSON blob (which contained names) is not
distributed. We describe the result as **pseudonymized and risk-minimized**
rather than anonymous: under GDPR, hashed identifiers remain personal data
while re-linking is theoretically possible. In practice linkability is
unusually low — 2016 identifiers predate Riot's PUUID migration and the source
records have expired from Riot's own retention — but we disclose the
categorization, prohibit re-identification attempts in the terms of use, and
provide a takedown / right-to-be-forgotten contact. The data contains no chat
or user-generated content.

### 3.5 Licensing and recollectability

We license only our curation, schema, and tooling (CC BY-NC 4.0) while
acknowledging that the underlying game data is Riot's intellectual property
(with Riot's standard non-endorsement disclaimer), and we include a
provenance-and-terms note (collected under the then-current API terms; preserved
for non-commercial research; takedown/RTBF contact provided). Prior to public
release we contacted Riot Developer Relations to request permission for the
release [status/outcome to be stated here]; a clause-by-clause compliance
review is maintained in the project repository. On
recollectability: match-v4 was removed from the API in September 2021 and
match-v5 retains roughly two years, so 2016 timeline/kill-event data expired
years before the current API — we substantiate the "cannot be recollected" claim
while scoping it precisely to the timeline+kill-event granularity that community
end-game archives do not preserve.

## 4. Benchmark tasks

> Numerical benchmark results remain pending a protocol-v2 rerun.

All tasks use a canonical duration cohort and three audited settings: a
build-order temporal holdout, an IID mixed-patch hash split, and a genuine
within-build control. Every run emits the exact match-level split manifest and
a provenance manifest; validation selects hyperparameters and test is evaluated
once.

**T1 — Draft win prediction.** Signed one-hot features for the ten champion
picks only. Bans, tier, patch and player history are not silently included.

**T2 — Early-game win prediction.** Team-differential timeline state plus kill
difference and first blood at 10/20 minutes. Champion composition is excluded,
and kills come from the normalized one-row-per-event table.

**T3 — Lineup-interaction prediction.** Compare held-out performance of
regularized champion main effects against main effects plus anti-symmetric
cross-team champion interactions. This measures incremental predictive value,
not causal counter-picks or lane matchups: the 25 cross-team pairs in one match
are correlated views of one team outcome.

## 5. Usage, limitations, maintenance

LoLA-2016 suits longitudinal meta-evolution (as a fixed historical baseline),
skill-conditioned design analysis (via tier labels), balance-structure studies,
and weakly-supervised behavioral work. It is **not** suitable for inferences
about the current game (champions and systems have changed substantially) or for
player-level profiling. Limitations: single region (NA), single patch band, solo
queue (not professional), pre-season (atypical motivation), 128-champion roster,
and tier as a lagged previous-season label. If redistribution is authorized, a
future public version may be archived on Zenodo and mirrored on HuggingFace; no
current DOI or mirror is claimed. Issues and takedown requests are handled via
the project repository.

## 6. Conclusion

LoLA-2016 preserves a slice of ranked *League of Legends* that the game's own
infrastructure can no longer produce, with the skill labels and timeline
granularity that make design- and balance-oriented research possible. We intend
to release it, subject to permission and a completed v2 audit, with reproducible tooling, in the
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
python -m lola_dataset export    --db lola.db --out parquet/ --salt-file SALT_PRIVATE.txt
python -m benchmarks.draft_baseline --parquet parquet/                  # T1
python -m benchmarks.early_game_baseline --parquet parquet/             # T2
python -m benchmarks.matchup_interaction_baseline --parquet parquet/    # T3
```
