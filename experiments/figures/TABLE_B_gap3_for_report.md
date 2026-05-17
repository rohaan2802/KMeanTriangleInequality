<!-- Gap 3 Table B — paste into report. SSE match: |ΔSSE| < 0.5 on bracket total in stdout. -->

| M | Lloyd time (s) | Elkan static (s) | Elkan guided (s) | Ratio static | Ratio guided | iters L / Es / Eg | naive vs Elkan(s) SSE | Elkan static vs guided SSE |
|---:|---:|---:|---:|---:|---:|---|---|---|
| 2 | 13.3161 | 2.7458 | 2.6948 | 0.2979 | 0.2979 | 82 / 82 / 82 | match | match |
| 8 | 4.1285 | 2.8219 | 2.8476 | 2.3207 | 2.4317 | 48 / 48 / 45 | match | differs |
| 16 | 4.7254 | 3.2900 | 2.8113 | 5.6713 | 5.6713 | 47 / 47 / 47 | match | match |
| 32 | 4.1874 | 2.5037 | 2.4925 | 11.7163 | 11.7163 | 30 / 30 / 30 | differs | match |
| 64 | 5.7816 | 3.0624 | 3.5013 | 20.0393 | 19.4586 | 24 / 23 / 24 | differs | differs |
| 128 | 9.0140 | 4.3204 | 4.0998 | 31.8309 | 31.7908 | 17 / 17 / 17 | differs | differs |

*Use “match/differs” to decide whether times are directly comparable; if Elkan static vs guided SSE differs, interpret runtime comparison cautiously.*
