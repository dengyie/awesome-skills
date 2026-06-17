from __future__ import annotations

import json
import pathlib
import re
import subprocess
from datetime import datetime
from typing import Dict, Iterable, List


HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
SECTION_RE = re.compile(r"^##\s+(?P<title>.+?)\s*$")
LEADING_LIST_MARKER_RE = re.compile(r"^-\s*(?:\[[ xX]\]\s*)?")
WORKSTREAM_MATCH_STOPWORDS = {
    "and",
    "best",
    "branch",
    "change",
    "changes",
    "code",
    "context",
    "current",
    "file",
    "files",
    "integration",
    "memory",
    "phase",
    "production",
    "project",
    "quality",
    "review",
    "script",
    "skill",
    "state",
    "stream",
    "test",
    "tests",
    "todo",
    "update",
    "workstream",
}
TODO_SECTION_RE = re.compile(r"^##\s+(In Progress|Next|Done)\s*$", re.MULTILINE)


def run_git(repo: pathlib.Path, args: List[str], check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=check,
        capture_output=True,
        text=True,
    )
    return result.stdout


def git_ref_exists(repo: pathlib.Path, ref_name: str) -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--verify", ref_name],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def get_current_branch(repo: pathlib.Path) -> str:
    return run_git(repo, ["branch", "--show-current"], check=False).strip()


def infer_base_ref(repo: pathlib.Path) -> str:
    branch = get_current_branch(repo)
    candidates = dedupe_keep_order(
        [
            get_remote_default_branch(repo),
            "origin/main",
            "origin/master",
            "origin/develop",
            "origin/trunk",
            "main",
            "master",
            "develop",
            "trunk",
        ]
    )

    for candidate in candidates:
        if not candidate:
            continue
        if not git_ref_exists(repo, candidate):
            continue
        if branch and branch == candidate.split("/")[-1]:
            continue
        merge_base = run_git(repo, ["merge-base", "HEAD", candidate], check=False).strip()
        if merge_base:
            return candidate

    return "HEAD"


def get_remote_default_branch(repo: pathlib.Path) -> str:
    remote_head = run_git(
        repo,
        ["symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"],
        check=False,
    ).strip()
    return remote_head


def normalize_scope_mode(scope_mode: str | None) -> str | None:
    if scope_mode is None:
        return None
    if scope_mode not in {"branch", "working_tree"}:
        raise ValueError(f"Unsupported scope mode: {scope_mode}")
    return scope_mode


def get_status_buckets(repo: pathlib.Path) -> Dict[str, List[str]]:
    raw = run_git(repo, ["status", "--short"], check=False)
    staged: List[str] = []
    unstaged: List[str] = []
    untracked: List[str] = []

    for line in raw.splitlines():
        if not line.strip():
            continue
        status = line[:2]
        path = line[3:].strip()
        if "->" in path:
            path = path.split("->", 1)[1].strip()
        if status == "??":
            untracked.append(path)
            continue
        if status[0] != " ":
            staged.append(path)
        if status[1] != " ":
            unstaged.append(path)

    return {
        "staged": sorted(set(staged)),
        "unstaged": sorted(set(unstaged)),
        "untracked": sorted(set(untracked)),
    }


def get_base_changed_files(repo: pathlib.Path, base_ref: str) -> List[str]:
    if base_ref == "HEAD":
        diff_output = run_git(repo, ["diff", "--name-only", "HEAD"], check=False)
    else:
        merge_base = run_git(repo, ["merge-base", "HEAD", base_ref], check=False).strip()
        diff_output = run_git(repo, ["diff", "--name-only", f"{merge_base}...HEAD"], check=False)

    return sorted(expand_repo_paths(repo, filter(None, diff_output.splitlines())))


def get_changed_files(repo: pathlib.Path, base_ref: str, include_worktree: bool = True) -> List[str]:
    files = set(get_base_changed_files(repo, base_ref))
    if not include_worktree:
        return sorted(files)

    status = get_status_buckets(repo)
    files.update(status["staged"])
    files.update(status["unstaged"])
    files.update(status["untracked"])
    return sorted(expand_repo_paths(repo, files))


def get_diff_text(repo: pathlib.Path, base_ref: str) -> str:
    if base_ref == "HEAD":
        return run_git(repo, ["diff", "--unified=0", "HEAD"], check=False)

    merge_base = run_git(repo, ["merge-base", "HEAD", base_ref], check=False).strip()
    return run_git(repo, ["diff", "--unified=0", f"{merge_base}...HEAD"], check=False)


def get_worktree_diff_text(repo: pathlib.Path) -> str:
    return run_git(repo, ["diff", "--unified=0", "HEAD"], check=False)


def get_scope_diff_text(
    repo: pathlib.Path,
    base_ref: str,
    *,
    include_worktree: bool,
    status: Dict[str, List[str]],
) -> str:
    if not include_worktree:
        return get_diff_text(repo, base_ref)

    diff_parts: List[str] = []
    if base_ref == "HEAD":
        diff_parts.append(get_worktree_diff_text(repo))
    else:
        diff_parts.append(get_diff_text(repo, base_ref))
        diff_parts.append(get_worktree_diff_text(repo))

    untracked_paths = expand_repo_paths(repo, status.get("untracked", []))
    diff_parts.append(build_untracked_diff_text(repo, untracked_paths))
    return "\n".join(part for part in diff_parts if part)


def build_untracked_diff_text(repo: pathlib.Path, paths: Iterable[str]) -> str:
    diff_parts: List[str] = []
    for path in paths:
        repo_path = repo / path
        if not repo_path.is_file():
            continue
        try:
            text = repo_path.read_text()
        except UnicodeDecodeError:
            continue
        lines = text.splitlines()
        if not lines:
            continue
        diff_parts.append(f"diff --git a/{path} b/{path}")
        diff_parts.append("new file mode 100644")
        diff_parts.append("--- /dev/null")
        diff_parts.append(f"+++ b/{path}")
        diff_parts.append(f"@@ -0,0 +1,{len(lines)} @@")
        diff_parts.extend(f"+{line}" for line in lines)
    return "\n".join(diff_parts)


def parse_unified_zero_diff(diff_text: str) -> Dict[str, Dict[str, List[Dict[str, int]]]]:
    result: Dict[str, Dict[str, List[Dict[str, int]]]] = {}
    current_file: str | None = None

    for line in diff_text.splitlines():
        if line.startswith("+++ "):
            file_name = line[4:].strip()
            if file_name == "/dev/null":
                current_file = None
                continue
            current_file = file_name[2:] if file_name.startswith("b/") else file_name
            result.setdefault(current_file, {"added": [], "deleted": []})
            continue

        match = HUNK_RE.match(line)
        if not match or current_file is None:
            continue

        old_start = int(match.group(1))
        old_count = int(match.group(2) or "1")
        new_start = int(match.group(3))
        new_count = int(match.group(4) or "1")

        if new_count > 0:
            result[current_file]["added"].append(
                {"start": new_start, "end": new_start + new_count - 1}
            )
        if old_count > 0:
            result[current_file]["deleted"].append(
                {"start": old_start, "end": old_start + old_count - 1}
            )

    return result


def detect_stack(paths: Iterable[str]) -> Dict[str, List[str]]:
    path_list = list(paths)
    lower_paths = [path.lower() for path in path_list]

    detected: List[str] = []

    def add_stack(name: str) -> None:
        if name not in detected:
            detected.append(name)

    for path in lower_paths:
        if path.endswith((".ts", ".tsx")) or path == "tsconfig.json":
            add_stack("typescript")
        if path.endswith((".js", ".cjs", ".mjs")) or path == "package.json":
            add_stack("node")
        if path.endswith(".py") or path in {"pyproject.toml", "requirements.txt", "poetry.lock"}:
            add_stack("python")
        if path.endswith(".go") or path == "go.mod":
            add_stack("go")
        if path.endswith((".sql", ".sqlite")) or "migration" in path or "schema.prisma" in path:
            add_stack("database")
        if path.endswith("dockerfile") or "docker-compose" in path or path == "compose.yaml":
            add_stack("docker")

    if any(path.endswith((".jsx", ".tsx")) for path in lower_paths):
        add_stack("frontend")

    reference_map = {
        "typescript": "typescript.md",
        "node": "backend-and-integrations.md",
        "python": "python.md",
        "database": "database.md",
        "docker": "review-framework.md",
        "frontend": "typescript.md",
    }

    suggested = []
    for core_reference in ["review-framework.md", "output-contract.md", "false-positive-control.md"]:
        suggested.append(core_reference)
    for stack in detected:
        mapped = reference_map.get(stack)
        if mapped and mapped not in suggested:
            suggested.append(mapped)

    if any(stack in detected for stack in ["typescript", "node", "python", "docker"]):
        suggested.append("verification-and-operations.md")

    return {
        "detected_stack": detected,
        "suggested_references": dedupe_keep_order(suggested),
    }


def derive_risk_flags(paths: Iterable[str], diff_text: str) -> List[str]:
    lower_paths = [path.lower() for path in paths]
    flags: List[str] = []

    def add_flag(flag: str) -> None:
        if flag not in flags:
            flags.append(flag)

    if any(token in path for path in lower_paths for token in ["auth", "permission", "policy", "acl", "session"]):
        add_flag("auth_or_access_control")
    if any(token in path for path in lower_paths for token in ["payment", "billing", "invoice", "stripe"]):
        add_flag("payments_or_billing")
    if any("migration" in path or path.endswith(".sql") or "schema.prisma" in path for path in lower_paths):
        add_flag("database_migration")
    if any(path.startswith(".github/workflows/") or "deploy" in path or "release" in path for path in lower_paths):
        add_flag("ci_cd_or_deploy")
    if any(path.endswith("dockerfile") or "docker-compose" in path or path == "compose.yaml" for path in lower_paths):
        add_flag("container_or_runtime")
    if any(token in path for path in lower_paths for token in ["api", "client", "http", "webhook"]):
        add_flag("api_or_network_boundary")
    if "fetch(" in diff_text or "axios" in diff_text or "requests." in diff_text:
        add_flag("api_or_network_boundary")
    if any(token in diff_text.lower() for token in ["logger", "metric", "trace", "span"]):
        add_flag("observability_change")

    return flags


def augment_references_for_risks(
    suggested_references: Iterable[str], risk_flags: Iterable[str]
) -> List[str]:
    references = list(suggested_references)
    flags = set(risk_flags)

    if "api_or_network_boundary" in flags:
        references.append("backend-and-integrations.md")
    if "auth_or_access_control" in flags or "payments_or_billing" in flags:
        references.append("security.md")
    if "database_migration" in flags:
        references.append("database.md")
    if flags:
        references.append("verification-and-operations.md")

    return dedupe_keep_order(references)


def build_safe_check_commands(
    detected_stack: Iterable[str],
    *,
    repo: pathlib.Path | None = None,
    repo_files: Iterable[str] | None = None,
) -> List[Dict[str, str]]:
    commands: List[Dict[str, str]] = []
    stack_list = list(detected_stack)
    file_list = list(repo_files or [])

    def add(command: str, reason: str) -> None:
        if not any(item["command"] == command for item in commands):
            commands.append({"command": command, "reason": reason})

    if "typescript" in stack_list or "node" in stack_list:
        package_manager = detect_js_package_manager(file_list)
        scripts = read_package_scripts(repo) if repo else None
        add_js_script_command(
            add,
            package_manager,
            scripts,
            "test",
            "Verify changed behavior and regression coverage.",
        )
        add_js_script_command(
            add,
            package_manager,
            scripts,
            "lint",
            "Catch static correctness and convention issues.",
        )
        add_js_script_command(
            add,
            package_manager,
            scripts,
            "typecheck",
            "Catch unsafe contract and type regressions.",
        )
        add_js_script_command(
            add,
            package_manager,
            scripts,
            "build",
            "Verify compile and packaging health.",
        )
    if "python" in stack_list:
        if repo and prefers_pytest(repo, file_list):
            add("python3 -m pytest", "Run Python pytest coverage for changed behavior.")
        else:
            add("python3 -m unittest discover", "Run Python test coverage for changed behavior.")
        if repo and uses_ruff(repo, file_list):
            add("python3 -m ruff check .", "Run configured Python lint checks.")
        if repo and uses_mypy(repo, file_list):
            add("python3 -m mypy .", "Run configured Python type checks.")
    if "go" in stack_list:
        add("go test ./...", "Run Go unit and package tests.")
    if "docker" in stack_list:
        add("docker compose config", "Validate container configuration without mutation.")

    return commands


def detect_js_package_manager(repo_files: Iterable[str]) -> str:
    files = {path.lower() for path in repo_files}
    if "pnpm-lock.yaml" in files or "pnpm-workspace.yaml" in files:
        return "pnpm"
    if "yarn.lock" in files:
        return "yarn"
    if "bun.lock" in files or "bun.lockb" in files:
        return "bun"
    return "npm"


def read_package_scripts(repo: pathlib.Path | None) -> Dict[str, str] | None:
    if repo is None:
        return None
    package_json = repo / "package.json"
    if not package_json.exists():
        return None
    try:
        payload = json.loads(package_json.read_text())
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    scripts = payload.get("scripts")
    if not isinstance(scripts, dict):
        return None
    return {str(key): str(value) for key, value in scripts.items()}


def add_js_script_command(
    add,
    package_manager: str,
    scripts: Dict[str, str] | None,
    script_name: str,
    reason: str,
) -> None:
    if scripts is not None and script_name not in scripts:
        return
    if package_manager == "npm":
        command = "npm test" if script_name == "test" else f"npm run {script_name}"
    elif package_manager == "pnpm":
        command = f"pnpm {script_name}"
    elif package_manager == "yarn":
        command = f"yarn {script_name}"
    elif package_manager == "bun":
        if script_name == "test":
            command = "bun run test" if scripts is not None else "bun test"
        else:
            command = f"bun run {script_name}"
    else:
        command = f"{package_manager} {script_name}"
    add(command, reason)


def prefers_pytest(repo: pathlib.Path, repo_files: Iterable[str]) -> bool:
    files = {path.lower() for path in repo_files}
    if "pytest.ini" in files or "conftest.py" in files:
        return True
    pyproject = repo / "pyproject.toml"
    if pyproject.exists():
        text = read_text_safely(pyproject)
        if "[tool.pytest" in text or "pytest" in text:
            return True
    requirements = repo / "requirements.txt"
    if requirements.exists() and "pytest" in read_text_safely(requirements).lower():
        return True
    return False


def uses_ruff(repo: pathlib.Path, repo_files: Iterable[str]) -> bool:
    files = {path.lower() for path in repo_files}
    if "ruff.toml" in files or ".ruff.toml" in files:
        return True
    pyproject = repo / "pyproject.toml"
    return pyproject.exists() and "[tool.ruff" in read_text_safely(pyproject)


def uses_mypy(repo: pathlib.Path, repo_files: Iterable[str]) -> bool:
    files = {path.lower() for path in repo_files}
    if "mypy.ini" in files or ".mypy.ini" in files:
        return True
    pyproject = repo / "pyproject.toml"
    return pyproject.exists() and "[tool.mypy" in read_text_safely(pyproject)


def read_text_safely(path: pathlib.Path) -> str:
    try:
        return path.read_text()
    except UnicodeDecodeError:
        return ""


def select_review_mode(
    changed_files: Iterable[str], risk_flags: Iterable[str]
) -> Dict[str, List[str] | str]:
    files = list(changed_files)
    flags = list(risk_flags)

    high_risk_flags = {
        "auth_or_access_control",
        "payments_or_billing",
        "database_migration",
        "ci_cd_or_deploy",
        "container_or_runtime",
        "api_or_network_boundary",
    }
    high_risk_hit = bool(high_risk_flags.intersection(flags))
    large_diff_hit = len(files) >= 8
    specialist_mode = high_risk_hit or large_diff_hit

    if specialist_mode:
        reviewers = ["correctness", "reliability", "security", "tests"]
        if len(files) >= 4 or "database_migration" in flags:
            reviewers.insert(1, "architecture")
        if high_risk_hit:
            reason = "high-risk change touches sensitive production surfaces"
            risk_level = "high"
        else:
            reason = "large diff benefits from specialist review split"
            risk_level = "medium"
        return {
            "mode": "specialist",
            "reviewers": dedupe_keep_order(reviewers),
            "follow_up": ["synthesizer"],
            "risk_level": risk_level,
            "review_mode_reason": reason,
        }

    return {
        "mode": "single",
        "reviewers": ["primary-reviewer"],
        "follow_up": [],
        "risk_level": "low" if len(files) <= 3 and not flags else "medium",
        "review_mode_reason": "small local change fits a single production-minded pass",
    }


def build_review_brief_markdown(context: Dict[str, object]) -> str:
    review_plan = context.get("review_plan") or select_review_mode(
        changed_files=context.get("changed_files", []),
        risk_flags=context.get("risk_flags", []),
    )
    risk_level = context.get("risk_level") or review_plan.get("risk_level", "unknown")
    review_mode_reason = context.get("review_mode_reason") or review_plan.get(
        "review_mode_reason", "unknown"
    )
    changed_files = context.get("changed_files", [])
    changed_file_text = ", ".join(f"`{item}`" for item in changed_files) if changed_files else "_none_"

    lines = [
        "# Review Brief",
        "",
        "## Scope",
        f"- Base: `{context.get('base', 'unknown')}`",
        f"- Current branch: `{context.get('current_branch', 'unknown')}`",
        f"- Scope mode: `{context.get('scope_mode', 'unknown')}`",
        f"- Changed files: {changed_file_text}",
        "",
        "## Routing",
        f"- Review mode: `{review_plan['mode']}`",
        f"- Risk level: `{risk_level}`",
        f"- Why this mode: {review_mode_reason}",
        f"- Reviewer set: {', '.join(f'`{item}`' for item in review_plan['reviewers'])}",
    ]

    if review_plan["follow_up"]:
        lines.append(
            f"- Follow-up: {', '.join(f'`{item}`' for item in review_plan['follow_up'])}"
        )

    lines.extend(
        [
            "",
            "## Risk Flags",
        ]
    )

    risk_flags = context.get("risk_flags", [])
    if risk_flags:
        lines.extend(f"- `{flag}`" for flag in risk_flags)
    else:
        lines.append("- _none detected_")

    lines.extend(
        [
            "",
            "## Suggested References",
        ]
    )
    for ref_name in context.get("suggested_references", []):
        lines.append(f"- `{ref_name}`")

    lines.extend(
        [
            "",
            "## Project Memory",
        ]
    )
    project_memory = context.get("project_memory", {})
    if project_memory and project_memory.get("present"):
        summary = project_memory.get("summary", {})
        todo_summary = project_memory.get("todo_summary", {})
        lines.append(f"- Memory root: `{project_memory.get('memory_root', '.codex-memory')}`")
        if summary.get("objective"):
            lines.append(f"- Objective: {'; '.join(summary['objective'])}")
        if summary.get("current_phase"):
            lines.append(f"- Current phase: {'; '.join(summary['current_phase'])}")
        if summary.get("current_focus"):
            lines.append(f"- Current focus: {'; '.join(summary['current_focus'])}")
        if todo_summary.get("in_progress"):
            lines.append(f"- TODO in progress: {'; '.join(todo_summary['in_progress'])}")
        relevant_workstreams = project_memory.get("relevant_workstreams", [])
        if relevant_workstreams:
            lines.append("- Relevant workstreams:")
            for workstream in relevant_workstreams:
                lines.append(
                    f"  - `{workstream['slug']}` ({workstream['path']})"
                )
                if workstream.get("objective"):
                    lines.append(
                        f"    objective: {'; '.join(workstream['objective'])}"
                    )
                if workstream.get("current_state"):
                    lines.append(
                        f"    state: {'; '.join(workstream['current_state'])}"
                    )
        else:
            lines.append("- Relevant workstreams: _none matched current change_")
    else:
        lines.append("- Project memory not present.")

    lines.extend(
        [
            "",
            "## Changed Line Ranges",
        ]
    )
    changed_ranges = context.get("changed_line_ranges", {})
    if changed_ranges:
        for file_name, bucket in changed_ranges.items():
            lines.append(f"- `{file_name}`")
            added = bucket.get("added", [])
            deleted = bucket.get("deleted", [])
            if added:
                lines.append(
                    f"  added: {', '.join(f'{item['start']}-{item['end']}' for item in added)}"
                )
            if deleted:
                lines.append(
                    f"  deleted: {', '.join(f'{item['start']}-{item['end']}' for item in deleted)}"
                )
    else:
        lines.append("- _no changed line ranges_")

    lines.extend(
        [
            "",
            "## Verification Commands",
        ]
    )
    commands = context.get("safe_check_commands", [])
    if commands:
        for item in commands:
            lines.append(f"- `{item['command']}`: {item['reason']}")
    else:
        lines.append("- _no stack-specific checks suggested_")

    return "\n".join(lines) + "\n"


def build_review_brief_compact(context: Dict[str, object]) -> str:
    plan = context.get("review_plan") or select_review_mode(
        changed_files=context.get("changed_files", []),
        risk_flags=context.get("risk_flags", []),
    )
    risk_level = context.get("risk_level") or plan.get("risk_level", "unknown")
    changed_files = ",".join(context["changed_files"])
    refs = ",".join(context["suggested_references"])
    risks = ",".join(context["risk_flags"]) if context["risk_flags"] else "none"
    project_memory = context.get("project_memory", {})
    memory_state = "present" if project_memory and project_memory.get("present") else "absent"
    workstreams = ",".join(
        item["slug"] for item in project_memory.get("relevant_workstreams", [])
    ) or "none"
    return (
        f"review-mode={plan['mode']} "
        f"risk-level={risk_level} "
        f"changed-files={changed_files or 'none'} "
        f"risk-flags={risks} "
        f"refs={refs or 'none'} "
        f"memory={memory_state} "
        f"workstreams={workstreams}\n"
    )


def expand_repo_paths(repo: pathlib.Path, paths: Iterable[str]) -> List[str]:
    expanded: List[str] = []

    for path in paths:
        if not path:
            continue

        repo_path = repo / path
        if repo_path.is_symlink():
            expanded.append(normalize_repo_path(path))
            continue
        submodule_root = find_git_submodule_root(repo, repo_path)
        if submodule_root is not None:
            expanded.append(repo_relative_path(repo, submodule_root))
            continue
        if repo_path.is_dir():
            expanded.extend(walk_repo_dir(repo, repo_path))
            continue

        expanded.append(normalize_repo_path(path))

    return dedupe_keep_order(expanded)


def is_git_submodule_path(path: pathlib.Path) -> bool:
    return path.is_dir() and (path / ".git").exists()


def find_git_submodule_root(repo: pathlib.Path, path: pathlib.Path) -> pathlib.Path | None:
    for candidate in [path] + list(path.parents):
        if candidate == repo:
            break
        if candidate.is_dir() and (candidate / ".git").exists():
            return candidate
    return None


def walk_repo_dir(repo: pathlib.Path, directory: pathlib.Path) -> List[str]:
    expanded: List[str] = []

    for child in sorted(directory.iterdir()):
        if child.is_symlink():
            expanded.append(repo_relative_path(repo, child))
            continue

        submodule_root = find_git_submodule_root(repo, child)
        if submodule_root is not None and submodule_root != directory:
            expanded.append(repo_relative_path(repo, submodule_root))
            continue

        if child.is_dir():
            expanded.extend(walk_repo_dir(repo, child))
            continue

        if child.is_file():
            expanded.append(repo_relative_path(repo, child))

    return expanded


def normalize_repo_path(path: str) -> str:
    return path.replace("\\", "/")


def repo_relative_path(repo: pathlib.Path, path: pathlib.Path) -> str:
    return path.relative_to(repo).as_posix()


def dedupe_keep_order(items: Iterable[str]) -> List[str]:
    result: List[str] = []
    for item in items:
        if item not in result:
            result.append(item)
    return result


def read_markdown_sections(path: pathlib.Path) -> Dict[str, List[str]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (FileNotFoundError, UnicodeDecodeError):
        return {}

    sections: Dict[str, List[str]] = {}
    current_section: str | None = None
    for line in lines:
        match = SECTION_RE.match(line)
        if match:
            current_section = match.group("title").strip()
            sections.setdefault(current_section, [])
            continue
        if current_section is not None:
            sections[current_section].append(line)
    return sections


def read_markdown_sections_from_text(text: str) -> Dict[str, List[str]]:
    lines = text.splitlines()
    sections: Dict[str, List[str]] = {}
    current_section: str | None = None
    for line in lines:
        match = SECTION_RE.match(line)
        if match:
            current_section = match.group("title").strip()
            sections.setdefault(current_section, [])
            continue
        if current_section is not None:
            sections[current_section].append(line)
    return sections


def replace_markdown_section(text: str, heading: str, body_lines: List[str]) -> str:
    lines = text.splitlines()
    new_lines: List[str] = []
    i = 0
    replaced = False

    while i < len(lines):
        line = lines[i]
        if line == heading:
            replaced = True
            new_lines.append(line)
            new_lines.extend(body_lines)
            i += 1
            while i < len(lines) and not lines[i].startswith("## "):
                i += 1
            continue
        new_lines.append(line)
        i += 1

    if not replaced:
        if new_lines and new_lines[-1] != "":
            new_lines.append("")
        new_lines.append(heading)
        new_lines.extend(body_lines)

    return "\n".join(new_lines).rstrip() + "\n"


def summarize_markdown_section(sections: Dict[str, List[str]], title: str) -> List[str]:
    raw_lines = sections.get(title, [])
    summary: List[str] = []
    for line in raw_lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped == "-" or stripped == "- [ ]" or stripped == "- [x]":
            continue
        summary.append(LEADING_LIST_MARKER_RE.sub("", stripped).strip())
    return summary


def format_review_status(review_status: str) -> str:
    return {
        "passed": "通过",
        "conditional": "有条件通过",
        "failed": "不通过",
    }.get(review_status, review_status)


def build_review_session_entry(
    context: Dict[str, object],
    *,
    review_status: str,
    review_score: int,
    todo_follow_ups: Iterable[str],
) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    changed_files = context.get("changed_files", [])
    scope_mode = context.get("scope_mode", "unknown")
    base = context.get("base", "unknown")
    changed_summary = ", ".join(changed_files[:6]) if changed_files else "No changed files recorded."
    actions = (
        f"Ran review setup for base `{base}` in `{scope_mode}` scope and generated the review brief."
    )
    results = (
        f"Review status: {format_review_status(review_status)} | 评分: {review_score} | "
        f"Changed files: {changed_summary}"
    )
    next_step = (
        "Review follow-ups: " + "; ".join(todo_follow_ups)
        if list(todo_follow_ups)
        else "No new follow-up items were recorded."
    )
    return (
        f"\n## {timestamp}\n"
        "- Task: Run production-code-quality-review.\n"
        f"- Actions: {actions}\n"
        f"- Results: {results}\n"
        f"- Next: {next_step}\n"
        "- Blockers: None.\n"
    )


def merge_review_follow_ups(todo_text: str, follow_ups: Iterable[str]) -> str:
    normalized_follow_ups = dedupe_keep_order(
        [item.strip() for item in follow_ups if item and item.strip()]
    )
    if not normalized_follow_ups:
        return todo_text

    sections = read_markdown_sections_from_text(todo_text)
    next_items = summarize_markdown_section(sections, "Next")
    for item in normalized_follow_ups:
        if item not in next_items:
            next_items.append(item)

    return replace_markdown_section(
        todo_text,
        "## Next",
        [f"- [ ] {item}" for item in next_items] or ["- [ ] Define the next action."],
    )


def record_review_memory(
    repo: pathlib.Path,
    context: Dict[str, object],
    *,
    review_status: str,
    review_score: int,
    todo_follow_ups: Iterable[str],
    append_session: bool,
) -> None:
    project_memory = context.get("project_memory", {})
    if not project_memory or not project_memory.get("present"):
        return

    memory_dir = repo / ".codex-memory"
    follow_ups = [item for item in todo_follow_ups if item and item.strip()]

    if append_session:
        session_log_path = memory_dir / "session-log.md"
        if session_log_path.exists():
            entry = build_review_session_entry(
                context,
                review_status=review_status,
                review_score=review_score,
                todo_follow_ups=follow_ups,
            )
            with session_log_path.open("a", encoding="utf-8", newline="\n") as handle:
                handle.write(entry)

    if follow_ups:
        todo_path = memory_dir / "todo.md"
        if todo_path.exists():
            original = todo_path.read_text(encoding="utf-8")
            updated = merge_review_follow_ups(original, follow_ups)
            todo_path.write_text(updated, encoding="utf-8")


def normalize_text_for_match(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def tokenize_for_match(value: str) -> set[str]:
    normalized = normalize_text_for_match(value)
    return {
        token
        for token in normalized.split()
        if len(token) >= 3 and token not in WORKSTREAM_MATCH_STOPWORDS
    }


def score_workstream_relevance(
    slug: str,
    summary: Dict[str, object],
    changed_files: Iterable[str],
) -> int:
    score = 0
    slug_tokens = tokenize_for_match(slug.replace("-", " "))
    changed_file_list = list(changed_files)
    file_text = " ".join(changed_file_list)
    changed_tokens = tokenize_for_match(file_text)

    for token in slug_tokens:
        if token in changed_tokens:
            score += 4

    summary_tokens = tokenize_for_match(
        " ".join(
            [
                " ".join(summary.get("objective", [])),
                " ".join(summary.get("current_state", [])),
                " ".join(summary.get("files", [])),
                " ".join(summary.get("next_actions", [])),
            ]
        )
    )
    score += len(summary_tokens.intersection(changed_tokens)) * 2

    listed_files = [item.lstrip("- ").strip("`") for item in summary.get("files", [])]
    for changed_file in changed_file_list:
        changed_path = normalize_text_for_match(changed_file)
        for listed in listed_files:
            listed_path = normalize_text_for_match(listed)
            if listed_path and (listed_path in changed_path or changed_path in listed_path):
                score += 6

    return score


def load_project_memory(repo: pathlib.Path, changed_files: Iterable[str]) -> Dict[str, object]:
    memory_dir = repo / ".codex-memory"
    if not memory_dir.exists():
        return {"present": False}

    project_state_path = memory_dir / "project-state.md"
    todo_path = memory_dir / "todo.md"
    workstreams_dir = memory_dir / "workstreams"

    project_sections = read_markdown_sections(project_state_path)
    summary = {
        "objective": summarize_markdown_section(project_sections, "Objective"),
        "current_phase": summarize_markdown_section(project_sections, "Current Phase"),
        "current_focus": summarize_markdown_section(project_sections, "Current Focus"),
        "next_milestone": summarize_markdown_section(project_sections, "Next Milestone"),
        "active_risks": summarize_markdown_section(project_sections, "Active Risks"),
        "active_blockers": summarize_markdown_section(project_sections, "Active Blockers"),
        "key_artifacts": summarize_markdown_section(project_sections, "Key Artifacts"),
    }

    todo_sections = read_markdown_sections(todo_path)
    todo_summary = {
        "in_progress": summarize_markdown_section(todo_sections, "In Progress"),
        "next": summarize_markdown_section(todo_sections, "Next"),
    }

    relevant_workstreams: List[Dict[str, object]] = []
    if workstreams_dir.exists():
        for path in sorted(workstreams_dir.glob("*.md")):
            sections = read_markdown_sections(path)
            workstream_summary = {
                "slug": path.stem,
                "path": f".codex-memory/workstreams/{path.name}",
                "objective": summarize_markdown_section(sections, "Objective"),
                "current_state": summarize_markdown_section(sections, "Current State"),
                "blockers": summarize_markdown_section(sections, "Blockers"),
                "files": summarize_markdown_section(sections, "Files"),
                "next_actions": summarize_markdown_section(sections, "Next Actions"),
                "validation": summarize_markdown_section(sections, "Validation"),
            }
            score = score_workstream_relevance(path.stem, workstream_summary, changed_files)
            workstream_summary["relevance_score"] = score
            if score > 0:
                relevant_workstreams.append(workstream_summary)

    relevant_workstreams.sort(
        key=lambda item: (-int(item["relevance_score"]), str(item["slug"]))
    )

    return {
        "present": True,
        "memory_root": ".codex-memory",
        "project_state_path": ".codex-memory/project-state.md",
        "todo_path": ".codex-memory/todo.md",
        "summary": summary,
        "todo_summary": todo_summary,
        "relevant_workstreams": relevant_workstreams[:3],
    }


def collect_review_context(
    repo: pathlib.Path,
    *,
    base_ref_override: str | None = None,
    scope_mode_override: str | None = None,
) -> Dict[str, object]:
    base_ref = base_ref_override or infer_base_ref(repo)
    status = get_status_buckets(repo)
    scope_mode = normalize_scope_mode(scope_mode_override)
    if scope_mode is None:
        scope_mode = "working_tree" if any(status.values()) else "branch"
    include_worktree = scope_mode == "working_tree"

    changed_files = get_changed_files(repo, base_ref, include_worktree=include_worktree)
    diff_text = get_scope_diff_text(
        repo,
        base_ref,
        include_worktree=include_worktree,
        status=status,
    )
    repo_files = list_repo_files(repo)
    stack_inputs = dedupe_keep_order(changed_files + select_repo_stack_markers(repo_files))
    stack_info = detect_stack(stack_inputs or repo_files)
    risk_flags = derive_risk_flags(changed_files, diff_text)
    suggested_references = augment_references_for_risks(
        stack_info["suggested_references"], risk_flags
    )

    review_plan = select_review_mode(changed_files, risk_flags)
    project_memory = load_project_memory(repo, changed_files)

    return {
        "schema_version": "review-context/v1",
        "repo": str(repo),
        "base": base_ref,
        "current_branch": get_current_branch(repo),
        "scope_mode": scope_mode,
        "status": status,
        "changed_files": changed_files,
        "changed_line_ranges": parse_unified_zero_diff(diff_text),
        "detected_stack": stack_info["detected_stack"],
        "suggested_references": suggested_references,
        "risk_flags": risk_flags,
        "risk_level": review_plan.get("risk_level", "unknown"),
        "review_mode_reason": review_plan.get("review_mode_reason", "unknown"),
        "safe_check_commands": build_safe_check_commands(
            stack_info["detected_stack"],
            repo=repo,
            repo_files=repo_files,
        ),
        "review_plan": review_plan,
        "project_memory": project_memory,
    }


def list_repo_files(repo: pathlib.Path) -> List[str]:
    tracked = run_git(repo, ["ls-files"], check=False).splitlines()
    return sorted(filter(None, tracked))


def select_repo_stack_markers(files: Iterable[str]) -> List[str]:
    markers: List[str] = []
    marker_names = {
        "package.json",
        "tsconfig.json",
        "go.mod",
        "pyproject.toml",
        "requirements.txt",
        "poetry.lock",
        "dockerfile",
        "compose.yaml",
        "compose.yml",
        "docker-compose.yml",
        "docker-compose.yaml",
        "schema.prisma",
    }

    for path in files:
        lower_path = path.lower()
        if (
            lower_path in marker_names
            or lower_path.startswith(".github/workflows/")
            or "migration" in lower_path
            or lower_path.endswith(".sql")
        ):
            markers.append(path)

    return dedupe_keep_order(markers)


def to_pretty_json(data: Dict[str, object]) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"
