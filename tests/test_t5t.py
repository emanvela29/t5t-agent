import importlib.util
import tempfile
import unittest
from datetime import date
from pathlib import Path

spec = importlib.util.spec_from_file_location('t5t', Path(__file__).parents[1] / 'top-five-things/scripts/t5t.py')
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)


class WorkflowTests(unittest.TestCase):
    def profile(self):
        return dict(document_url='https://docs.google.com/document/d/test/edit', template_tab_id='t.0',
                    timezone='America/Los_Angeles', bcc='team@example.com', subject='Top 5 Things',
                    to=['Taylor Example', 'Morgan Example'],
                    recipient_aliases={'T. Example': 'Taylor Example'})

    def report(self):
        return dict(monday='2026-09-28', mission='Progress across five workflows.',
                    mentioned_people=['T. Example', 'Alex Example', 'alex example', 'Morgan Example'],
                    open_questions=[], workstreams=[dict(title=f'Workstream {i}', summary='Reviewed.',
                    goal='Complete review.', collaboration='Alex Example', status='In progress',
                    next_steps='Resolve feedback.') for i in range(5)])

    def test_cross_year_and_weekend(self):
        self.assertEqual(t.week(date(2027, 1, 3)), dict(monday='2026-12-28', friday='2027-01-01',
                         title='Dec 28, 2026 - Jan 1, 2027'))

    def test_recipients_aliases_and_fixed_header(self):
        text = t.render(self.profile(), self.report())
        self.assertIn('**Cc:** Alex Example\n', text)
        self.assertIn('**To:** Taylor Example, Morgan Example', text)
        self.assertIn('**Bcc:** team@example.com', text)

    def test_recipients_are_profile_specific(self):
        profile = self.profile()
        profile['to'] = ['Alex Example']
        text = t.render(profile, self.report())
        self.assertIn('**To:** Alex Example\n', text)
        self.assertIn('**Cc:** Taylor Example, Morgan Example\n', text)
        profile['to'] = []
        self.assertIn('Profile requires to as a nonempty list of recipients',
                      t.validate(profile, self.report()))

    def test_incomplete_and_unresolved_not_approvable(self):
        r = self.report()
        self.assertEqual(t.validate(self.profile(), r), [])
        r['workstreams'].pop()
        r['open_questions'] = ['Was the delivery accepted?']
        r['mission'] = 'Progress\u2014pending.'
        errors = t.validate(self.profile(), r)
        self.assertEqual(len(errors), 3)

    def test_approval_invalidates_after_edit(self):
        import subprocess
        import sys
        with tempfile.TemporaryDirectory() as root:
            p, r, d, a = [Path(root) / name for name in ('profile.json', 'report.json', 'draft.md', 'approval.json')]
            t.save(p, self.profile())
            t.save(r, self.report())
            d.write_text(t.render(self.profile(), self.report()))
            base = [sys.executable, str(Path(t.__file__))]
            args = ['--profile', str(p), '--report', str(r), '--draft', str(d), '--approval', str(a)]
            subprocess.run(base + ['approve'] + args + ['--user-approved'], check=True, capture_output=True)
            subprocess.run(base + ['check-approval'] + args, check=True, capture_output=True)
            changed = self.profile()
            changed['document_url'] = 'https://docs.google.com/document/d/other/edit'
            t.save(p, changed)
            self.assertNotEqual(subprocess.run(base + ['check-approval'] + args, capture_output=True).returncode, 0)
            d.write_text(d.read_text() + 'Manual edit\n')
            self.assertNotEqual(subprocess.run(base + ['approve'] + args + ['--user-approved'], capture_output=True).returncode, 0)


if __name__ == '__main__':
    unittest.main()
