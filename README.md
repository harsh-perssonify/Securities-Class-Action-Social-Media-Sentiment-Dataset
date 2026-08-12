# Securities Class Action Social-Media Sentiment Dataset

66,890 X/Twitter messages discussing U.S. securities class actions
(2002–2025), labelled for sentiment and relevance by an LLM, scored by four
off-the-shelf sentiment models, and anchored by a **400-message
human-annotated gold standard** with its codebook and agreement statistics.
The 845 underlying lawsuits ship with it, structured — court, parties, class
period, motion and settlement outcomes — so message sentiment can be joined
to case outcomes directly.

The gold set is the point of the release: it lets you measure how well
automatic sentiment labelling actually works on financial-litigation social
media, rather than assuming it.

## Distributed as message IDs, not text

Per X's Developer Agreement, this release contains **Tweet IDs and our own
labels — no message text, engagement metrics, timestamps, or language
codes.** Recover them yourself:

```bash
python hydrate.py --timestamps-only     # offline, no credentials needed
export X_BEARER_TOKEN=...               # then, for text + metrics:
python hydrate.py
```

`--timestamps-only` needs no X account at all: Tweet IDs issued after
2010-11-04 encode their own creation time, so `hydrate.py` reconstructs
`created_at` by arithmetic for 66,803 of 66,890 IDs (the other 87 predate
that scheme). Derived times match X's to the second for all but 16 messages,
which differ by exactly 1s from millisecond rounding.

Full hydration recovers all nine withheld fields — `text`, `created_at`,
`lang`, `conversation_id`, `ref_type` and the four engagement counts —
keyed on `message_id`. Expect some messages to be unavailable:
deleted, suspended, or made private since collection. That is the mechanism
working as intended: this dataset cannot re-publish content its authors have
withdrawn.

What you retrieve is Tweet Content and stays under X's terms, not the
CC BY-NC licence covering our labels. Do not redistribute it, and do not
retain copies of messages that stop hydrating.

## Files

| File | Rows | What |
|---|---|---|
| `gold_annotations.csv` | 400 | **The gold standard.** Human `gold_polarity` + `gold_relevance`, plus every model's prediction on the same messages. |
| `gold_annotation_guide.md` | — | The codebook the annotator worked from: category definitions, boundary rules, worked examples. |
| `gold_agreement_metrics.json` | — | Every method vs the gold labels: accuracy, macro-F1, Cohen's κ, bootstrap CIs, confusion matrices. |
| `messages.csv` | 66,890 | All message IDs with LLM labels and our case/window mappings. |
| `model_scores.csv` | 66,890 | VADER, Loughran–McDonald, FinBERT and Twitter-RoBERTa scores per message. |
| `case_crosswalk.csv` | 845 | `case_ref` → court docket number, ticker, company name. |
| `litigation_cases.csv` | 845 | The full case record: court, parties, class period, motion and settlement outcomes, lifecycle dates. |
| `hydrate.py` | — | Recovers text/metrics (API) or timestamps (offline). |
| `LICENSE.md`, `CITATION.cff`, `CHECKSUMS.txt` | — | Terms, citation metadata, SHA-256 integrity. |

Join the message files on `message_id`; join the case files on `case_ref`.

Every file is a plain uncompressed CSV — UTF-8, RFC 4180-quoted, **LF line
endings**, no BOM. Nothing needs unpacking; open them directly in pandas, R,
Excel, or anything else.

The only caveat: some fields legitimately contain newlines inside quotes,
message text most of all. Parse with a real CSV reader rather than splitting
on `\n`.

## The gold set

400 messages drawn with a fixed seed, stratified on LLM relevance × polarity
× cohort with proportional allocation — self-weighting, so unweighted
metrics estimate corpus-level agreement directly without applying
`sampling_weight`. Annotation was **blind**: the annotator saw only the
message text, never any model's prediction.

Agreement with the LLM classifier (reproducible from `gold_annotations.csv`
alone):

| | Accuracy | Macro-F1 | Cohen's κ |
|---|---|---|---|
| Polarity | 0.860 | 0.878 | 0.741 |
| Relevance | 0.860 | 0.797 | 0.746 |

Baseline polarity κ against the same labels: Twitter-RoBERTa 0.449,
Loughran–McDonald 0.210, VADER 0.171, **FinBERT 0.079**. FinBERT is the
instructive case — 53.8% raw accuracy but κ near zero, because most of that
accuracy is the model defaulting to `neutral`, which happens to match this
corpus's neutral-heavy skew. A clean worked example of why κ belongs beside
accuracy on imbalanced label distributions.

**Known limitation:** 124 messages (0.19% of the corpus) were excluded from
the sampling frame because the LLM emitted an out-of-schema label for them.
The gold set therefore cannot contain a message the LLM failed to format,
which very slightly favours it.

## The cases

`case_crosswalk.csv` resolves every `case_ref` to the case it stands for:

| Column | What |
|---|---|
| `case_ref` | `CASE_0001` … — the identifier used in the message files |
| `case_id` | Court docket number — format is not uniform, see below |
| `cohort` | `2024`, `2025`, or `archive` |
| `ticker` / `company_name` | The defendant company |

`case_ref` is a short internal key, not an anonymisation: U.S. securities
class actions are public records, indexed publicly (e.g. the Stanford
Securities Class Action Clearinghouse), and `ticker` was already published
alongside every message. The crosswalk simply saves you the lookup.

Two things to know before you rely on it. `case_id` formatting is inherited
from our sources and is not uniform — most values look like
`{division}_{yy}cv{number}`, about half carry a leading record ID from our
source index (`{record}_{division}_{yy}cv{number}`), and appellate matters
appear as `{yy}-{number}`. No value includes the district, so pair `case_id`
with `company_name` to pin a case down rather than treating it as a citable
docket reference. And 845 cases are listed but only 268 have messages in
this release; the rest are the sampling frame the corpus was drawn from.

`litigation_cases.csv` covers the same 845 cases with the full record —
court, defendants, class period, motion-to-dismiss and settlement outcomes,
and the lifecycle date series. The crosswalk is just the four identifying
columns pulled out for convenient joining; if you need more than case
identity, go straight to `litigation_cases.csv`.

### Read this before using the case fields

These fields were extracted programmatically from complaint PDFs and
settlement notices. They were **not** hand-verified case by case, and the
quality varies sharply by column. Treat them as a research starting point,
not as a reliable legal record — check the docket before relying on any
individual value.

Specifically:

- **Coverage is uneven.** Only `case_ref`, `case_id`, `cohort`,
  `fraud_types`, `total_documents` and `char_count` are populated for all
  845 rows. `court` is filled for 304, `filing_date` for 613,
  `settlement_amount` for 327, `class_certification` for 55, `exchange` for
  69. `settlement_date` is **empty for every row** — use `final_approval_date`
  or `disbursement_date` instead.
- **`lead_plaintiff` is largely unusable.** Of 290 non-empty values, roughly
  a quarter are truncated sentence fragments captured by an over-greedy
  pattern (`"and Approval of Lead"`, `"them"`, `"Movant"`) rather than party
  names. Do not aggregate this column without cleaning it.
- **Date formats are not consistent across columns.** `filing_date` is
  `MM/DD/YY`, `notice_date` and the approval dates are `YYYY-MM-DD`, and
  `class_period_start` / `class_period_end` are free text (`March 14, 2022`).
  Parse per column.
- **`fraud_types` is our coding, not the filings'.** It is populated for all
  845 rows because it was model-assigned from document text — it is a label
  we produced, on the same footing as the `llm_*` message labels, and
  carries the same error profile.
- **`court` gives the district only** (`SOUTHERN DISTRICT OF NEW YORK`), with
  no circuit or judge.
- **`source_pdf`, `total_documents` and `char_count` describe our collection**,
  not the case — they record which document the extraction read and how much
  text it saw. `source_pdf` filenames and the record-ID prefixes in `case_id`
  are internal identifiers from our source index and are meaningless outside
  this dataset.

## Columns

- `message_id` — Tweet ID. The join key, and the hydration key.
- `case_ref` / `case_ref_all` — case identifier, resolved to a real docket
  by `case_crosswalk.csv`. 332 messages were collected under more than one
  case; `case_ref_all` lists all of them.
- `cohort` — `2024`, `2025`, or `archive` (resolved cases, filings 2002–2021).
- `ticker` — the company the message was collected against.
- `windows` — semicolon-separated event windows the message falls in
  (`baseline`, `class_period`, `event`, `post_disclosure`, `post_filing`).
  Windows overlap by design; 3,356 messages are in more than one.
- `author_hash` — salted SHA-256 pseudonym; 19,388 distinct authors. Stable
  within the dataset, not reversible to an account. (X would permit raw User
  IDs; we withhold them anyway.)
- `is_spam` — our collection-time heuristic (5+ cashtags with the ticker
  absent from the first 60 characters), independent of `llm_relevance`.
- `llm_*` — Claude Haiku labels: relevance, polarity, intensity (−2…+2),
  emotion, severity, topic.
- `*_cont` (in `model_scores.csv`) — each model's continuous score, signed
  **positive = positive sentiment**. VADER's compound score;
  Loughran–McDonald's `(n_pos − n_neg) / n_tokens`; FinBERT and RoBERTa's
  `P(positive) − P(negative)`.
- `*_label` — the 3-class mapping used throughout: VADER at ±0.05 compound,
  Loughran–McDonald by dominant word count (ties → neutral), transformers by
  argmax.

## What is not here

**Tweet Content** — text, timestamps, language, engagement metrics. Recover
it with `hydrate.py`, under X's terms. This is the one hard exclusion: X's
Developer Agreement permits redistributing Tweet IDs, not the content behind
them.

**The `author_hash` salt** — withheld deliberately, so the pseudonyms cannot
be brute-forced back to accounts.

**The source documents themselves** — the complaint PDFs and settlement
notices the case fields were extracted from. `litigation_cases.csv` carries
the structured extraction; the underlying filings are on PACER.
