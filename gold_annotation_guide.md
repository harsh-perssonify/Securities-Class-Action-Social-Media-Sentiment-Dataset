# Gold annotation codebook

> Examples below are **abstracted descriptions** of real messages, not
> verbatim quotations, so this document carries no redistributable Tweet
> Content. The annotator worked from the verbatim originals.

400 messages in `validation_sample.csv`. Fill **`gold_relevance`** and
**`gold_polarity`** for every row. Leave nothing else changed.

Allowed values — type them exactly, lowercase:

- `gold_relevance` → `relevant` | `tangential` | `spam`
- `gold_polarity` → `negative` | `neutral` | `positive`

## Before you start

The `pred_*` columns at the far right hold model predictions, including the
LLM's. **Hide or delete those columns while labelling** — the point of this
exercise is an independent reference, and reading them first destroys it.
`compare_annotations.py` recovers the predictions by `message_id`, so
deleting the columns from your working copy is safe.

Label both axes for every row, including messages you judge `spam`. Polarity
is about the message's stance toward the company, and a spam message still has
one. Judge only what is in the text; do not follow links or look the case up.
If a message is genuinely undecidable, leave the row blank rather than
guessing — the scorer reports how many rows were labelled and ignores blanks.

## `gold_relevance` — is this message about the company's situation?

**`relevant`** — substantively about this company: its stock, the alleged
fraud, the litigation, an investigation, regulatory action, earnings, or a
corporate event. The message has actual content about the firm.

- A news headline reporting that a regulator has confirmed a previously undisclosed probe into the company, carrying its cashtag.
- A report that the company instructed staff to stay quiet about missing paperwork, framed as a lawsuit story.
- A statement that a federal agency has opened a criminal investigation into the company for suspected fraud.

**`tangential`** — the ticker or company name appears, but the message is not
about the company's situation: watchlists, portfolio lists, mechanical filing
tickers, unrelated market commentary, price chatter with no informational
content.

- An automated delayed-feed line noting the company filed an 8-K, with a timestamp.
- A wire-style item noting some institutional holder increased its position as the share price fell.
- A reply to another account making a bullish price prediction using the cashtag.

**`spam`** — automated or promotional noise: cashtag stuffing, pump/dump,
signal-service and score-bot output, app advertising, engagement farming.
Judge by the message's *function*, not its topic.

- A scoring-bot post emitting a numeric score plus "Signal (Positive)" and generic stock hashtags.
- An app-promotion post announcing new regulatory documents and ending in a product plug.
- A delayed-feed bot reciting a Form 4 insider derivative transaction.

### Decision rule for law-firm solicitations

Messages of the form "SHAREHOLDER ALERT: <law firm> announces filing of a
securities class action against <company>" are the single most
common hard case in this corpus, and the LLM labelled near-identical examples
inconsistently across `relevant`, `spam`, and both polarities.

**Rule: a law-firm notice naming this company's investigation, filing, or
settlement is `relevant`** — it is substantively about the litigation, and its
promotional character is recorded separately by the `topic` field, not by
relevance. Mark such a notice `spam` only if the firm's boilerplate is
attached to a stuffed list of unrelated tickers, or the company is not
actually named.

Applying this rule consistently matters more than the rule being the only
defensible one. Disagreement concentrated here is an expected, reportable
outcome, not a labelling error.

## `gold_polarity` — stance toward the company

Judge the stance the message conveys about the company, not your own view of
the company and not whether the news is exciting.

**`negative`** — fear, anger, criticism, concern, accusation, bearish
outlook, or the reporting of adverse facts (fraud allegations, probes, suits,
losses, declines).

- A headline reporting the company failed to get a market-rigging lawsuit dismissed.
- An all-caps announcement that a former state attorney general has initiated an investigation.
- A wire item noting an institutional holder cut its stake as the company's valuation declined.

**`neutral`** — factual, procedural, or balanced with no discernible stance:
bare filing notices, mechanical data, headlines that report without
characterising, genuinely two-sided commentary.

- A neutral news headline noting a third party urged the company's CEO to settle regulatory charges.
- A terse factual note that a specific filing was confirmed with the regulator.

**`positive`** — defending the company, bullish sentiment, optimism,
reassurance, dismissing concerns, or reporting favourable facts (upgrades,
insider buying, stake increases).

- A wire item reporting a major shareholder purchased several million dollars of stock.
- A headline stating the company is untroubled by the costs of product-liability lawsuits.
- A wire item reporting an institutional holder raised its stake.

### Boundary notes

- **Adverse facts reported flatly are `negative`, not `neutral`.** "SEC opens
  probe into X" carries negative information about X even with no adjectives.
  Reserve `neutral` for messages with no directional content at all.
- **Bad news about a defendant's opponent** — a company *winning* a dismissal
  is `positive` for that company.
- **Sarcasm and mockery** are `negative`.
- **Price-only statements** ("$X down 4%") are `negative` when they report a
  decline, `positive` for a rise, but are usually `tangential` on relevance.
- **Do not let relevance drive polarity.** A `spam` score-bot posting "Signal
  (Positive)" is `spam` + `positive`.

## When you are done

`label_validation.py` writes directly into `validation_sample.csv`'s
`gold_relevance`/`gold_polarity` columns as you go — nothing extra to save.
Copy (don't rename) it to `annotations.csv` once you're done, keeping
`validation_sample.csv` itself as the pristine, reproducible, unlabeled draw:

```bash
cp validation_sample.csv annotations.csv
python compare_annotations.py
```

The scorer reports, per method and separately for polarity and relevance:
accuracy, macro-F1, Cohen's κ (with bootstrap 95% CIs), and a confusion
matrix — written to `results.json` plus `table_primary.tex` /
`table_baselines.tex`. Only the
LLM predicts relevance; the four off-the-shelf methods produce polarity only,
so the relevance table has a single row by construction.
