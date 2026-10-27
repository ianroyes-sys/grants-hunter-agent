---
name: grants
description: Find and submit grant, pitch-competition, accelerator and founder-fellowship applications for a small business end to end. Use when the owner asks to apply for grants or funding for the business, find business grants, check grant status, or finish a grant they unblocked.
---

# Grants

Work from the grants-hunter-agent repo root (set `GRANTS_HOME` if you keep it somewhere other than the session's working directory), run every command from there, and read its `CLAUDE.md` first. That file holds the rules: authority, facts, voice, walls, engine commands and browser notes. If the owner has given standing approval to submit fee-less applications (recorded in `CLAUDE.md`), report results and don't ask permission again. Without that line, stop before every Submit and ask.

Arguments pick the branch:
- no argument: a full pass, steps 1–5;
- `hunt`: steps 1–2;
- `status`: step 5 only;
- a program name: steps 3–4 for that one program.

## 1. Unblock
Read `OWNER-ACTIONS.md` and any answers the owner left for the `grants` loop.
- **The owner marked a row done:** release that candidate with `bin/engine record --key KEY --state needs-browser --evidence OWNER-ACTIONS.md --user-request "<their words>"`, then move the row to the done table.
- **Deadline passed on an open row:** record it closed, citing the source.

Done when every row with a recorded answer has been acted on.

## 2. Hunt
Run `bin/engine prepare --lane opportunity-hunt --output pipeline/grants-hunt.json`. Skip anything already in `knownSources` or `RULED-OUT.md`.

Search current official sources, rotating through the families listed in `BUSINESS.md` under "Source families". A typical set:
- federal, state and city small-business programs (SBA, the state economic development office, local chambers and EDCs);
- corporate small-business grants (banks, carriers, card networks, telecoms and their grant partners);
- student-founder competitions and accelerators, if a founder is enrolled;
- founder-identity funds that match the founders (for example Black-, women-, veteran- or immigrant-founder programs);
- industry funds that pay vendors in the business's field;
- university business-plan competitions open to outside students;
- free credit programs that admit the business's type (some exclude agencies and service firms).

Verify each lead on the sponsor's own page. You need all four of: eligibility that fits the business, no fee, a deadline in the future or rolling, and a named sponsor. Add each verified lead with `bin/engine add`. Log every source family with `search-result`, including zero-result ones. Excluded programs go in `RULED-OUT.md` with the rule that excludes them.

Done when at least three source families have been searched and logged this pass.

## 3. Apply
Run `bin/engine prepare --lane opportunity --output pipeline/grants-packet.json`, then take each candidate in order:
1. Grep `pipeline/SUBMISSIONS.md` (and `$JOB_SUBMISSIONS_LEDGER`, if another agent also applies to competitions for the same person). One program gets one application.
2. Open the official form in Playwright and read every page before writing anything.
3. Draft the answers from `ANSWER-BANK.md` and the facts in `BUSINESS.md`, fitted to each prompt's word limit, then pass essays through a humanizer pass (plain sentences, no AI tells).
4. Fill each field, re-read what rendered, and click Submit once.
5. If you hit a wall from `CLAUDE.md`, add an `OWNER-ACTIONS.md` row with the exact step and link, record the candidate `deferred` with a `user-action:` reason, and move to the next candidate.

Done when the packet's `counts.actionable` is 0, or every remaining candidate is deferred with a concrete reason.

## 4. Record
For each submission:
- save a screenshot to `screenshots/` and the answers to `evidence/`;
- append one row to `pipeline/SUBMISSIONS.md`;
- run `bin/engine record --state submitted` with the confirmation text;
- add any new strong answer to `ANSWER-BANK.md`.

Done when every portal confirmation from this pass has all four.

## 5. Follow up and report
Search the business inbox for mail from submitted programs since the last pass (`scripts/gmail_search.py` or a Gmail MCP) and log it in `FOLLOWUP.md`. Escalate finalist notices, interviews and document requests to the top of `OWNER-ACTIONS.md`.

Report:
- what was submitted (program, ask, confirmation);
- new leads found;
- new owner actions, with due dates;
- counts from `prepare`.
