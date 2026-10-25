# Agreement summary: claude-opus-5-5

Rows compared: 39

## Agreement by dimension

| dimension | exact | within_1 | mean_signed (model-human) | mean_abs | spearman |
|---|---|---|---|---|---|
| centrality | 0.64 | 0.95 | -0.26 | 0.41 | 0.79 |
| strength | 0.51 | 0.95 | -0.36 | 0.56 | 0.57 |
| correctness | 0.51 | 1.00 | 0.23 | 0.49 | 0.63 |
| clarity | 0.33 | 0.90 | 0.77 | 0.77 | 0.41 |
| total | 0.10 | 0.64 | 0.38 | 1.56 | 0.72 |

## Mean absolute difference by position (hardest first)

| position_id | n | mad_centrality | mad_strength | mad_correctness | mad_clarity | mad_total |
|---|---|---|---|---|---|---|
| P7b | 3 | 1.00 | 0.67 | 0.67 | 1.33 | 0.92 |
| P2a | 3 | 0.67 | 1.67 | 0.67 | 0.33 | 0.83 |
| P7a | 3 | 0.00 | 0.67 | 0.67 | 1.67 | 0.75 |
| P6a | 3 | 1.00 | 0.67 | 0.67 | 0.33 | 0.67 |
| P5a | 3 | 0.00 | 0.67 | 0.67 | 1.33 | 0.67 |
| P4a | 3 | 0.67 | 0.67 | 0.33 | 0.67 | 0.58 |
| P8a | 3 | 0.67 | 0.33 | 0.33 | 0.67 | 0.50 |
| P1 | 3 | 0.33 | 0.33 | 0.67 | 0.67 | 0.50 |
| P4b | 3 | 0.67 | 0.33 | 0.00 | 1.00 | 0.50 |
| P3a | 3 | 0.33 | 0.33 | 0.67 | 0.33 | 0.42 |
| P5b | 3 | 0.00 | 0.00 | 1.00 | 0.67 | 0.42 |
| P6b | 3 | 0.00 | 0.33 | 0.00 | 0.67 | 0.25 |
| P8b | 3 | 0.00 | 0.67 | 0.00 | 0.33 | 0.25 |

## Fluency leak

6 rows (human clarity >= 4, correctness <= 2).

- Strength: model 2.00 vs human 2.33
- Correctness: model 2.33 vs human 1.83

If the model's numbers are higher, it is rewarding fluency.

## Settled-law leak

0 of 22 rows the human marked correctness <= 2 got model correctness >= 4 (0%).

## Top 8 divergences

### P2a-A2 - Bitcoin is a commodity, not a security (abs diff 5)

**Argument:** Bitcoin trades on exchanges, is held almost entirely for profit, and now sits inside SEC-registered exchange-traded products. Something bought and sold as an investment is an investment, and investments are the SEC's domain.

**Scores (centrality/strength/correctness/clarity):** human 3/4/3/4, model 2/1/2/4

**Human notes:** Rated the steelman, not the text. Read this as a substance-over-form point: how an asset actually trades (inside ETPs, as an investment) can determine jurisdiction regardless of its raw form, as with commodity ETFs where SEC and CFTC jurisdiction depends on the wrapper. That argument is stronger than the one written, which conflates “investment” with “investment contract.” Model rated as written. Scores stand; disagreement reflects a rater-protocol gap (as-written vs. strongest reconstruction). The reconstructed version should be added as a separate argument.

**Model justification:** The argument relies on profit motive, which is only one Howey element, and ignores the decisive efforts-of-others and common-enterprise prongs; it also misreads spot ETP registration, since the trust shares are the securities while the underlying bitcoin is not (as with gold ETFs like GLD), so its premise that anything bought as an investment is a security misstates the law.


### P4a-A3 - Ether is a commodity under present-day Howey analysis (abs diff 5)

**Argument:** All Ether holders' fortunes rise and fall together with the value of the network, which satisfies horizontal commonality as several circuits define it. A common enterprise therefore exists, and the position's first premise fails.

**Scores (centrality/strength/correctness/clarity):** human 5/3/3/3, model 3/2/2/4

**Human notes:** Same protocol gap as P2a-A2. Rated centrality 5 because common enterprise is a Howey prong and attacking any prong is on-point; model rated 3 because the position’s weight sits on efforts-of-others, which this argument leaves untouched. Also credited the argument for where horizontal commonality could go rather than what it states; model correctly notes that commonality requires pooling, not shared price exposure. Scores stand.

**Model justification:** The argument attacks only the common-enterprise prong and leaves the dispositive efforts-of-others analysis untouched; it also misstates horizontal commonality, which requires pooling of investor funds with pro rata profit-sharing (e.g., in Telegram and Kik, issuer-pooled sale proceeds), not merely holders' shared exposure to market price.


### P2a-A3 - Bitcoin is a commodity, not a security (abs diff 4)

**Argument:** The 'digital gold' analogy fails because gold has non-monetary demand and physical scarcity, while Bitcoin's value rests on convention alone. That makes it a collectible or a speculative token, not a commodity.

**Scores (centrality/strength/correctness/clarity):** human 2/2/1/3, model 1/1/2/4

**Human notes:** (none)

**Model justification:** The argument attacks a 'digital gold' analogy the position never relies on and assumes commodity status requires intrinsic or non-monetary value, but the CEA's definition broadly covers all goods, articles, rights, and interests without any such test; even if Bitcoin were a 'collectible,' that would not make it a security under Howey.


### P6a-A3 - Meme coins are digital collectibles (abs diff 4)

**Argument:** The collectible analogy fails on substance. Collectibles are non-fungible and scarce; meme coins are fungible, often with unlimited issuance, and trade at machine speed in liquid markets. The closer analog is a lottery ticket or a currency with no economy behind it.

**Scores (centrality/strength/correctness/clarity):** human 4/4/3/4, model 2/2/3/4

**Human notes:** (none)

**Model justification:** The argument attacks the 'collectible' label on fungibility and scarcity, but the position rests on the absence of legal rights, issuer obligations, and managerial efforts, which is the Howey-relevant substance the SEC staff's February 2025 meme coin statement relied on; it also overstates that collectibles must be non-fungible, cites no law, and its lottery-ticket or currency alternatives would not make meme coins securities either.


### P7b-A1 - A token sold to fund an unbuilt platform is sold under an investment contract (abs diff 4)

**Argument:** The investment contract is the transaction, not the asset. A secondary-market purchaser who bought on an exchange never contracted with the issuer, and Ripple's programmatic-sales reasoning holds that such purchasers had no basis to expect profits from the issuer's efforts. The initial sale may be an investment contract; it does not follow that 'the token' is a security.

**Scores (centrality/strength/correctness/clarity):** human 3/3/2/3, model 2/2/3/4

**Human notes:** (none)

**Model justification:** The transaction-versus-asset point is sound, but the position is expressly limited to the sale at issuance, which the argument concedes may be an investment contract. The argument also mischaracterizes Ripple's programmatic sales, which were Ripple's own blind sales on exchanges rather than true secondary resales, and omits that Terraform declined to follow that reasoning.


### P7b-A3 - A token sold to fund an unbuilt platform is sold under an investment contract (abs diff 4)

**Argument:** Pre-sales of consumptive goods are not securities: a deposit on a restaurant under construction, a Kickstarter pledge. The immediate-use requirement comes from staff no-action letters, not from Howey. A token pre-sold for consumption and marketed that way is a forward sale of a good; timing alone cannot be dispositive, marketing is.

**Scores (centrality/strength/correctness/clarity):** human 5/4/4/3, model 4/3/3/4

**Human notes:** (none)

**Model justification:** The argument targets the dispositive question of whether buyers expect profit or consumption, and it has real support in Forman's consumptive-use principle, but it overstates its case in two ways: it implies the pre-functionality factor comes only from no-action letters, when Kik and Telegram themselves relied on non-functionality and resale expectations, and it treats marketing as dispositive, ignoring that Howey turns on economic reality, including tradability, which distinguishes tokens from restaurant deposits or Kickstarter pledges.


### P1-A1 - Bitcoin is inapt as currency on functional grounds (abs diff 3)

**Argument:** The functions of money are a spectrum, not a threshold, and Bitcoin performs them well where it is actually used: remittances into economies with capital controls, high-inflation jurisdictions, and Lightning-based payments where throughput is not binding. Judged where it competes, rather than against Visa in the United States, it is a functioning currency for a real population.

**Scores (centrality/strength/correctness/clarity):** human 5/3/3/4, model 4/3/4/5

**Human notes:** (none)

**Model justification:** The argument engages the functional criterion directly by reframing money's functions as a context-dependent spectrum. However, it mainly rehabilitates the medium-of-exchange function in niche settings and leaves the volatility and unit-of-account objections largely unanswered. Its empirical premise is also contestable, since stablecoins and dollars often dominate in high-inflation and capital-control settings. It misstates no law.


### P7a-A2 - Broken Tokens are capital raises mislabeled as utility tokens (abs diff 3)

**Argument:** Every early-stage token is 'pre-utility' at launch; the definition makes all ICOs broken, which proves too much.

**Scores (centrality/strength/correctness/clarity):** human 3/1/1/3, model 3/2/2/4

**Human notes:** (none)

**Model justification:** The overbreadth objection targets the definition's scope, but it ignores the position's conjunctive elements: profit and ownership marketing, and few legal rights. Its implied premise that classing most ICOs as capital raises is absurd also runs against the SEC's view (e.g., Chairman Clayton's 2018 remarks) that most ICOs were securities offerings under Howey.
