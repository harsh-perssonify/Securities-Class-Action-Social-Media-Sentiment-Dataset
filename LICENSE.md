# Licence and terms of use

Three different regimes apply to different parts of this release. Read all
three before redistributing.

## 1. Our annotations and labels — CC BY-NC 4.0

The following are our own work and are released under
[Creative Commons Attribution-NonCommercial 4.0 International](https://creativecommons.org/licenses/by-nc/4.0/)
(SPDX: `CC-BY-NC-4.0`):

- `gold_annotations.csv` — the 400 human gold labels
- `gold_annotation_guide.md` — the codebook
- `gold_agreement_metrics.json` — the agreement statistics
- the `llm_*` columns in `messages.csv` — LLM classifications
- `model_scores.csv` — baseline model scores
- our derived mappings: `case_ref`, `cohort`, `windows`, `is_spam`,
  `author_hash`, and the `case_ref` → case assignment in
  `case_crosswalk.csv`
- the `fraud_types` coding in `litigation_cases.csv`, and the structuring of
  that file — the schema, the extraction, and the arrangement of the
  underlying facts into it

You may share and adapt these, provided you give appropriate credit and
**do not use them for commercial purposes**. See `CITATION.cff` for the
citation.

"NonCommercial" is CC's own definition: not primarily intended for or
directed toward commercial advantage or monetary compensation. Academic and
non-profit research, teaching, and journalism are fine. Use inside a
commercial product, or research funded to build one, is not — ask us
instead. If you need a commercial licence, contact the authors listed in
`CITATION.cff`.

## 2. Message IDs — X Developer Agreement

`message_id` values are Tweet IDs. They are redistributed here under the
provision of X's Developer Agreement and Policy permitting redistribution of
Tweet IDs. **No hydrated Tweet Content is included in this release** — no
message text, no engagement metrics, no timestamps, no language codes.

If you re-hydrate using `hydrate.py`, the content you retrieve is Tweet
Content and is governed by X's terms, not by the CC BY-NC licence above. In
particular you must not redistribute hydrated content, and you must honour
deletions: content whose author has removed it will not re-hydrate, and you
should not retain copies of it.

## 3. Case records — facts of public proceedings

`case_crosswalk.csv` and `litigation_cases.csv` describe U.S. federal court
proceedings: docket numbers, parties, courts, class periods, motion and
settlement outcomes, and lifecycle dates.

These are facts about publicly filed litigation. Court filings in the United
States are public records and federal government edicts are not subject to
copyright; the facts recorded in them — who sued whom, in which court, on
what date, for how much — are not anyone's property to license. What we do
claim, and license CC BY-NC above, is the work of extracting those facts
into a schema: the field definitions, the `case_ref` keying, the
`fraud_types` coding, and the compilation as a whole.

Two provenance notes:

- The underlying complaint PDFs and settlement notices were obtained from
  PACER and from a commercial archive. **The source documents are not
  redistributed here** — only structured fields extracted from them. If you
  need the filings themselves, retrieve them from PACER.
- `source_pdf` filenames and the record-ID prefixes inside `case_id` are
  internal identifiers from our source index. They are collection artefacts,
  meaningless outside this dataset, and are not citable docket references.

`allegations_summary` is a condensed description of what a complaint
alleges, produced by our extraction pipeline from the filing text. It is a
summary of a public court filing, not a reproduction of it, and it is an
**allegation** — an untested claim by a plaintiff, not a finding of fact.
See the warranty note below.

## No market data is included

There is no fourth regime, because there is no market data here. This
release contains **no prices, returns, volumes, market capitalisations or
any other quantitative market series** — check the column lists in
`README.md` and you will not find one.

`ticker`, `exchange` and `company_name` are identifiers, not market data. A
ticker symbol is assigned by an exchange, a listing venue is a matter of
public record, and a company's name is its own. No data vendor holds a
licensable interest in the fact that UnitedHealth Group trades as `UNH`.
`company_name` and `exchange` here were read from the court filings
alongside the rest of the case record, not retrieved from a market feed —
their inconsistent capitalisation (`BLUEBIRD BIO, INC`, `Bumble Inc`) is the
tell.

> **If you rebuild this dataset:** the pipeline may call Yahoo Finance via
> `yfinance` to resolve or validate tickers. Yahoo's terms restrict
> redistribution of their data, and `yfinance` is an unofficial client. That
> constrains what a *future* build may publish — if you add price series,
> event-window returns, or any other retrieved values, this section stops
> being true and you need to license them separately. It does not constrain
> the release as it currently stands, which retrieves nothing from Yahoo.

## No warranty

Provided as-is, without warranty of any kind.

**The labels contain errors.** They are machine- and human-generated; the
measured human–LLM agreement is κ ≈ 0.74 on both axes, which is substantial
but far from perfect.

**The case fields contain errors.** They were extracted programmatically
from PDFs and were not verified case by case. Coverage is uneven, several
columns are known to be unreliable, and one is empty throughout —
`README.md` documents the specific problems. Verify against the docket
before relying on any individual value.

**Allegations are not findings.** `allegations_summary`, `fraud_types`,
`sections_cited` and `defendants` record what a plaintiff claimed in a
filing. A securities complaint is an untested assertion; most are disputed,
many are dismissed, and a settlement is not an admission. `defendants` names
individual people — officers and directors named in complaints. Their
presence in this dataset means only that someone sued them.

Do not treat any field here as ground truth about a company, a person, or a
legal matter, and do not use this dataset to make representations about
anyone's conduct.
