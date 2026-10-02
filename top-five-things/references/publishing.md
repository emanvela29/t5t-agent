# Publish an approved weekly tab

## Preconditions

Run the helper `check-approval` against the exact profile, report, and Markdown draft. Also confirm actual conversational approval. Read the native destination again with all tabs and revision information. If the Google Docs skill is available, use its trusted-read and preservation procedure. Verify the configured template id, unchanged Bcc, and unique weekly title. Never rename the whole document.

## Native duplication

Use an available native tab-duplication tool or authorized browser action to duplicate the template inside the user's own document. Discover actual capabilities; do not invent a `duplicateTab` API request. A file-level copy copies the whole document and is not the requested destination. `addDocumentTab` creates a blank tab and is not a formatting-preserving copy.

If native duplication is unavailable, ask the user to duplicate the Template tab through Google Docs and name the copy with the approved date range. Explain that the active API lacks a native duplication action, and exact formatting is required. Continue preparing the draft independently; do not substitute a reconstructed tab. Verify the user's duplicate by reading it and comparing structure/styles before editing.

New tabs go after the latest weekly tab unless the user chooses another location. Preserve all existing tab ids, titles, order and content. Capture the new tab id from tool readback, never guess it. If the title already exists, inspect it and ask whether to revise; do not overwrite based only on a matching title.

## Fill without losing formatting

Read the duplicate's native paragraphs and runs. Map Mission, five summary entries, workstream titles, and Goal/Collaboration/Status/Next Steps fields to their actual ranges. Replace placeholder spans in place and append answers after field labels, preserving native lists and paragraph boundaries. Keep header labels bold and preserve each relevant run's font family, size, weight, color, links, paragraph spacing, list level, indentation, and alignment. Preserve source-native chips/objects where applicable. Remove optional placeholder guidance only when not used.

Every mutation must explicitly target the new tab id. For replaceAllText, use tabsCriteria.tabIds; for indexed ranges/locations, use tabId. Do not rely on first-tab defaults. Use requiredRevisionId when supported; on mismatch re-read and re-plan, never blindly retry. Apply indexed edits from end to start or refresh indexes after each edit. Preserve To names under the user's alias preference and preserve Bcc exactly. Use small scoped text/style edits; do not clear and recreate the body. Missing exact rich-element support is a limitation to disclose, not a reason to flatten it.

## Verification and recovery

Read the resulting tab and compare the full report with approved content, allowing native display representations of dates/links. Check To/Cc/Bcc, five summary/detail pairs, Mission, no em dashes, no leftover placeholders, and no source notes or approval metadata in publication prose. Compare representative and edited text runs and all affected paragraph/list styles with the template, including colors, sizes and indentation. Check template and historical tab content remains unchanged. Use rendered/browser inspection when available; report when only native style metadata was verified.

On a partial failure, inspect the existing new tab before any retry, repair only that tab, and do not create another. Never claim success while verification fails. Do not delete the tab automatically to hide a failed attempt. Record document id, tab id, title, revision, approved draft hash and verification result in private `publication.json`. The user decides when this report becomes completed history. Publishing to Docs does not authorize email delivery.

API reference checked during development: https://developers.google.com/workspace/docs/api/reference/rest/v1/documents/request
