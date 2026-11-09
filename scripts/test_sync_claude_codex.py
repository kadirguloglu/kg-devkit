#!/usr/bin/env python3
"""Claude bakım kaynaklarının Codex eşlemesini geçici depolarda doğrular.

Kullanım: python3 scripts/test_sync_claude_codex.py
Yalnız standart kütüphane; gerçek depoyu veya kullanıcı ayarlarını değiştirmez.
"""

import json
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROLES = {
    "kit-agent-linter",
    "kit-doc-sync",
    "kit-prompt-sync",
    "kit-release-notes",
}


class SyncClaudeCodexTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="kg-devkit-sync-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "repo with spaces"
        self.root.mkdir()
        shutil.copytree(ROOT / ".claude", self.root / ".claude")
        (self.root / "scripts").mkdir()
        self.script = self.root / "scripts/sync-claude-codex.py"
        shutil.copyfile(ROOT / "scripts/sync-claude-codex.py", self.script)

    def run_sync(self, *args, expected=0, cwd=None):
        result = subprocess.run(
            [sys.executable, str(self.script), *args],
            cwd=cwd or self.root,
            capture_output=True,
            text=True,
            timeout=20,
        )
        self.assertEqual(
            result.returncode,
            expected,
            f"args={args!r}\nstdout={result.stdout}\nstderr={result.stderr}",
        )
        return result

    def snapshot(self, path=None):
        directory = path or self.root / ".codex"
        if not directory.exists():
            return {}
        return {
            str(file.relative_to(directory)): (file.read_bytes(), file.stat().st_mtime_ns)
            for file in directory.rglob("*")
            if file.is_file()
        }

    def read_role(self, name):
        return tomllib.loads(
            (self.root / ".codex/agents" / f"{name}.toml").read_text()
        )

    def git(self, *args):
        return subprocess.run(
            ["git", *args],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
            timeout=20,
        ).stdout

    def test_real_roles_permissions_and_native_hook_registration(self):
        self.run_sync()
        outputs = self.root / ".codex"
        self.assertEqual({p.stem for p in (outputs / "agents").glob("*.toml")}, ROLES)
        for name in ROLES:
            with self.subTest(name=name):
                role = self.read_role(name)
                self.assertEqual(role["name"], name)
                self.assertTrue(role["description"])
                self.assertEqual(
                    role["sandbox_mode"],
                    "workspace-write" if name == "kit-prompt-sync" else "read-only",
                )
                body = role["developer_instructions"]
                self.assertIn("Full read (mandatory)", body)
                self.assertIn(f"{name} çalışmaya başladım.", body)
                self.assertIn(f"{name} çalışmam tamamlandı.", body)
                self.assertIn("spawn agents", body)
                self.assertNotIn(role.get("model"), {"sonnet", "opus"})

        hooks = json.loads((outputs / "hooks.json").read_text())
        commands = [
            item["command"]
            for group in hooks["hooks"]["Stop"]
            for item in group["hooks"]
        ]
        self.assertTrue(any(".codex/hooks/kit-review-gate.py" in c for c in commands))
        self.assertTrue(all("CLAUDE_PROJECT_DIR" not in c for c in commands))
        self.assertTrue((outputs / "hooks/kit-review-gate.py").is_file())
        json.loads((outputs / ".claude-sync.json").read_text())

    def test_body_quotes_backslashes_and_unicode_survive_toml_round_trip(self):
        source = self.root / ".claude/agents/kit-doc-sync.md"
        sentinel = '''
Round-trip sample: "quoted"; triple double """; triple single ''' + "'''" + r'''; path C:\temp\kit.
Regex: \\.(pyc|toml)$; Türkçe: ıİğĞşŞçÇöÖüÜ.
'''
        source.write_text(source.read_text() + sentinel)
        self.run_sync()
        self.assertIn(sentinel.strip(), self.read_role("kit-doc-sync")["developer_instructions"])

    def test_repeated_sync_is_idempotent_and_check_writes_nothing(self):
        self.run_sync()
        before = self.snapshot()
        self.run_sync()
        self.assertEqual(self.snapshot(), before)
        self.run_sync("--check")
        self.assertEqual(self.snapshot(), before)

    def test_source_update_is_detected_then_propagated(self):
        self.run_sync()
        source = self.root / ".claude/agents/kit-doc-sync.md"
        source.write_text(source.read_text() + "\nUpdated source requirement sentinel.\n")
        before = self.snapshot()
        self.run_sync("--check", expected=1)
        self.assertEqual(self.snapshot(), before)
        self.run_sync()
        self.assertIn(
            "Updated source requirement sentinel.",
            self.read_role("kit-doc-sync")["developer_instructions"],
        )
        self.run_sync("--check")

    def test_missing_output_check_does_not_recreate_output(self):
        self.run_sync()
        missing = self.root / ".codex/agents/kit-doc-sync.toml"
        missing.unlink()
        before = self.snapshot()
        self.run_sync("--check", expected=1)
        self.assertEqual(self.snapshot(), before)
        self.assertFalse(missing.exists())
        self.run_sync()
        self.assertTrue(missing.exists())

    def test_deleted_source_removes_only_its_managed_output(self):
        self.run_sync()
        custom = self.root / ".codex/agents/custom.toml"
        custom.write_text('name = "custom"\n')
        (self.root / ".claude/agents/kit-release-notes.md").unlink()
        self.run_sync("--check", expected=1)
        self.run_sync()
        self.assertFalse((self.root / ".codex/agents/kit-release-notes.toml").exists())
        self.assertEqual(custom.read_text(), 'name = "custom"\n')
        self.assertTrue((self.root / ".codex/agents/kit-doc-sync.toml").exists())

    def test_unmanaged_files_and_configuration_are_preserved(self):
        custom = self.root / ".codex/agents/custom.toml"
        custom.parent.mkdir(parents=True)
        custom.write_text('name = "custom"\n')
        config = self.root / ".codex/config.toml"
        config.write_text('[features]\nexample = false\n')
        self.run_sync()
        self.assertEqual(custom.read_text(), 'name = "custom"\n')
        self.assertEqual(config.read_text(), '[features]\nexample = false\n')
        self.run_sync("--check")

    def test_unmanaged_hook_file_collision_is_not_overwritten(self):
        hooks = self.root / ".codex/hooks.json"
        hooks.parent.mkdir()
        hooks.write_text('{"hooks": {}, "user_setting": true}\n')
        before = self.snapshot()
        self.run_sync(expected=1)
        self.assertEqual(self.snapshot(), before)

    def test_locally_modified_generated_file_blocks_partial_updates(self):
        self.run_sync()
        local = self.root / ".codex/agents/kit-doc-sync.toml"
        local.write_text(local.read_text() + "\n# A local user change.\n")
        source = self.root / ".claude/agents/kit-agent-linter.md"
        source.write_text(source.read_text() + "\nA different pending update.\n")
        before = self.snapshot()
        self.run_sync(expected=1)
        self.assertEqual(self.snapshot(), before)

    def test_invalid_agent_name_is_transactional(self):
        self.run_sync()
        first = self.root / ".claude/agents/kit-agent-linter.md"
        first.write_text(first.read_text() + "\nPending valid update.\n")
        last = self.root / ".claude/agents/kit-release-notes.md"
        last.write_text(last.read_text().replace("name: kit-release-notes", "name: wrong-name", 1))
        before = self.snapshot()
        self.run_sync(expected=1)
        self.assertEqual(self.snapshot(), before)

    def test_unknown_source_file_is_reported_without_writes(self):
        self.run_sync()
        (self.root / ".claude/new-unsupported-config.json").write_text("{}\n")
        before = self.snapshot()
        self.run_sync(expected=1)
        self.assertEqual(self.snapshot(), before)

    def test_unknown_settings_are_reported_without_writes(self):
        self.run_sync()
        settings = self.root / ".claude/settings.json"
        data = json.loads(settings.read_text())
        data["unsupportedNewSetting"] = True
        settings.write_text(json.dumps(data))
        before = self.snapshot()
        self.run_sync(expected=1)
        self.assertEqual(self.snapshot(), before)

    def test_running_from_another_working_directory_uses_script_root(self):
        other = Path(self.tmp.name) / "unrelated"
        other.mkdir()
        self.run_sync(cwd=other)
        self.assertTrue((self.root / ".codex/agents/kit-doc-sync.toml").is_file())
        self.assertFalse((other / ".codex").exists())
        self.run_sync("--check", cwd=other)

    def test_watch_generates_initial_outputs_and_propagates_source_change(self):
        process = subprocess.Popen(
            [sys.executable, str(self.script), "--watch"],
            cwd=self.root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        output = self.root / ".codex/agents/kit-doc-sync.toml"

        def wait_for_output(predicate):
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    stdout, stderr = process.communicate(timeout=1)
                    self.fail(f"Watcher exited early: {stdout}\n{stderr}")
                if predicate():
                    return
                time.sleep(0.05)
            self.fail("Watcher did not produce the expected output within 5 seconds")

        try:
            wait_for_output(output.is_file)
            source = self.root / ".claude/agents/kit-doc-sync.md"
            updated = self.root / "updated-source.md"
            updated.write_text(source.read_text() + "\nWatch update sentinel.\n")
            updated.replace(source)
            wait_for_output(lambda: "Watch update sentinel." in output.read_text())
        finally:
            if process.poll() is None:
                process.send_signal(signal.SIGINT)
            try:
                process.communicate(timeout=3)
            except subprocess.TimeoutExpired:
                process.terminate()
                try:
                    process.communicate(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.communicate(timeout=3)
        self.assertEqual(process.returncode, 0)
        self.run_sync("--check")

    def test_symlink_output_cannot_escape_repository(self):
        outside = Path(self.tmp.name) / "outside-output"
        outside.mkdir()
        sentinel = outside / "keep.txt"
        sentinel.write_text("User-owned external directory.\n")
        codex = self.root / ".codex"
        codex.mkdir()
        (codex / "agents").symlink_to(outside, target_is_directory=True)
        before = self.snapshot(outside)
        self.run_sync(expected=1)
        self.assertEqual(self.snapshot(outside), before)
        self.assertEqual({p.name for p in codex.iterdir()}, {"agents"})
        self.assertTrue((codex / "agents").is_symlink())

    def test_hook_source_updates_are_propagated(self):
        self.run_sync()
        source = self.root / ".claude/hooks/kit-review-gate.py"
        marker = "# Updated source hook comment sentinel."
        source.write_text(source.read_text() + "\n" + marker + "\n")
        self.run_sync("--check", expected=1)
        self.run_sync()
        generated = self.root / ".codex/hooks/kit-review-gate.py"
        self.assertIn(marker, generated.read_text())
        self.run_sync("--check")

    def test_native_hook_clean_changed_repeat_and_separate_client_state(self):
        fixture = self.root / "plugins/kg-devkit/agents/example.md"
        fixture.parent.mkdir(parents=True)
        fixture.write_text("Example plugin agent baseline.\n")
        (self.root / "README.md").write_text("Example repository.\n")
        (self.root / "CHANGELOG.md").write_text("Existing release.\n")
        self.run_sync()
        self.git("init", "-q")
        self.git("add", ".")
        self.git(
            "-c", "user.name=Sync Test", "-c", "user.email=sync-test@example.invalid",
            "-c", "commit.gpgsign=false", "commit", "-qm", "Fixture baseline",
        )
        claude_state = self.root / ".git/kit-review-gate/state.json"
        claude_state.parent.mkdir(parents=True)
        claude_state.write_text('{"claude_state_sentinel": true}\n')

        def run_hook(native_command=False):
            if native_command:
                hooks = json.loads((self.root / ".codex/hooks.json").read_text())
                command = hooks["hooks"]["Stop"][0]["hooks"][0]["command"]
                working_directory = fixture.parent
            else:
                command = [sys.executable, str(self.root / ".codex/hooks/kit-review-gate.py")]
                working_directory = self.root
            result = subprocess.run(
                command,
                shell=native_command,
                cwd=working_directory,
                input=json.dumps({
                    "hook_event_name": "Stop", "cwd": str(working_directory),
                    "stop_hook_active": False,
                }),
                capture_output=True,
                text=True,
                timeout=20,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout) if result.stdout.strip() else {}

        self.assertNotEqual(run_hook().get("decision"), "block")
        fixture.write_text("Changed plugin agent behavior.\n")
        response = run_hook()
        self.assertEqual(response.get("decision"), "block")
        for name in ROLES:
            self.assertIn(name, response.get("reason", ""))
        self.assertNotEqual(run_hook().get("decision"), "block")
        fixture.write_text("Another plugin agent change, checked through hooks.json.\n")
        response = run_hook(native_command=True)
        self.assertEqual(response.get("decision"), "block")
        self.assertIn("kit-agent-linter", response.get("reason", ""))
        self.assertNotEqual(run_hook(native_command=True).get("decision"), "block")
        self.assertEqual(claude_state.read_text(), '{"claude_state_sentinel": true}\n')


if __name__ == "__main__":
    unittest.main(verbosity=2)
