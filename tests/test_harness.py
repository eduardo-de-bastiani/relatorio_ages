import json
import io
from contextlib import redirect_stdout
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from migration_harness.build import audit_log, _copy_sources, compile_profile
from migration_harness.common import safe_relative, sha256, require_work_branch
from migration_harness.coordination import scope_check, resource_locks, run_task, checkpoint
from migration_harness.environment import check_lock, REQUIRED
from migration_harness import cli


class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.repo = Path(self.temporary.name)
        self.run_git("init", "-b", "harness/test")
        (self.repo / "docs").mkdir()
        (self.repo / "RELATORIO_ATUAL.odt").write_bytes(b"frozen test source")
        (self.repo / ".gitignore").write_text("/build/\n")
        self.config = {"phase": "harness", "source": "RELATORIO_ATUAL.odt",
                       "manifest": "docs/CONTENT_MANIFEST.json", "destination_root": "destination",
                       "roles": {"orchestrator": {"write": ["docs/*"], "locks": ["integration"]},
                                 "extractor": {"write": ["docs/CONTENT_MANIFEST.json"], "locks": ["manifest"]},
                                 "converter": {"write": [], "locks": ["unit:{unit}"]}}}
        (self.repo / "harness.json").write_text(json.dumps(self.config))
        (self.repo / "docs/CONTENT_MANIFEST.json").write_text(json.dumps({"units": [{"id": "u", "destination": "destination/u.tex"}]}))
        (self.repo / "docs/BASELINE.json").write_text(json.dumps({"protected_files": {"RELATORIO_ATUAL.odt": sha256(self.repo / "RELATORIO_ATUAL.odt")}}))
        self.run_git("add", ".")
        self.run_git("-c", "user.name=Harness test", "-c", "user.email=harness@example.org", "commit", "-m", "test baseline")

    def tearDown(self):
        self.temporary.cleanup()

    def run_git(self, *args):
        return subprocess.run(["git", "-C", str(self.repo), *args], check=True, capture_output=True)

    def test_path_escape_and_main_rejected(self):
        with self.assertRaises(ValueError):
            safe_relative(self.repo, "../escape")
        self.run_git("branch", "-m", "main")
        with self.assertRaises(ValueError):
            require_work_branch(self.repo)

    def test_missing_manifest_is_a_structured_failure(self):
        self.config["toolchain_lock"] = "docs/TOOLCHAIN.lock.json"
        (self.repo / "harness.json").write_text(json.dumps(self.config))
        (self.repo / "docs/CONTENT_MANIFEST.json").unlink()
        output = io.StringIO()
        with patch.object(cli, "REPO", self.repo), redirect_stdout(output):
            status = cli.main(["inventory", "--check"])
        report = json.loads(output.getvalue())
        self.assertEqual(status, 1)
        self.assertEqual(report["status"], "fail")
        self.assertIsNone(report["execution"]["manifest_sha256"])

    def test_extractor_owns_manifest_even_against_broad_doc_pattern(self):
        (self.repo / "docs/CONTENT_MANIFEST.json").write_text('{"units": []}')
        self.assertEqual(scope_check("orchestrator", "HEAD", repo=self.repo)["status"], "fail")
        self.assertEqual(scope_check("extractor", "HEAD", repo=self.repo)["status"], "pass")

    def test_source_never_allowed(self):
        self.config["roles"]["orchestrator"]["write"].append("*")
        (self.repo / "harness.json").write_text(json.dumps(self.config))
        (self.repo / "RELATORIO_ATUAL.odt").write_bytes(b"changed")
        self.assertIn("RELATORIO_ATUAL.odt", scope_check("orchestrator", "HEAD", repo=self.repo)["forbidden_paths"])

    def test_converter_cannot_run_during_harness(self):
        with self.assertRaisesRegex(ValueError, "not authorized"):
            run_task("converter", [sys.executable, "-c", "pass"], unit="u", repo=self.repo)

    def test_lock_collision(self):
        with resource_locks(["manifest"], repo=self.repo):
            with self.assertRaisesRegex(ValueError, "already owned"):
                with resource_locks(["manifest"], repo=self.repo):
                    pass

    def test_checkpoint_never_manufactures_approval(self):
        result = checkpoint("u", repo=self.repo)
        self.assertEqual(result["status"], "pending_human_approval")
        self.assertIsNone(result["approval"])
        self.assertFalse(result["pilot_authorized"])
        with self.assertRaises(ValueError):
            checkpoint("../../../escape", repo=self.repo)

    def test_failed_preflight_invalidates_old_pass_artifacts(self):
        output = self.repo / "build/document"
        output.mkdir(parents=True)
        for name in ["main.pdf", "main.bbl", "main.toc", "main.bcf", "report.json"]:
            (output / name).write_text("stale")
        report = compile_profile("document", repo=self.repo)
        self.assertEqual(report["status"], "unconverted")
        self.assertEqual({p.name for p in output.iterdir()}, {"report.json"})
        self.assertEqual(json.loads((output / "report.json").read_text())["status"], "unconverted")

    def test_task_cannot_switch_to_main(self):
        self.run_git("branch", "main")
        with self.assertRaises(ValueError):
            run_task("extractor", ["git", "switch", "-q", "main"], repo=self.repo)

    def test_production_build_requires_frozen_commit(self):
        source = self.repo / "relatorio_AGES_eduardo"
        source.mkdir()
        (source / "main.tex").write_text("synthetic uncommitted source")
        report = compile_profile("document", repo=self.repo)
        self.assertEqual(report["status"], "fail")
        self.assertEqual(report["findings"][0]["code"], "UNCOMMITTED_DOCUMENT")

    def test_child_cli_can_use_parent_owned_lock(self):
        module_root = str(Path(__file__).resolve().parents[1] / "scripts")
        code = ("import sys; from pathlib import Path; "
                f"sys.path.insert(0, {module_root!r}); "
                "from migration_harness.coordination import resource_locks; "
                "lease=resource_locks(['manifest'],repo=Path.cwd()); "
                "lease.__enter__(); lease.__exit__(None,None,None)")
        self.assertEqual(run_task("extractor", [sys.executable, "-c", code], repo=self.repo)["status"], "pass")

    def test_clean_trusted_readonly_task_and_scope_violation(self):
        self.assertEqual(run_task("extractor", [sys.executable, "-c", "pass"], repo=self.repo)["status"], "pass")
        result = run_task("extractor", [sys.executable, "-c", "from pathlib import Path; Path('wrong.txt').write_text('x')"], repo=self.repo)
        self.assertEqual(result["status"], "fail")
        self.assertIn("wrong.txt", result["scope"]["forbidden_paths"])

    def test_final_log_errors_and_warnings_block(self):
        for message in ["Missing character: x", "Overfull \\hbox (2pt)", "Package test Warning: issue", "Reference `x' undefined"]:
            with self.subTest(message=message):
                self.assertEqual(audit_log(message)["status"], "fail")
        self.assertEqual(audit_log("Output written on main.pdf")["status"], "pass")
        self.assertEqual(audit_log("", biber_log="WARN - Missing field")["status"], "fail")
        self.assertEqual(audit_log("", compiler_output="warning: Object @page.1 already defined.")["status"], "fail")

    def test_toolchain_and_cache_drift(self):
        locked = {"commands": {k: {"version": "1"} for k in REQUIRED}, "python": "3.12", "cache_resources": {"x": "abc"}}
        actual = json.loads(json.dumps(locked))
        self.assertEqual(check_lock(actual, locked), [])
        actual["cache_resources"]["x"] = "changed"
        self.assertEqual(check_lock(actual, locked)[0]["code"], "CACHE_DRIFT")

    def test_isolated_copy_excludes_stale_artifacts(self):
        source, output = self.repo / "src", self.repo / "out"
        source.mkdir(); output.mkdir()
        for name in ["main.tex", "main.aux", "main.bbl", "main.pdf", "image.png"]:
            (source / name).write_bytes(b"test")
        _copy_sources(source, output)
        self.assertEqual({p.name for p in output.iterdir()}, {"main.tex", "image.png"})


if __name__ == "__main__":
    unittest.main()
