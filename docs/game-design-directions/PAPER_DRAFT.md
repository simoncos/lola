# Mastery and Mistrust: Skill Reward, Mechanical Difficulty, and Perceived Imbalance in League of Legends

*Working draft v0 — 2026-07-15. All numbers from `analysis/design_*.py` on the
LoLA-2016 corpus. Prose is a first draft for iteration, not final copy.*

---

## Abstract

Game designers speak of champions that "reward mastery" and champions that are
"unfun to play against," but these design properties are rarely measured, and
when they are, they are measured casually — typically as win rate against player
rank. Using a preserved archive of 222,652 ranked *League of Legends* matches
from Pre-Season 2016 (patches 5.21–6.1), unusual for carrying a per-player
skill tier on an amateur solo-queue population, we ask two design questions and
find that the obvious measurements mislead. First, we show that *skill
expression* has at least three non-coinciding operationalizations — win-rate
slope across tiers, individual skill-to-lead amplification, and Riot's own
mechanical-difficulty label — and that they are mutually uncorrelated
(pairwise Spearman ≤ 0.19). The popular win-rate-vs-rank measure is the weakest:
matchmaking compresses win rate toward 0.5 and champion pick populations are
self-selected across tiers. Using a leave-one-out, role-stratified amplification
measure that conditions on each player's own demonstrated skill, we obtain a
face-valid per-role skill-reward ranking — and show that it is *dissociated*
from mechanical difficulty (position-controlled partial Spearman −0.03):
snowball and sustain champions reward skill without being mechanically complex,
while some complex champions do not reward it in resources. Second, we treat
1.33M bans as a revealed signal of *perceived* imbalance and find it separates
from *actual* power: several champions are banned far more than their win rate
warrants ("anti-fun": Yasuo, Illaoi, Jax, Dr. Mundo, stable across all tiers),
while strong champions go unbanned ("sleepers": Janna, Amumu, Malzahar). A
positive association between mastery reward and being banned-as-unfair at high
tier appears with one skill measure (Spearman 0.18) but does not survive the
role-stratified measure; we report it as exploratory.
We argue that skill *reward*, mechanical *difficulty*, and perceived *fairness*
are three separable design axes that popular metrics conflate, and we release
the code and (anonymized) data.

---

## 1. Introduction

Competitive game balance is usually studied as prediction (who will win) or
recommendation (what to pick). Designers, however, reason in terms of *design
properties* of individual champions: Does this champion reward the effort of
mastering it? Is it oppressive or unfun to play against? Riot Games' own public
design writing operationalizes "perceived vs. actual power" and assigns each
champion a mechanical-difficulty rating, but the academic literature has largely
left these designer-facing constructs unmeasured on public data, in part because
the data that would support them — a large amateur population labeled by skill —
is rarely available.

We use a corpus with exactly that property: 222,652 North American ranked
solo-queue matches from Pre-Season 2016, in which every participant carries a
previous-season tier (Bronze through Challenger). Two design questions organize
the paper:

- **RQ1 (skill reward).** Which champions convert player skill into in-game
  advantage, and does this "mastery reward" coincide with mechanical difficulty?
- **RQ2 (perceived imbalance).** Do players ban the champions that are actually
  strong, or the ones that *feel* unfair — and does that perception shift with
  skill?

Our contributions are:

1. **A measurement critique.** We show that three natural operationalizations of
   "skill expression" — win-rate slope vs. tier, individual skill-to-lead
   amplification, and Riot's mechanical-difficulty label — are mutually
   uncorrelated. The most common one (win rate vs. rank, used by community
   analytics) is confounded by matchmaking compression and cross-tier player
   self-selection, and should not be used as a skill-reward measure.
2. **A dissociation.** With a confound-controlled, role-stratified amplification
   measure, skill *reward* and mechanical *difficulty* are separable design axes
   (partial Spearman −0.03): snowball/sustain champions reward skill at low
   mechanical difficulty; some high-difficulty champions do not reward it.
3. **Perceived vs. actual imbalance.** Bans separate from win rate; we identify
   stable "anti-fun" and "sleeper" champions and show mastery-rewarding
   champions skew anti-fun at high tier (weak but significant).
4. **A reproducible pipeline** on a preserved, non-recollectable historical
   patch window, released with code and anonymized data.

## 2. Related Work

**Skill and player modeling in MOBAs.** Skill-rating systems (TrueSkill 2
[Minka et al. 2018]; PandaSkill [arXiv:2501.10049, IEEE ToG 2025]) rate *players*,
not champions-as-designed-objects. Work on player generality and proficiency —
the proficiency–congruency dilemma [Kim et al., CHI 2016; arXiv:1512.08321] and
play-style flexibility [arXiv:2402.05865] — studies how players' skill and
versatility relate to outcome, but does not measure the champion as the unit
whose skill-reward is at issue. Per-champion "mastery curves" exist only as
industry analytics (e.g., itero.gg), computed from champion-mastery points and
win rate rather than a skill-labeled population, and not validated as a design
measure.

**Intransitivity and the limits of win rate.** Chen & Joachims' blade-chest
model [WSDM 2016] found that in team games (Dota 2, StarCraft II) intransitive
matchup structure adds little over an additive strength term — team format
"smooths out" low-level interactions. Sanjaya et al. [Algorithms 2022] measure
non-transitivity in chess *as a function of skill*, finding it peaks in mid-Elo
bands; our skill-conditioned view of champion design is analogous but concerns
skill-reward rather than intransitivity. These motivate treating win rate as a
compressed, skill-dependent signal.

**Balance as a design argument from telemetry.** Li et al. [IEEE TVCG 2017]
diagnose snowball/comeback drivers for designers; "Beyond Win Rates"
[arXiv:2502.01250] clusters latent character roles in Valorant to argue about
balance beyond aggregate rates; Data Cracker [Medler et al., CHI 2011] is the
canonical telemetry-as-design-instrument case. He et al. [FDG 2021] estimate
causal patch effects in LoL. Riot's /dev "Champion Balance Framework" (2019)
frames perceived vs. actual power (the "Sleeper Zone"). The DiGRA 2024 study of
predictability and player agency theorizes counterplay conceptually. To our
knowledge no peer-reviewed work operationalizes per-champion skill-reward on a
skill-labeled amateur population, or decomposes bans into perceived-vs-actual
imbalance resolved by tier.

## 3. Data

The LoLA-2016 corpus (companion dataset paper, [R1]) comprises 222,652 NA
`RANKED_SOLO_5x5` matches from patches 5.21–6.1 (Pre-Season 2016), with
2,226,520 participant records (40+ end-game stats each), 8.9M per-minute
timeline segments (gold/xp/cs and lane-differential deltas), 13.1M deduplicated
kill events, 1.33M bans, and each player's previous-season tier across eight
buckets (Unranked, Bronze→Challenger). 128 champions. The window is a frozen
historical patch band no longer recollectable from Riot's API. We exclude
matches under 10 minutes and, for skill measures, players with fewer than 15
games and champion cells with fewer than 3 games. Positions (top/jungle/mid/
adc/support) are assigned from the timeline `lane`/`role` fields, which map
cleanly to the five canonical positions for ~96% of participants.

Riot mechanical-difficulty labels are the Data Dragon `info.difficulty` integer
(1–10); 21 champions reworked after early 2016 are flagged lower-confidence and
robustness is reported with them excluded.

## 4. Measuring skill expression, three ways

**(a) Win rate vs. tier (P0).** For each champion we fit a weighted least-squares
slope of win rate against ordinal tier. This is the community-analytics measure.
Champions with the steepest positive slopes are Nidalee (+0.020 win rate per
tier step), Nunu, Kindred, Lulu, and Talon; the steepest negative slopes are
Zyra (−0.019), Illaoi, Amumu, and Warwick. The signs are face-valid (mechanical
junglers/assassins reward tier; simple low-elo-strong champions decline), but
two problems undermine the measure: matchmaking pulls win rate toward 0.5,
compressing the signal, and the population piloting a champion differs by tier
(self-selection).

**(b) Individual skill amplification (P1).** To condition on skill without the
tier proxy, we measure, for each champion C, the weighted slope of a player's
performance *on* C against that player's leave-one-out baseline on their *other*
champions. A champion "rewards mastery" if generally-skilled players overperform
on it beyond their baseline. Using early-game lane dominance (cs- plus
xp-differential per minute) as the performance metric — far less
matchmaking-compressed than win rate — the top amplifiers are Lissandra, Viktor,
Rek'Sai, Nidalee, Jax, and Azir; the bottom are Soraka, Leona, Karma, and
Draven.

Crucially, this individual-skill measure correlates **near zero** with the
win-rate-vs-tier measure (Spearman 0.04 on win, −0.01 on lane dominance; n=123;
Fig. 1). Even holding the metric fixed at win rate, the two disagree. The two
axes — "does this champion's *population* win more at higher tiers" versus "does
an *individual's* skill convert to extra performance on it" — are not the same
construct, and the win-rate-vs-tier measure is the confounded one.

**(c) Role-stratified amplification and Riot difficulty (P2.5).** The lane-diff
amplification is role-sensitive: junglers (whose lane differential is measured
against the enemy jungler) score systematically high, and supports do not farm.
We remove this by z-scoring lane dominance *within position* before measuring
amplification, so each champion is compared to same-position peers. The
within-role rankings are face-valid: mid amplifiers are Lissandra, Viktor,
Xerath, Kassadin, Azir, and LeBlanc; jungle amplifiers are Rek'Sai, Nunu,
Nidalee, and Elise; top amplifiers are Jax, Cho'Gath, and Dr. Mundo.

## 5. Skill reward is not mechanical difficulty

The role-stratified amplification remains **uncorrelated with Riot's
mechanical-difficulty label** (Fig. 2): overall Spearman 0.04 (0.07 excluding
reworked champions), position-controlled partial correlation −0.03, and
per-position correlations all near zero (top −0.02, mid 0.02, adc 0.01, jungle
−0.03, support −0.23). This is not a role artifact — stratification does not
rescue it.

The dissociation is interpretable. The amplification measure rewards champions
whose extra skill converts into resource leads: this includes mechanically
complex mages (Azir, LeBlanc; Riot difficulty 9) *and* snowball/sustain
bruisers whose farming leads compound (Jax difficulty 5, Cho'Gath 5, Dr. Mundo
5, Maokai 3). Conversely, several high-difficulty champions (Bard 9, Fiddlesticks
9, Shaco 9 — supports and roamers) do not amplify lane resources at all.
"Hard to execute" and "rewards being executed well" are different properties of
a champion's design, and a single "difficulty" label conflates them.

## 6. Bans as perceived imbalance

We treat each champion's ban rate as a revealed signal of *perceived* threat and
its win rate as a proxy for *actual* power; bans in this era are team-global (not
role-slotted), so raw ban rate is unbiased. Standardizing both and taking the
gap (ban_z − win_z) sorts champions into quadrants (Fig. 3): overpowered (strong
and banned), anti-fun (banned but not strong), sleeper (strong but unbanned),
fair. Overall counts are 18 overpowered, 8 anti-fun, 44 sleeper, 58 fair.

The **anti-fun** champions — banned far beyond what their win rate warrants — are
Yasuo, Illaoi, Tahm Kench, and Darius; Yasuo is the textbook case, banned for
being unpleasant to play against despite a sub-50% win rate. The **sleepers** —
strong but rarely banned — are enchanters and simple champions: Janna, Amumu,
Malzahar, Sona. This is direct evidence that *anti-fun ≠ overpowered*: what
players ban encodes frustration, not just power.

Resolving by tier, the perceived-imbalance signal is fairly stable but drifts
across the skill range (Spearman 0.86 low–mid, 0.75 mid–high, 0.58 low–high).
Yasuo, Illaoi, Jax, and Dr. Mundo are anti-fun at every tier; Tahm Kench peaks
at high tier; Kindred becomes anti-fun *only* at high tier.

**RQ3 (do mastery-rewarding champions read as unfair?).** Correlating the P1
skill amplification with the high-tier perceived-imbalance gap yields Spearman
0.18 (95% CI [0.00, 0.34], n=123; Fig. 4). However, the association is **not
robust**: with the role-stratified amplification (our more trustworthy measure)
it drops to 0.14 with a CI that includes zero ([−0.04, 0.32], n=124), and
within-position correlations are heterogeneous (top +0.32, adc +0.37, mid
+0.08, jungle −0.14, support −0.23; small per-position n). We therefore report
RQ3 as exploratory only: the pattern is visible in anecdotes (Kindred turns
anti-fun only at high tier) and in lane roles, but does not survive as a
general effect. Establishing or refuting it likely needs positional ban data
from a later era.

## 7. Discussion

Three designer-facing properties that intuition and even Riot's own tools tend to
run together — how much a champion *rewards* skill, how *hard* it is to execute,
and how *fair* it feels — come apart empirically. Skill reward is measurable but
is mis-measured by the popular win-rate-vs-rank curve; it is distinct from
mechanical difficulty; and neither predicts the perceived-fairness signal in
bans. For design practice this suggests that "difficulty," "power," and
"counterplay/fairness" should be tuned and communicated as separate axes: a
champion can be simple yet high-reward (snowball bruisers), complex yet
low-reward, strong yet unbanned, or weak yet reviled.

The frozen 2016 window is both a limitation and an asset: it captures a specific,
now-obsolete ruleset (pre-objective-bounty, post-Mastery-overhaul), making the
measurements a clean historical baseline rather than a claim about the current
game.

## 8. Limitations

Win rate is matchmaking-compressed, which is conservative for the ban gap but
weak for skill measures (hence the amplification approach). The amplification
measure captures lane-resource conversion, not teamfighting or macro skill, and
support skill in particular is poorly captured by farm differentials. Previous-
season tier is a coarse, lagged skill label. Bans conflate perceived power with
meta/streamer effects and are only a proxy for "unfun." Riot difficulty labels
are current values; 21 reworked champions are lower-confidence (robustness
reported). Selection effects are mitigated (leave-one-out baseline, role
stratification) but not eliminated; a same-player-across-time design is future
work. Single region, single patch band, solo queue (not professional play).

## 9. Conclusion

On a rare skill-labeled amateur corpus, we measured two designer-facing
properties of champions and found the naive measurements misleading: skill
reward, mechanical difficulty, and perceived fairness are three separable axes
that popular metrics conflate. The contribution is as much methodological — how
*not* to measure skill expression — as empirical. Code and anonymized data are
released with the companion dataset.

## Figures

Generated by `analysis/make_figures.py` → `analysis/output/figures/` (300 dpi,
Okabe-Ito colorblind-safe, position-colored where applicable).

- **Fig. 1** `fig1_three_measures.png` — three operationalizations of skill
  expression (win-rate slope vs tier, lane amplification, Riot difficulty) are
  mutually uncorrelated (pairwise |Spearman| ≤ 0.09).
- **Fig. 2** `fig2_reward_vs_difficulty.png` — role-stratified skill amplification
  vs Riot mechanical difficulty, colored by position; dissociated (partial
  Spearman −0.03).
- **Fig. 3** `fig3_ban_quadrants.png` — ban-rate-z vs win-rate-z quadrants;
  anti-fun (Yasuo, Illaoi, Darius, Tahm Kench) separate from overpowered.
- **Fig. 4** `fig4_rq3_interaction.png` — skill amplification vs high-tier
  perceived-minus-actual gap; weak positive (Spearman 0.18).

## References (to verify/format at submission)

- Minka, Cleven, Zaykov. TrueSkill 2. MSR-TR, 2018.
- Le Guen et al. PandaSkill. arXiv:2501.10049; IEEE ToG 2025.
- Kim, Keegan, Park, Oh. The Proficiency–Congruency Dilemma. CHI 2016;
  arXiv:1512.08321.
- (authors) Play Style Flexibility in League of Legends. arXiv:2402.05865.
- Chen, Joachims. Modeling Intransitivity in Matchup and Comparison Data
  (blade-chest). WSDM 2016.
- Sanjaya, Wang, Yang. Measuring the Non-Transitivity in Chess. Algorithms
  15(5):152, 2022; arXiv:2110.11737.
- Li, Xu, Chan, Wang, Wang, Qu, Ma. Visual Analytics for Snowballing and
  Comeback in MOBA Games. IEEE TVCG 23(1), 2017.
- (authors) Beyond Win Rates: Clustering-Based Character Balance Analysis.
  arXiv:2502.01250, 2025.
- Medler, John, Lane. Data Cracker. CHI 2011.
- He, Tran, Jiang, Burghardt, Ferrara, Zheleva, Lerman. Heterogeneous Effects of
  Software Patches in a MOBA. FDG 2021; arXiv:2110.14632.
- Riot Games /dev. Champion Balance Framework. 2019 (industry).
- DiGRA 2024. Predictability in Competitive Video Games: Strategic Equilibrium
  and Player Agency. (dl.digra.org art. 2218)
- [R1] LoLA-2016 dataset paper (companion; Zenodo DOI TBD).
