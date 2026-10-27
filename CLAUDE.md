# Grants: operating contract

The single source of rules for every grant run, whether manual (the `grants` skill) or scheduled (the `grants` loop). Edit the **Authority** line and `BUSINESS.md` for your own business before the first run.

## Outcome and authority
Win non-dilutive money and free resources for the business in `BUSINESS.md` by finding, completing and submitting applications end to end.

**Authority:** _(replace this line)_ Example: "The owner gave standing approval on 2026-10-21 to submit free, fee-less applications for the business end to end." With that line, submitting needs no further ask. Without it, the agent prepares everything and stops before each Submit.

Scope: small-business grants, pitch competitions, accelerators and pre-accelerators that take no equity or take it only on an explicit later opt-in, founder fellowships, and free credit or service programs the business is eligible for.

## Facts
- Every factual claim comes from `BUSINESS.md` ("Facts for forms" and "Proof"). Lead with the main line of business. Use side projects only as supporting proof.
- Reuse and adapt `ANSWER-BANK.md`. After each submission, add any new approved answer there.
- If a required fact is missing (EIN, P&L, a testimonial, a date of birth that isn't on file, or attendance at a live event on a date the owner hasn't confirmed), the candidate becomes an **owner action**: add a row to `OWNER-ACTIONS.md` and continue with other candidates. Never estimate, round up or invent.
- The website is always the business's own site from `BUSINESS.md`, never a founder's personal portfolio. Use the exact legal name from `BUSINESS.md`.
- Founder attributes (student status, school, identity-based eligibility) come only from `BUSINESS.md`. If a program needs two student founders and only one is confirmed, it's an owner action.

## Voice
Many programs screen for AI text (some run GPTZero). Write like a founder explaining the business to a person: plain sentences, concrete numbers, first person where the form allows it. Keep the punctuation plain: commas and periods, never em dashes or semicolon chains. No hype words, triads or slogan closers. Run a humanizer pass over every essay longer than three sentences before pasting it.

## Walls (approval does not lift these)
- **Fees:** any application fee, paid tier or "processing" charge means skip it, permanently.
- **Sensitive data:** never enter SSN, EIN-plus-bank pairs, bank or routing numbers, card data or government ID. If a form requires one, it's an owner action.
- **Accounts:** never create a new account and never type a password. "Continue with Google" is fine when the browser's signed-in Google session already has an account on that site. If no account exists, record the signup URL as an owner action. The owner signs in once in the browser the loop uses, and the next run picks up from there.
- **Bot checks:** never solve or bypass a CAPTCHA, MFA or bot check. Record it and move on.
- **Prohibited writing:** if a program bans AI-written applications, list it in `RULED-OUT.md` and point the owner to it.
- **Legitimacy:** skip affiliate funnels, "grant matching" services that charge, and anything without official rules or a named sponsor.

## Queue and records
The deterministic engine owns dedupe and state:
```
bin/engine prepare --lane opportunity --output pipeline/grants-packet.json     # actionable queue (packet "candidates" + "counts")
bin/engine prepare --lane opportunity-hunt --output pipeline/grants-hunt.json  # knownSources + searchHistory for hunting
bin/engine add --file cand.json   # ONE object: name, sourceUrl, category, cycle, eligibility, evidence[{url,excerpt}], openStatus(open|unknown), effort(low|unknown), optional deadline (YYYY-MM-DD)
bin/engine record --key KEY --state submitted --evidence screenshots/X.png --confirmation "exact portal text" --user-request "owner's standing grant approval"
bin/engine record --key KEY --state deferred --reason "user-action: <what the owner must do>"
bin/engine record --key KEY --state closed --evidence RULED-OUT.md --reason "<eligibility rule that excludes the business>"
bin/engine record --key KEY --state needs-browser --evidence OWNER-ACTIONS.md --user-request "<owner's words>"   # release after the owner's step is done
bin/engine search-result --focus FOCUS --source SOURCE --added N --reason REASON
```
Run these from the repo root. `--output` needs a real file path, so `/dev/null` won't work.
- The candidate category must contain one of the enabled keywords in `pipeline/CATEGORIES.json`, e.g. "small-business grant", "pitch competition", "accelerator".
- The engine takes a lock. Run calls one at a time, and don't run them in parallel shells.
- If another agent also applies to competitions for the same person (a job-search agent, say), set `JOB_SUBMISSIONS_LEDGER` to its ledger and grep it for the program name first, so one program never gets two applications.
- A submission counts only with a screenshot plus the portal's confirmation text or email. To log one:
  - save the PNG to `screenshots/YYYY-MM-DD-<slug>.png`;
  - save the answers to `evidence/YYYY-MM-DD-<slug>.md`;
  - append one row to `pipeline/SUBMISSIONS.md`;
  - run `record`.
- If a click might have submitted, record it as `unverified` and reconcile it from email or the portal before you click again. Never resend blind.

## Browser
A sign-in only exists in the browser profile it happened in. Pick one browser for the loop (for example a Playwright MCP attached to the owner's everyday Chrome profile) and send every "sign in to X" owner action to that browser. If several agents share it, hold a lease so two jobs never drive it at once.

Form tactics:
- Fill fields with `browser_fill_form` and CSS selectors.
- Click Save/Next/Submit with `browser_evaluate` when normal clicks are intercepted.
- Some forms only enable Submit after each field is saved.
- Before the single Submit click, re-read every rendered field and attachment.
- Decline upsells and paid trials.

## Follow-up
Search the business inbox (`scripts/gmail_search.py` with the `gws` CLI, or a Gmail MCP) for replies from submitted programs. Log each reply in `FOLLOWUP.md`:
- Interview, finalist, award or document request: put it at the top of `OWNER-ACTIONS.md` with the deadline.
- A routine confirmation step on the official channel (confirm email, RSVP to a session already applied for): do it.
- Never send any other email.
