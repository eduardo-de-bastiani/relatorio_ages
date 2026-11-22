import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.migration_harness import url_reconciliation as urls
from scripts.migration_harness import recorda_deployment

ROOT = Path(__file__).resolve().parents[1]


class UrlReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        self.uid = 'chapter-06-text-h-0109'
        self.contract = json.loads((ROOT / urls.CONTRACT).read_text())
        self.spec = self.contract['units'][self.uid]
        for relative in (urls.CONTRACT, self.spec['tex_path']):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            data = (ROOT / relative).read_bytes()
            if relative == self.spec['tex_path']:
                approval = recorda_deployment.load(ROOT)
                data = recorda_deployment.previous_bytes(data, approval['files'][relative])
            path.write_bytes(data)
        ledger = json.loads((ROOT / 'migration/ledgers' / (self.uid + '.json')).read_text())
        self.unit = ledger['units'][self.uid]
        self.records = {c['source_id']: {'href': c['destination']} for c in self.spec['changes']}

    def test_exact_empty_and_visible_transformations_are_projected(self):
        projections = urls.load_unit(self.root, self.uid, self.unit, self.records)
        for change in self.spec['changes']:
            self.assertEqual(urls.project({'source_id': change['source_id']}, change['after'], projections), change['before'])
        self.assertIn('text-a-0148', self.spec['changes'][0]['after'])
        self.assertIn(self.spec['changes'][0]['destination'], self.spec['changes'][0]['after'])

    def test_destination_or_contract_tampering_fails(self):
        self.records['text-a-0149']['href'] += '/other'
        with self.assertRaises(ValueError):
            urls.load_unit(self.root, self.uid, self.unit, self.records)
        self.records['text-a-0149']['href'] = self.spec['changes'][1]['destination']
        path = self.root / urls.CONTRACT
        path.write_bytes(path.read_bytes() + b' ')
        with self.assertRaises(ValueError):
            urls.load_unit(self.root, self.uid, self.unit, self.records)

    def test_reindexed_tampered_anchor_still_fails(self):
        path = self.root / self.spec['tex_path']
        data = path.read_bytes().replace(b'Banco%20de%20Dados}', b'Banco%20de%20DadoX}', 1)
        path.write_bytes(data)
        digest = hashlib.sha256(data).hexdigest()
        for m in self.unit['element_map']:
            m['target_sha256'] = digest
        with self.assertRaises(ValueError):
            urls.load_unit(self.root, self.uid, self.unit, self.records)

    def test_local_alignment_is_exactly_scoped(self):
        uid = 'chapter-05-text-h-0078'
        spec = self.contract['units'][uid]
        source = (ROOT / spec['tex_path']).read_bytes()
        spans = urls.layout_group_spans(self.root, uid, source)
        self.assertEqual([source[a:b] for a, b in spans], [b'\\begingroup', b'\\endgroup'])
        self.assertEqual(hashlib.sha256(urls.previous_bytes(self.root, uid, source)).hexdigest(), spec['before_sha256'])
        with self.assertRaises(ValueError):
            urls.layout_group_spans(self.root, uid, source.replace(b'\\raggedright', b'\\raggedleft '))

    def test_prior_whole_file_requires_exact_successor(self):
        data = (self.root / self.spec['tex_path']).read_bytes()
        # Reconstruct the 11/11 successor before the separately approved
        # 18/11 caption shift. Its whole-file hash is still checked by the contract.
        data = data.replace(b"\\textbf{Figura 24 ", b"\\textbf{Figura 25 ", 1)
        old = urls.previous_bytes(self.root, self.uid, data)
        self.assertEqual(hashlib.sha256(old).hexdigest(), self.spec['before_sha256'])
        with self.assertRaises(ValueError):
            urls.previous_bytes(self.root, self.uid, data + b' ')

if __name__ == '__main__':
    unittest.main()
