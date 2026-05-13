# Golf Clash Wind Cheat Sheet — rings per MPH

Generated from `my_bag.yaml`. Ball power assumed: **Power 0**.

Formula: `rings = wind_mph × cell_value`

## Table 1 — Normal Club Range (rings/MPH)

| Club | Acc | Power | MIN | MID | MAX |
|---|---:|---:|---:|---:|---:|
| Driver — Quarterback 8 | 100 | 231 | 0.69 | 0.83 | 0.96 |
| Wood — Sniper 7 | 100 | 166 | 0.68 | 0.80 | 0.92 |
| Long Iron — Grizzly 5 | 60 | 122 | 0.38 | 0.47 | 0.56 |
| Short Iron — Hornet 4 | 91 | 84 | 0.39 | 0.59 | 0.79 |

### Bag-specific MIN actual-carry values

| Club | MIN carry | from |
|---|---:|---|
| Driver | 166 | Wood power |
| Wood | 122 | Long Iron power |
| Long Iron | 84 | Short Iron power |
| Short Iron | 41 | Wedge power |

## Table 2 — Slider Cheat Sheet (rings/MPH)

| Slider % | Wedge — Endbringer 3 | Rough Iron — Nirvana 4 | Sand Wedge — Malibu 6 |
|---:|---:|---:|---:|
| 100% | 0.64 | 0.41 | 0.68 |
| 90% | 0.58 | 0.37 | 0.61 |
| 80% | 0.51 | 0.33 | 0.54 |
| 70% | 0.45 | 0.29 | 0.47 |
| 60% | 0.38 | 0.25 | 0.41 |
| 50% | 0.32 | 0.21 | 0.34 |
| 40% | 0.26 | 0.17 | 0.27 |
| 30% | 0.19 | 0.12 | 0.20 |
| 20% | 0.13 | 0.08 | 0.14 |
| 10% | 0.06 | 0.04 | 0.07 |

### MAX rings/MPH (100% slider)

- **Wedge — Endbringer 3** = `0.64`
- **Rough Iron — Nirvana 4** = `0.41`
- **Sand Wedge — Malibu 6** = `0.68`

---

**Caveats:**
- Tables assume ball Power 0 unless `ball_power` in bag config is non-zero (multiplies actual_carry by 1.00/1.03/1.05/1.07/1.10/1.13 for Power 0..5).
- Head/tail winds are reduced by ~40% in-game vs side winds.
- MIN values are bag-specific: upgrading a shorter club raises the next-longer club's MIN.
- Grizzly/B52 at level >= 5 apply the 0.9x correction automatically.
