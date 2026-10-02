# Top Five Things Agent

An assistant skill that turns weekly work notes into a structured Top 5 Things report, saves a local draft for review, and helps publish an explicitly approved report into your own Google Docs template.

This repository contains the reusable skill, a local Python helper, and tests. Each user's profiles, notes, reports, and approval records stay in the ignored `.t5t/` directory. No personal weekly reports or preconfigured personal destinations are included.

## What it does

- Accepts five named workstreams or a brain dump and helps select five meaningful updates without inventing missing facts.
- Uses your template and up to three completed weekly reports for formatting and writing style; compares ongoing work with the preceding report.
- Optionally gathers context from your connected Slack, email, Google Drive, Teams, or local notes when you authorize that discovery.
- Produces a Mission, five summary entries, and five detail sections containing Goal, In collaboration with, Status, and Next Steps.
- Uses your configured To, Bcc, and subject; derives Cc from people mentioned in the report and deduplicates confirmed aliases.
- Saves structured JSON and a Markdown draft, checks required fields, and records content hashes after you approve publication.
- Guides your assistant through copying and filling a native Google Docs template tab and verifying the result.

The Python helper makes no network requests and cannot publish, send email, schedule reports, or verify factual truth. Google Docs publishing requires your assistant's authenticated editing tools and your explicit approval of the current draft. This is an on-demand skill, not a standalone chatbot or background service.

## Requirements

- An AI assistant that can read local files and follow `SKILL.md`. Local command execution is needed to use the helper.
- Python 3.9 or newer with IANA timezone data available. The helper uses only the standard library; there is no package install step. Some systems, especially Windows, may need timezone data installed separately.
- Your own Google Doc with a template tab for the full publishing workflow. Completed weekly tabs are optional.
- Connected Google Docs read/edit tools for publishing. Other source connectors are optional; you can draft from pasted notes when connectors are unavailable.

## Get started

Clone this repository and open the folder in your assistant-enabled editor:

```sh
git clone https://github.com/emanvela29/t5t-agent.git
cd t5t-agent
```

Ask your assistant:

> Read top-five-things/SKILL.md and help me set up my weekly Top 5 Things. Use my own Google Doc and ask me for any missing setup details.

The assistant asks for your document, timezone, and source preferences. It initializes a profile, reads your template, confirms its recipients and subject, and identifies completed examples when available. You can also initialize the profile yourself:

```sh
python3 top-five-things/scripts/t5t.py init \
  --user me \
  --document 'https://docs.google.com/document/d/YOUR_DOCUMENT_ID/edit' \
  --timezone America/Los_Angeles
```

Replace the document URL and timezone with your own. `init` creates `.t5t/profiles/me.json`; it refuses to overwrite an existing profile. Initialization alone does not complete setup. Have your assistant fill `template_tab_id`, `to` (a nonempty list of recipient names or addresses), `bcc`, and `subject` from your template. The current helper requires a nonempty Bcc. If your template has no Bcc or To, the assistant must explain that limitation rather than invent recipients. Optional `recipient_aliases` maps an alternate name to a confirmed preferred name. Each person uses a separate profile.

If your assistant supports installed skills, install the `top-five-things/` folder using its skill installation mechanism. Otherwise, explicitly load `top-five-things/SKILL.md` each time. The included `AGENTS.md` gives assistants that support it the same routing instruction. When using the skill in a different project, add `.t5t/` to that project's `.gitignore` before generating private files.

## Use it each week

Ask your assistant:

> Read top-five-things/SKILL.md. Draft my Top 5 Things for this week using profile me. Here are my notes: [paste your updates].

Specify a reporting date if you want a different week. The default period is the current Monday through Friday in your timezone, including when invoked on a weekend. You can opt out of connected-source discovery and supply notes directly.

The assistant asks about material gaps, saves the draft, and shows it for review. Each week's private files live at:

```text
.t5t/profiles/me.json
.t5t/drafts/me/<YYYY-MM-DD Monday>/report.json
.t5t/drafts/me/<YYYY-MM-DD Monday>/draft.md
```

Optional source notes, approval records, and publication records also stay in `.t5t/`. See the [report JSON contract](top-five-things/references/report-format.md) for required fields and an illustrative workstream. Reports normally require exactly five real workstreams. Incomplete drafts can be reviewed, but the helper refuses approval while fields or questions remain unresolved.

Request changes in chat, or edit `draft.md` and tell the assistant to reconcile your edits into `report.json`. Rendering preserves one changed draft as `draft.md.previous`; an existing backup must be reconciled before another replacement. The assistant must obtain approval again after any approved content or profile changes.

When the draft is ready, explicitly approve publication, for example:

> I approve this exact draft. Publish it to my configured Google Doc for this week.

The assistant then checks the approval record, duplicates the native template tab, fills only that weekly tab, and reads it back to verify content and formatting. It preserves the template and historical reports. If native tab duplication is unavailable in your assistant's tools, you must duplicate the template tab in Google Docs before the assistant can populate it. See the [publishing workflow](top-five-things/references/publishing.md). Publishing to Docs does not send email.

## Local helper commands

Run commands from the repository root. To inspect a reporting period:

```sh
python3 top-five-things/scripts/t5t.py week --timezone America/Los_Angeles
python3 top-five-things/scripts/t5t.py week --date 2026-09-30
```

After your assistant creates `report.json`, set these paths to the actual reporting Monday:

```sh
T5T_PROFILE=.t5t/profiles/me.json
T5T_WEEK=.t5t/drafts/me/2026-09-28
```

Validate and render:

```sh
python3 top-five-things/scripts/t5t.py validate \
  --profile "$T5T_PROFILE" --report "$T5T_WEEK/report.json"
python3 top-five-things/scripts/t5t.py render \
  --profile "$T5T_PROFILE" --report "$T5T_WEEK/report.json" \
  --draft "$T5T_WEEK/draft.md"
```

Only after explicit approval of the exact draft, record and check its hashes:

```sh
python3 top-five-things/scripts/t5t.py approve \
  --profile "$T5T_PROFILE" --report "$T5T_WEEK/report.json" \
  --draft "$T5T_WEEK/draft.md" --approval "$T5T_WEEK/approval.json" \
  --user-approved
python3 top-five-things/scripts/t5t.py check-approval \
  --profile "$T5T_PROFILE" --report "$T5T_WEEK/report.json" \
  --draft "$T5T_WEEK/draft.md" --approval "$T5T_WEEK/approval.json"
```

Neither command publishes anything. `--user-approved` is bookkeeping supplied by the operator, not independent proof of human consent. Hash checks detect subsequent file changes; the assistant must still verify actual approval, facts, the inventory of mentioned people, and Google Docs formatting. Use `--help` after any subcommand for its arguments.

## Privacy and sharing

`.gitignore` excludes `.t5t/`, Python caches, local environment files, private key files, and virtual environments. Keep personal profiles, destination URLs, notes, and drafts under `.t5t/`; placing them elsewhere may expose them to Git. Avoid `git add -f` for ignored files. Before committing, inspect `git diff --cached` and `git ls-files`.

To distribute the skill, share only the `top-five-things/` folder or clone this repository. Do not zip a working directory containing `.t5t/`. This repository includes fictional examples and tests, not users' actual reports. Source discovery remains subject to each assistant's account access and your authorization.

## Development checks

```sh
python3 -m unittest discover -s tests -v
```

The tests cover week boundaries, configurable recipients and aliases, incomplete report validation, and approval invalidation after edits. Connected-source access and Google Docs formatting must be checked in your environment during an approved publishing run.
