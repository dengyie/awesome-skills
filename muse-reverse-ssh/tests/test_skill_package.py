import pathlib
import re
import shutil
import subprocess
import tempfile
import time
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class MuseReverseSshPackageTests(unittest.TestCase):
    def test_required_skill_files_are_present(self):
        required_paths = [
            ROOT / "SKILL.md",
            ROOT / "agents" / "openai.yaml",
            ROOT / "scripts" / "reverse-ssh-keepalive.sh",
            ROOT / "scripts" / "reverse-ssh-boot.service",
            ROOT.parent / "docs" / "usage" / "muse-reverse-ssh.md",
        ]
        missing = [
            str(path.relative_to(ROOT.parent))
            for path in required_paths
            if not path.exists()
        ]
        self.assertEqual(missing, [])

    def test_skill_frontmatter_and_metadata_are_aligned(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"---\n(.*?)\n---", skill_text, re.DOTALL)
        self.assertIsNotNone(match)
        frontmatter = match.group(1)

        self.assertIn("name: muse-reverse-ssh", frontmatter)
        self.assertIn("reverse SSH tunnel", frontmatter)

        metadata = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "Muse Reverse SSH"', metadata)
        self.assertIn("$muse-reverse-ssh", metadata)

    def test_core_safety_and_keepalive_are_documented(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for expected in [
            "GatewayPorts",
            "ExitOnForwardFailure",
            "ServerAliveInterval",
            "PasswordAuthentication no",
            "flock -n",  # still documented: as the thing NOT to use for long-lived supervisors
            "mkdir",  # atomic mkdir lockdir is the recommended single-instance guard
            "StrictHostKeyChecking",
        ]:
            self.assertIn(expected, skill_text)

    def test_boot_service_template_is_consistent(self):
        unit = ROOT / "scripts" / "reverse-ssh-boot.service"
        content = unit.read_text(encoding="utf-8")
        for expected in [
            "reverse-ssh-keepalive.sh",
            "Restart=always",
            "Environment=HOME=",
            "WantedBy=multi-user.target",
        ]:
            self.assertIn(expected, content)

    def test_boot_persistence_is_documented(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for expected in [
            "Boot Persistence",
            "reverse-ssh-boot.service",
            "@reboot",
            "Environment=HOME",
            "Layer 1",
            "Layer 2",
            "Layer 3",
            "autossh",
            "External watchdog",
            "VPS-side detection",
        ]:
            self.assertIn(expected, skill_text)

    def test_keepalive_script_is_valid_shell(self):
        script = ROOT / "scripts" / "reverse-ssh-keepalive.sh"
        content = script.read_text(encoding="utf-8")
        self.assertTrue(content.startswith("#!/bin/bash"))
        for expected in [
            "-R ",
            "ExitOnForwardFailure",
            "ServerAliveInterval",
            ".keepalive.lockdir",  # atomic mkdir lock, not flock (fd inheritance hazard)
            'mkdir "$LOCKDIR"',
            'ln "$LOCKDIR/claim.$$" "$LOCKDIR/info"',  # atomic claim, no clobber
            'mv -T "$LOCKDIR" "$stale"',  # atomic rename takeover, no reclaim mutex
            'lock_is_live "$stale"',  # re-verify AFTER the rename, not before
            'OWNER_CMDLINE="$(basename "$0")"',  # owner check must not hardcode the script name
            "lock ownership lost",  # main loop re-validates ownership every iteration
        ]:
            self.assertIn(expected, content)
        # No separate reclaim mutex anymore: the atomic rename IS the mutual
        # exclusion (the old mkdir mutex had a torn-claim race that let two
        # reclaimers delete a live holder's lockdir concurrently).
        self.assertNotIn(".keepalive.reclaim", content)
        self.assertNotIn("RECLAIMDIR", content)
        # bash -n: the template must at least parse.
        result = subprocess.run(
            ["bash", "-n", str(script)], capture_output=True, text=True, timeout=30
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_keepalive_has_no_age_based_reclaim(self):
        # A healthy supervisor runs for weeks, so its lock timestamp is always
        # old: an age rule would let any second instance steal the lock from a
        # healthy first one. Stale means dead pid / cmdline mismatch only.
        content = (ROOT / "scripts" / "reverse-ssh-keepalive.sh").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("LOCK_MAX_AGE", content)

    def test_production_pitfalls_are_documented(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for expected in [
            "the `sshd` binary itself is gone after a reboot",  # offline deb reinstall
            "ss -tnp",  # zombie tunnel: a live process does not mean a live tunnel
            "Never silence repair diagnostics",  # keep repair stderr in the log
        ]:
            self.assertIn(expected, skill_text)


class KeepaliveLockBehaviorTests(unittest.TestCase):
    """Behavioral tests for the keepalive's mkdir lock.

    The lock functions are extracted from the real template script and driven
    by small bash drivers, so these tests verify behavior (mutual exclusion,
    stale reclaim, liveness check) rather than string presence.
    """

    DRIVER_NAME = "reverse-ssh-keepalive-test-driver.sh"  # lock_is_live greps the cmdline for basename($0)

    def _write_harness(self, tmpdir):
        script = (ROOT / "scripts" / "reverse-ssh-keepalive.sh").read_text(
            encoding="utf-8"
        )
        start = script.index('LOCKDIR="${LOCKDIR:-')
        end = script.index("# --- end single-instance lock ---")
        lockfn = pathlib.Path(tmpdir) / "lockfn.sh"
        lockfn.write_text(script[start:end], encoding="utf-8")
        driver = pathlib.Path(tmpdir) / self.DRIVER_NAME
        # Production-fidelic holder: after acquiring, re-validate ownership
        # like the real keepalive's main loop does, and step down if the
        # claim is gone. A plain "sleep N" holder would never notice a
        # ghost-kill or a displaced lock, which is exactly what the
        # exactly-one-winner test is trying to exercise.
        driver.write_text(
            "#!/bin/bash\n"
            "set -u\n"
            f'STATE_DIR="{tmpdir}"\n'
            f'LOCKDIR="{tmpdir}/lockdir"\n'
            f'source "{lockfn}"\n'
            "lock_acquire\n"
            "rc=$?\n"
            'if [ "$rc" -eq 0 ]; then\n'
            '  echo "SURVIVED $$"\n'
            "  for i in $(seq 1 40); do\n"
            '    cur=$(cut -d" " -f1 < "$LOCKDIR/info" 2>/dev/null || true)\n'
            '    if [ "${cur:-}" != "$$" ]; then\n'
            '      echo "STEPPED-DOWN $$"\n'
            "      exit 0\n"
            "    fi\n"
            "    sleep 0.1\n"
            "  done\n"
            "fi\n"
            "exit 0\n",
            encoding="utf-8",
        )
        driver.chmod(0o755)
        return driver

    def _seed_stale_lock(self, tmpdir):
        lockdir = pathlib.Path(tmpdir) / "lockdir"
        lockdir.mkdir(parents=True, exist_ok=True)
        # pid 4194304 can never exist (above the kernel pid_max); the lock is
        # unambiguously stale no matter when the test runs.
        (lockdir / "info").write_text("4194304 1000000000\n", encoding="utf-8")

    def test_stale_lock_reclaim_has_exactly_one_winner(self):
        # 16 instances racing on a stale lock: exactly one ends up holding it.
        # (Earlier designs failed here: rm -rf + mkdir reclaim produced 4-5
        # simultaneous winners; a mkdir "reclaim mutex" still produced 3,
        # because its torn-claim race let two reclaimers rm -rf a live
        # holder's lockdir concurrently. The atomic-rename design caught two
        # more: a 0-winner liveness failure (a contender yielded to its own
        # moved-aside-and-back claim, and so did everyone else), and a
        # 2-winner safety failure (a reclaimer moved aside a live holder's
        # directory, a new contender claimed the fresh path before the move
        # back, and the blocked-in-ssh ghost never stepped down).
        #
        # "Winner" means a process that acquired the lock AND still holds it
        # at the end (no STEPPED-DOWN, exit 0): a ghost that printed SURVIVED
        # and was then terminated by the reclaim path does not count.
        # Each driver gets its own output file: 16 processes sharing one
        # file descriptor can clobber each other's lines via the shared
        # file offset.
        with tempfile.TemporaryDirectory() as tmpdir:
            driver = self._write_harness(tmpdir)
            self._seed_stale_lock(tmpdir)
            procs = []
            for i in range(16):
                out = open(pathlib.Path(tmpdir) / f"driver-{i}.out", "w",
                           encoding="utf-8")
                procs.append((
                    subprocess.Popen(
                        ["bash", str(driver)],
                        stdout=out,
                        stderr=subprocess.DEVNULL,
                    ),
                    out,
                    i,
                ))
            deadline = time.time() + 90
            for proc, out, _ in procs:
                remaining = max(1, deadline - time.time())
                try:
                    proc.wait(timeout=remaining)
                finally:
                    out.close()
            holders = []
            for proc, out, i in procs:
                text = (pathlib.Path(tmpdir) / f"driver-{i}.out").read_text(
                    encoding="utf-8"
                )
                if ("SURVIVED" in text and "STEPPED-DOWN" not in text
                        and proc.returncode == 0):
                    holders.append(text.strip().splitlines())
            self.assertEqual(len(holders), 1,
                             f"expected 1 final holder, got: {holders}")

    def test_contender_reclaims_own_abandoned_claim(self):
        # Regression test for a real concurrency failure (16 contenders, 0
        # winners): a contender whose mid-claim lockdir was moved aside by a
        # reclaimer and then moved *back* (the post-rename re-verification
        # found it live) used to see its own pid as "a live other holder" and
        # yield to itself - while every other contender yielded to it too, so
        # nobody ever held the lock. A claim naming our own pid must be
        # treated as stale *for us* and reclaimed.
        with tempfile.TemporaryDirectory() as tmpdir:
            script = (ROOT / "scripts" / "reverse-ssh-keepalive.sh").read_text(
                encoding="utf-8"
            )
            start = script.index('LOCKDIR="${LOCKDIR:-')
            end = script.index("# --- end single-instance lock ---")
            lockfn = pathlib.Path(tmpdir) / "lockfn.sh"
            lockfn.write_text(script[start:end], encoding="utf-8")
            probe = pathlib.Path(tmpdir) / "own-claim-probe.sh"
            probe.write_text(
                "#!/bin/bash\n"
                "set -u\n"
                f'STATE_DIR="{tmpdir}"\n'
                f'LOCKDIR="{tmpdir}/lockdir"\n'
                f'source "{lockfn}"\n'
                'mkdir -p "$LOCKDIR"\n'
                # simulate our own claim that a reclaimer moved aside and back
                'echo "$$ 1234567890" > "$LOCKDIR/info"\n'
                "lock_acquire\n"
                "rc=$?\n"
                'if [ "$rc" -eq 0 ]; then\n'
                '  echo "SURVIVED $$"\n'
                "fi\n"
                "exit 0\n",
                encoding="utf-8",
            )
            probe.chmod(0o755)
            result = subprocess.run(
                ["bash", str(probe)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(result.returncode, 0)
            self.assertIn("SURVIVED", result.stdout)
            self.assertNotIn("another keepalive instance running", result.stdout)

    def test_ghost_holder_is_terminated_when_move_back_fails(self):
        # Deterministic test for the 2-winner safety fix: when a reclaimer
        # moves aside a live holder's directory but cannot move it back
        # (a new contender claimed the fresh path in between), the original
        # owner is a ghost - still alive, but its directory is gone. It must
        # be terminated, otherwise it keeps supervising alongside the new
        # claimant (it can sit blocked in foreground ssh for hours, never
        # reaching its main-loop ownership check).
        with tempfile.TemporaryDirectory() as tmpdir:
            script = (ROOT / "scripts" / "reverse-ssh-keepalive.sh").read_text(
                encoding="utf-8"
            )
            start = script.index('LOCKDIR="${LOCKDIR:-')
            end = script.index("# --- end single-instance lock ---")
            lockfn = pathlib.Path(tmpdir) / "lockfn.sh"
            lockfn.write_text(script[start:end], encoding="utf-8")
            probe = pathlib.Path(tmpdir) / "ghost-probe.sh"
            probe.write_text(
                "#!/bin/bash\n"
                "set -u\n"
                f'STATE_DIR="{tmpdir}"\n'
                f'LOCKDIR="{tmpdir}/lockdir"\n'
                f'source "{lockfn}"\n'
                'if [ "${GHOST_MODE:-}" = "killer" ]; then\n'
                '  lock_displace_ghost "$STALE"\n'
                '  echo "killer done"\n'
                "  exit 0\n"
                "fi\n"
                "lock_acquire\n"
                'if [ "$?" -eq 0 ]; then\n'
                '  echo "SURVIVED $$"\n'
                # blocked holder: models a supervisor sitting in foreground
                # ssh, which never reaches its ownership re-validation.
                "  sleep 30\n"
                "fi\n"
                "exit 0\n",
                encoding="utf-8",
            )
            probe.chmod(0o755)
            # H becomes the holder. Its cmdline contains "ghost-probe.sh",
            # which is also basename($0) for the killer probe, so the
            # cmdline liveness check matches.
            holder = subprocess.Popen(
                ["bash", str(probe)],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                bufsize=1,
            )
            try:
                line = holder.stdout.readline()
                self.assertIn("SURVIVED", line)
                # Simulate the race: R moved H's directory aside, then a new
                # contender C claimed the fresh path, so the move-back fails.
                stale = pathlib.Path(tmpdir) / "lockdir.stale.99999"
                (pathlib.Path(tmpdir) / "lockdir").rename(stale)
                (pathlib.Path(tmpdir) / "lockdir").mkdir()
                killer = subprocess.run(
                    ["bash", str(probe)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    env={**dict(__import__("os").environ),
                         "GHOST_MODE": "killer",
                         "STALE": str(stale)},
                )
                self.assertEqual(killer.returncode, 0)
                self.assertIn("killer done", killer.stdout)
                self.assertIn("ghost holder", killer.stderr)
                # H (the ghost) must be gone, and its orphaned claim dir
                # must be cleaned up.
                holder.wait(timeout=10)
                self.assertIsNotNone(holder.returncode)
                self.assertFalse(stale.exists())
            finally:
                if holder.poll() is None:
                    holder.kill()
                    holder.wait(timeout=10)
                if holder.stdout:
                    holder.stdout.close()

    def test_live_lock_makes_contender_yield_quietly(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            driver = self._write_harness(tmpdir)
            holder = subprocess.Popen(
                ["bash", str(driver)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            try:
                time.sleep(1.0)  # let the holder acquire
                contender = subprocess.run(
                    ["bash", str(driver)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                self.assertEqual(contender.returncode, 0)
                self.assertIn("another keepalive instance running", contender.stdout)
                self.assertNotIn("SURVIVED", contender.stdout)
            finally:
                holder.terminate()
                holder.wait(timeout=10)
                if holder.stdout:
                    holder.stdout.close()

    def test_stale_lock_is_reclaimed_by_single_contender(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            driver = self._write_harness(tmpdir)
            self._seed_stale_lock(tmpdir)
            contender = subprocess.run(
                ["bash", str(driver)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(contender.returncode, 0)
            self.assertIn("SURVIVED", contender.stdout)
            # the winner's trap cleans up the lockdir on exit
            self.assertFalse((pathlib.Path(tmpdir) / "lockdir").exists())

    def test_tun_pattern_matches_only_real_tunnels(self):
        script = (ROOT / "scripts" / "reverse-ssh-keepalive.sh").read_text(
            encoding="utf-8"
        )
        match = re.search(r'^TUN_PATTERN="[^"]*"$', script, re.M)
        self.assertIsNotNone(match, "TUN_PATTERN assignment not found")
        bash_test = """
TUNNEL_KEY=/home/u/.ssh/tunnel-key
REMOTE_PORT=2222
VPS_USER=tunnel
@PATTERN@
pass=0; fail=0
check() {
  if [[ "$1" =~ $TUN_PATTERN ]]; then got=match; else got=nomatch; fi
  if [ "$got" = "$2" ]; then pass=$((pass+1)); else echo "FAIL: $3 (got $got)"; fail=$((fail+1)); fi
}
check 'ssh -i /home/u/.ssh/tunnel-key -o BatchMode=yes -N -R 2222:localhost:22 tunnel@203.0.113.10' match 'real tunnel'
check 'bash /home/u/.reverse-ssh/reverse-ssh-keepalive.sh' nomatch 'supervisor itself'
check 'ssh -i /home/u/.ssh/other-key mango@203.0.113.10' nomatch 'admin ssh session'
check 'ssh -i /home/u/.ssh/tunnel-key -N -R 9999:localhost:22 tunnel@203.0.113.10' nomatch 'different remote port'
[ "$fail" = 0 ]
""".replace("@PATTERN@", match.group(0))
        result = subprocess.run(
            ["bash", "-c", bash_test], capture_output=True, text=True, timeout=30
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    @unittest.skipUnless(shutil.which("shellcheck"), "shellcheck not installed")
    def test_shellcheck_is_clean(self):
        script = ROOT / "scripts" / "reverse-ssh-keepalive.sh"
        result = subprocess.run(
            ["shellcheck", "-S", "warning", str(script)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
