LOUVO - developer notes (v1 draft, not yet balanced or tested against the
real Math SDK engine - see "known limitations" at the bottom before relying
on any of this).

THEME
Parody of the Lovoo dating app. Duel at Dawn's Wild West setting is swapped
for a "swipe app" setting; each mechanic below has a direct 1:1 counterpart
in the reference game.

SYMBOLS
  W          Wild - Louvo heart logo. Pays 20x on 5-of-a-kind only.
  S          Scatter - "DATE" icon. 3 = Speed Dating (10 FS), 4+ = After
             Dark (10 FS).
  M          MATCH - expands to a full wild reel + a duel multiplier
             (2x-200x, higher of two drawn values "wins the duel").
             Never appears on the After Dark reel-set.
  K          SUPER LIKE - expands to a full wild reel + a multiplier AND
             fires extra wilds onto the board based on how many likes it received.
             Max 2 per spin, max 1 per reel.
  H1..H6     portrait symbols, best to weakest pay:
             H1 Le R, H2 Inso, H3 Shanna, H4 Manu, H5 Indigo, H6 Coca Cherry
  L1..L4     basic symbols (all pay the same): L1 Verifie, L2 Message,
             L3 Flamme, L4 Coeur

WIN EVALUATION
19 paylines on a 5x5 grid (see game_config.py - PLACEHOLDER line map, not
extracted from the reference game's exact line images).

BONUS STRUCTURE
  Speed Dating (3 scatters, 10 FS)
    - same base mechanics, higher chance of M/K and higher multipliers.
    - +2 FS for 2 more scatters, +4 FS for 3 more scatters during the bonus.
  After Dark (4 scatters, 10 FS)
    - M never appears normally; K appears more often.
    - Landing a full 6-like K queues a "Match Streak" (DuelSpin-equivalent):
      an immediate forced bonus spin guaranteeing 2/3/4/5 M symbols (1st to
      4th unlock), +3 extra FS per unlock, max 4 unlocks per bonus round.

BONUS BUY
  bonus_speed_dating (placeholder cost 80x) / bonus_after_dark (placeholder
  cost 150x): direct entry into a bonus tier.
  match_boost (cost 3x): 5x higher natural chance of triggering a bonus,
  not guaranteed - plays like normal base spins with boosted odds.
  match_frenzy (cost 60x): every spin guarantees 2+ MATCH reels, stays in
  base spins only (scatters stripped so it can never trigger freegame).
  like_storm (cost 60x): every spin guarantees 1 SUPER LIKE with 2+ likes,
  same base-spins-only rule.
  Costs are NOT tuned - see known limitations.

FILES IN THIS FOLDER
  game_config.py        symbols, paytable, paylines, reels, bet modes
  game_override.py       attaches multiplier / like-count to fresh M/K symbols
  game_calculations.py   reel-expansion + like-firing + Match Streak logic
  game_executables.py    thin placeholder for future game-specific overrides
  gamestate.py           run_spin() / run_freespin() - the main control flow
  run.py                 simulation runner (start with num_sim_args = 100,
                          compression = False, per the SDK's own quickstart
                          advice, before scaling up)
  reels/BR0.csv           basegame reel strip (placeholder weights)
  reels/FR0.csv           Speed Dating reel strip (placeholder weights)
  reels/FR1.csv           After Dark reel strip (placeholder weights, no M)

KNOWN LIMITATIONS / WHAT STILL NEEDS WORK
1. Written without network access to the actual StakeEngine/math-sdk
   package, so import paths marked "TODO: verify path locally" in
   game_calculations.py, game_executables.py, gamestate.py and run.py are
   best-effort reconstructions from the public docs, not confirmed against
   the real source. Fix these first - diff against games/0_0_expwilds/
   (official "expanding wild reel" sample, closest match to Louvo) for the
   correct import paths and loop-counter attribute names (self.fs/self.tot_fs
   in gamestate.py is an educated guess).
2. Reel strip weights, multiplier ladders and bonus-buy costs are placeholder
   values, not derived from simulation. Run with run_optimization = True
   (needs Rust/Cargo) once the mechanics check out, to hit the 96.5% RTP
   target properly.
3. Paylines are a generic symmetric 19-line set, not extracted from the
   reference game's exact line-position images.
4. The "MATCH and SUPER LIKE never resolve on the same spin" rule is
   currently handled by dropping MATCH at runtime if both appear - the
   reference game instead seems to prevent this at the reel-strip design
   level. Either approach works; this one is just simpler to reason about
   for a first pass.
