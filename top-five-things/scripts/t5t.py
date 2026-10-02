#!/usr/bin/env python3
"""Local-only profile, draft and approval helpers. No network or publishing actions."""
import argparse
import hashlib
import json
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def canonical(name, aliases=None):
    name = ' '.join(name.split())
    for alias, preferred in (aliases or {}).items():
        if name.casefold() == ' '.join(alias.split()).casefold():
            return ' '.join(preferred.split())
    return name


def week(day):
    monday = day - timedelta(days=day.weekday())
    friday = monday + timedelta(days=4)
    def label(d, year=False):
        return f'{d:%b} {d.day}' + (f', {d.year}' if year else '')
    title = f'{label(monday, monday.year != friday.year)} - {label(friday, True)}'
    return {'monday': monday.isoformat(), 'friday': friday.isoformat(), 'title': title}


def cc(people, recipients, aliases=None):
    seen = {canonical(n, aliases).casefold() for n in recipients}
    result = []
    for person in people:
        person = canonical(person, aliases)
        if person.casefold() not in seen:
            seen.add(person.casefold())
            result.append(person)
    return result


def validate(profile, report):
    errors = []
    for key in ('document_url', 'template_tab_id', 'timezone', 'bcc', 'subject'):
        if not isinstance(profile.get(key), str) or not profile[key].strip():
            errors.append(f'Profile requires {key}')
    recipients = profile.get('to')
    if not isinstance(recipients, list) or not recipients or any(
            not isinstance(p, str) or not p.strip() for p in recipients):
        errors.append('Profile requires to as a nonempty list of recipients')
    aliases = profile.get('recipient_aliases', {})
    if not isinstance(aliases, dict) or any(
            not isinstance(k, str) or not k.strip() or not isinstance(v, str) or not v.strip()
            for k, v in aliases.items()):
        errors.append('recipient_aliases must map nonempty aliases to preferred names')
    try:
        ZoneInfo(profile.get('timezone', ''))
    except (ValueError, KeyError):
        errors.append('Invalid profile timezone')
    try:
        monday = date.fromisoformat(report['monday'])
        if monday.weekday() != 0:
            errors.append('Report monday must be a Monday')
    except (ValueError, KeyError, TypeError):
        errors.append('Report requires ISO monday date')
    for key in ('mission',):
        if not isinstance(report.get(key), str) or not report[key].strip():
            errors.append(f'Report requires {key}')
    streams = report.get('workstreams', [])
    if not isinstance(streams, list):
        return errors + ['workstreams must be a list']
    if len(streams) != 5:
        errors.append('Exactly five workstreams required; never invent filler')
    titles = set()
    for i, stream in enumerate(streams, 1):
        if not isinstance(stream, dict):
            errors.append(f'Workstream {i} must be an object')
            continue
        for key in ('title', 'summary', 'goal', 'collaboration', 'status', 'next_steps'):
            value = stream.get(key)
            if not isinstance(value, str) or not value.strip():
                errors.append(f'Workstream {i} requires {key}')
        title = str(stream.get('title', '')).strip().casefold()
        if title in titles:
            errors.append(f'Duplicate workstream title: {title}')
        titles.add(title)
    people = report.get('mentioned_people')
    if not isinstance(people, list) or any(not isinstance(p, str) or not p.strip() for p in people):
        errors.append('mentioned_people must be a list of nonempty names')
    if '\u2014' in json.dumps(report, ensure_ascii=False):
        errors.append('Em dashes are not allowed')
    if report.get('open_questions'):
        errors.append('Resolve open_questions before approval')
    return errors


def render(profile, report):
    period = week(date.fromisoformat(report['monday']))
    people = cc(report.get('mentioned_people', []), profile['to'], profile.get('recipient_aliases'))
    lines = [f'# {period["title"]}', '', f'**Subject:** {profile["subject"]}',
             f'**To:** {", ".join(profile["to"])}', f'**Cc:** {", ".join(people)}',
             f'**Bcc:** {profile["bcc"]}', '', f'## Mission', '', report['mission'],
             '', '## Summary', '']
    for s in report['workstreams']:
        lines.append(f'- **{s["title"]}:** {s["summary"]}')
    lines += ['', '## Details']
    for s in report['workstreams']:
        lines += ['', f'### {s["title"]}', '']
        for key, label in [('goal', 'Goal'), ('collaboration', 'In collaboration with'),
                           ('status', 'Status'), ('next_steps', 'Next Steps')]:
            lines.append(f'- **{label}:** {s[key]}')
    return '\n'.join(lines) + '\n'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fingerprints(args):
    return {key: digest(getattr(args, key)) for key in ('profile', 'report', 'draft')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    init = sub.add_parser('init')
    init.add_argument('--user', required=True)
    init.add_argument('--document', required=True)
    init.add_argument('--timezone', required=True)
    init.add_argument('--root', default='.t5t')
    dates = sub.add_parser('week')
    dates.add_argument('--date', help='Any ISO date in the requested week')
    dates.add_argument('--timezone', default='America/Los_Angeles')
    for command in ('validate', 'render', 'approve', 'check-approval'):
        cmd = sub.add_parser(command)
        cmd.add_argument('--profile', required=True)
        cmd.add_argument('--report', required=True)
        if command != 'validate':
            cmd.add_argument('--draft', required=True)
        if command in ('approve', 'check-approval'):
            cmd.add_argument('--approval', required=True)
        if command == 'approve':
            cmd.add_argument('--user-approved', action='store_true', required=True,
                             help='Use only after explicit user approval of this exact draft')
    args = parser.parse_args()
    if args.command == 'init':
        if not re.fullmatch(r'[a-zA-Z0-9_-]+', args.user):
            parser.error('user must contain only letters, numbers, underscores or hyphens')
        if not re.fullmatch(r'https://docs\.google\.com/document/d/[A-Za-z0-9_-]+(?:/[^\s]*)?', args.document):
            parser.error('Provide a native Google Docs URL')
        ZoneInfo(args.timezone)
        path = Path(args.root) / 'profiles' / f'{args.user}.json'
        if path.exists():
            parser.error(f'Profile already exists: {path}')
        save(path, {'user': args.user, 'document_url': args.document, 'template_tab_id': None,
                    'timezone': args.timezone, 'subject': 'Top 5 Things',
                    'to': [], 'recipient_aliases': {}, 'bcc': None, 'completed_example_tab_ids': [],
                    'source_discovery': 'offer', 'source_types': ['slack', 'email', 'google_drive', 'teams', 'local_notes']})
        print(f'Created {path}; read the template to complete template_tab_id, to, bcc, and subject.')
        return
    if args.command == 'week':
        day = date.fromisoformat(args.date) if args.date else datetime.now(ZoneInfo(args.timezone)).date()
        print(json.dumps(week(day)))
        return
    profile, report = read(args.profile), read(args.report)
    errors = validate(profile, report)
    if args.command == 'render':
        # Incomplete reports are reviewable. They remain ineligible for approval.
        content = render(profile, report)
        target = Path(args.draft)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.read_text(encoding='utf-8') != content:
            backup = target.with_name(target.name + '.previous')
            if backup.exists():
                parser.error(f'Preserve or reconcile existing backup first: {backup}')
            backup.write_bytes(target.read_bytes())
        target.write_text(content, encoding='utf-8')
        print(f'Saved {target}')
        if errors:
            print('Not ready for approval:\n' + '\n'.join(errors))
        return
    if errors:
        parser.error('; '.join(errors))
    if args.command == 'validate':
        print('Report checks passed. Agent must still verify facts and completeness of mentioned_people.')
        return
    if Path(args.draft).read_text(encoding='utf-8') != render(profile, report):
        parser.error('Draft differs from report. Reconcile edits and obtain approval again.')
    hashes = fingerprints(args)
    if args.command == 'approve':
        save(args.approval, {'hashes': hashes, 'approved_at': datetime.now(timezone.utc).isoformat(),
                             'note': 'Recorded by assistant after conversational approval; not independent proof of consent.'})
        print('Approval recorded. No remote action performed.')
    else:
        if read(args.approval).get('hashes') != hashes:
            parser.error('Content or profile changed since approval; obtain approval again')
        print('Approval hashes match. Verify conversational consent before publishing.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise SystemExit(f'Error: {exc}')
