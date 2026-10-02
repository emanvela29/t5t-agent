# Local report contract

Paths are relative to the project where the agent is invoked. Keep each user's state separate:

```
.t5t/profiles/<user>.json
.t5t/drafts/<user>/<YYYY-MM-DD Monday>/report.json
.t5t/drafts/<user>/<YYYY-MM-DD Monday>/draft.md
```

`report.json` shape (repeat the workstream object for five real workstreams):

```json
{
  "monday": "2026-09-28",
  "mission": "A cohesive summary of this week's five workflows.",
  "mentioned_people": ["Alex Example"],
  "open_questions": [],
  "workstreams": [
    {
      "title": "Workstream name",
      "summary": "This week's meaningful outcome or change.",
      "goal": "The outcome this workstream supports.",
      "collaboration": "Alex Example and the vendor team",
      "status": "In progress - confirmed change and any current blocker.",
      "next_steps": "Specific agreed next action, with owner and date only when known."
    }
  ]
}
```

`mentioned_people` contains every named person in Mission, summaries and details, not just collaboration fields. The agent must verify this inventory semantically; the helper only deduplicates it and excludes To recipients. Do not treat vendors or teams as named people. The fields are plain prose; do not embed review questions or source-gathering notes in them. Working drafts may have fewer than five entries and explicit unknowns, but approval validation rejects incomplete reports. An explicitly user-authorized exception requires an agent-reviewed manual path and a recorded reason, not adding fake items to bypass checks.

Helper commands (substitute actual paths):

```sh
python3 top-five-things/scripts/t5t.py week --date 2026-09-30
python3 top-five-things/scripts/t5t.py render --profile PROFILE --report REPORT --draft DRAFT
python3 top-five-things/scripts/t5t.py validate --profile PROFILE --report REPORT
python3 top-five-things/scripts/t5t.py approve --profile PROFILE --report REPORT --draft DRAFT --approval APPROVAL --user-approved
python3 top-five-things/scripts/t5t.py check-approval --profile PROFILE --report REPORT --draft DRAFT --approval APPROVAL
```

Use `approve` only after actual user consent. Rendering preserves one previous draft before replacing changed text; reconcile manual edits first. If a `.previous` backup already exists, resolve it deliberately rather than deleting it blindly. A draft heading with the week is review metadata; the Google Docs tab title holds that week while the template controls the document's content heading. The helper does not assess factual truth, source coverage, or Google Docs formatting.
