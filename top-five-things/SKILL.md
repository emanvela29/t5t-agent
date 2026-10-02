---
name: top-five-things
description: Draft, revise, and publish weekly Top 5 Things workstream reports from notes and optional sources, preserving a user's Google Docs template and requiring draft approval before publishing.
---

# Top Five Things

## Setup and scope

Keep this workflow portable: discover the current assistant's actual file and connector capabilities rather than assuming tool names, an IDE, credentials, or installed plugins. Store private state in `.t5t/` under the working project, never inside this shareable skill. Select the user's profile explicitly if more than one exists. Never reuse another person's destination or historical facts.

On first use, ask for the user's own Google Doc, timezone, and optional source preferences. Use `scripts/t5t.py init` to initialize a profile. Read the full tab tree, identify the template by id, and identify the latest three **completed** reporting tabs. Confirm ordering if titles/dates are ambiguous; do not assume the last tab is a sent report. Save their ids to the profile. Inspect the native template styles and structures. Preserve its Bcc exactly. Confirm To recipients and subject from the user's template and save them in the profile. Store confirmed name aliases in the optional `recipient_aliases` map. Never assume another team's recipients or guess email addresses.

Use the template for formatting and the latest three completed weeks for writing style. Refresh those examples over time, excluding drafts and the template. If no history is available, use the writing guidance below and disclose that examples were unavailable. A missing connector does not prevent a local draft; request pasted content when needed. Do not install integrations or change sharing as a side effect.

## Weekly intake

1. Resolve the reporting Monday and Friday in the user's timezone. Ask if “last week” or a backdated request is ambiguous. Default to the current calendar week, including on weekends. Use the helper's `week` command for date arithmetic.
2. Accept either five named workstreams or unstructured notes. If selection is necessary, propose five based on meaningful progress, delivery impact, decisions, blockers, and upcoming milestones; have the user confirm the selection. With fewer than five, ask what else belongs. Never fabricate filler. Keep an incomplete draft if needed; publish fewer only if the user explicitly requests that exception.
3. Read the preceding completed update and ask what changed in continuing workstreams. Keep stable goals as historical context, but confirm their continued applicability. Completion of a milestone does not imply completion of the whole project. Silence does not mean no change, and an elapsed deadline does not mean a delivery happened.
4. Offer discovery in connected Slack, email, Google Drive, Teams, and user-designated local notes unless the user has opted out. Do not repeatedly offer after refusal. Offer once, continue drafting while awaiting an answer, and search when requested or previously authorized. Supplied links are permission to read their relevant content, not to search unrelated accounts. Keep sources optional.
5. Read `references/sources.md` when gathering context. Ask one compact set of material missing questions: this week's change, goal, collaborators, status, and next steps or dates. Skip answered questions. Sources can answer them; uncertain identities and conflicting facts need clarification. Preserve approximate quantities as approximate.

## Draft and review

Read `references/report-format.md` and write a structured report plus a local Markdown draft in `.t5t/drafts/<user>/<monday>/`. Use the helper to validate and render. Save source references separately from report prose. Do not require sources for first-person updates.

Write the five detail sections first, with Goal, In collaboration with, Status, and Next Steps. Write matching summary entries in the same order. Rewrite Mission as a coherent summary of all five workflows, not a generic role description. Match the latest three completed examples: concrete outcomes, delivery quantities, decisions and approval conditions; concise summaries; specific next actions. Do not copy historical facts merely to match prose. Do not use em dashes anywhere in the report. Avoid inventing owners, deadlines, metrics, acceptance, approvals, or collaboration.

Maintain an explicit list of people mentioned anywhere in the finished report. Cc includes each person except the profile's To recipients, with confirmed aliases deduplicated. Vendors/teams are not individual recipients. A person only mentioned in background sources is not automatically a collaborator or Cc recipient. Resolve ambiguous first names before finalizing recipients; names are acceptable when emails are unavailable. Keep To and Bcc as agreed. Do not send email or messages.

Show the draft link and a short review note about changes from last week, unanswered questions, and any source conflicts. Keep these notes outside the publication text. Invite edits. If the user directly edits Markdown, reconcile it into the structured report and regenerate before approval; never silently overwrite those edits. Validate again after revisions.

## Approval and publication

Only after the user explicitly approves the current draft for publication, use `approve` to record its hashes. A tool-generated approval record is bookkeeping, not user consent. Any later draft or profile change requires renewed approval. Building this skill is not approval to publish.

Follow `references/publishing.md` for native duplication, scoped edits, and verification. Never alter historical tabs or the template. If that week already exists, ask whether to revise it rather than creating another. Publish no draft with unresolved factual questions unless the user explicitly approves identified omissions/unknowns. Record the returned tab id only after verification. Do not mark a newly created draft as completed history until the user confirms it as final. No automated weekly trigger is configured; run when the user invokes the agent.
