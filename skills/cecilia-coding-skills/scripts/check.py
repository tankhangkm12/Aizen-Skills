#!/usr/bin/env python3
"""check — run the repository's own quality checks and record what really happened (v21).

    python scripts/check.py --task SHOP-42              # detect, run, write evidence
    python scripts/check.py --task SHOP-42 --plan       # print the commands only
    python scripts/check.py --task SHOP-42 --steps test,secrets --base origin/develop

Steps (each skipped when the repository has nothing for it):
  lint · typecheck · build · test   the repo's own scripts/tools (package.json scripts, ruff/pytest/mypy,
                                    mvn/gradle, go, cargo, dotnet) — nothing is installed;
  secrets   gitleaks on the task's commits + staged + untracked files; without gitleaks a built-in scan of
            the changed files for high-confidence patterns (weaker — reported as such);
  deps      when a dependency manifest changed: the added packages, whether they exist on the registry, their
            age and licence, names one edit away from a popular package (typosquats, invented names), known
            vulnerabilities (osv-scanner / npm audit / pip-audit when available);
  size      size of the build output (dist/, build/, .next/, out/, target/) and the change since this task's
            first run;

Writes tensura/reports/<TASK>/evidence.json (in the Cecilia workspace when there is one) (sha, branch, base, command, exit code, seconds, status, the
failing tail) and prints a summary of at most 15 lines. Reports quote this file instead of re-typing
results; a reviewer can re-run any step. A missing tool is `unverified`, never `pass`.

Exit code: 0 all run steps passed (or were skipped), 1 a step failed, 2 usage error.
Python ≥ 3.9, standard library only. Network is used only to read public registries (deps step).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import hashlib
import re
import shlex
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

VERSION = "21.0.0"
STEPS = ("lint", "typecheck", "build", "test", "secrets", "deps", "size")
MANIFESTS = {"package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lockb", "requirements.txt",
             "requirements-dev.txt", "pyproject.toml", "poetry.lock", "uv.lock", "Pipfile", "Pipfile.lock", "pom.xml",
             "build.gradle", "build.gradle.kts", "go.mod", "go.sum", "Cargo.toml", "Cargo.lock", "Gemfile",
             "Gemfile.lock", "composer.json", "composer.lock"}
BUILD_DIRS = ("dist", "build", ".next", "out", "target", ".output", "storybook-static")
COPYLEFT = re.compile(r"\b(A?GPL|LGPL|SSPL|EUPL|OSL|CC-BY-SA)", re.I)
POPULAR_NPM = """react react-dom next vue nuxt svelte angular express koa fastify nestjs axios lodash underscore moment dayjs
date-fns uuid chalk commander yargs dotenv cors body-parser jsonwebtoken bcrypt bcryptjs mongoose sequelize prisma typeorm
knex pg mysql2 redis ioredis socket.io ws zod yup joi ajv webpack vite rollup esbuild babel typescript eslint prettier jest
vitest mocha chai sinon supertest cypress playwright puppeteer tailwindcss postcss autoprefixer sass styled-components
@emotion/react @mui/material antd bootstrap jquery rxjs redux @reduxjs/toolkit zustand mobx react-router react-router-dom
react-query @tanstack/react-query swr graphql apollo-server @apollo/client node-fetch cross-fetch got superagent formik
react-hook-form classnames clsx framer-motion three d3 chart.js recharts lodash-es ramda immer nanoid bluebird async
debug winston pino morgan helmet multer sharp jimp nodemailer stripe aws-sdk @aws-sdk/client-s3 firebase firebase-admin
@supabase/supabase-js openai langchain cheerio xml2js csv-parse papaparse yaml js-yaml minimist glob rimraf mkdirp
fs-extra concurrently nodemon ts-node tsx husky lint-staged commitlint semver inquirer ora""".split()
POPULAR_PY = """requests numpy pandas django flask fastapi pydantic sqlalchemy alembic celery redis pytest boto3 botocore
urllib3 certifi idna charset-normalizer six python-dateutil pyyaml jinja2 click rich typer httpx aiohttp uvicorn gunicorn
psycopg2 psycopg2-binary pymongo motor scipy scikit-learn matplotlib seaborn tensorflow torch transformers openai
langchain beautifulsoup4 lxml pillow cryptography pyjwt bcrypt passlib marshmallow attrs orjson ujson black ruff mypy
flake8 isort pre-commit tox coverage hypothesis faker tqdm loguru structlog sentry-sdk""".split()
SECRET_RX = [
    ("private key", re.compile(r"-----BEGIN (RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY")),
    ("AWS access key", re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}")),
    ("Slack token", re.compile(r"\bxox[abpr]-[A-Za-z0-9-]{10,}")),
    ("Stripe key", re.compile(r"\b(sk|rk)_live_[A-Za-z0-9]{20,}")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("OpenAI/Anthropic key", re.compile(r"\bsk-(proj-|ant-)?[A-Za-z0-9_-]{32,}")),
    ("JWT", re.compile(r"\beyJ[A-Za-z0-9_-]{15,}\.eyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{10,}")),
    ("URL with password", re.compile(r"\b[a-z][a-z0-9+.-]*://[^\s:/@'\"]+:[^\s@/'\"]{6,}@[^\s'\"]+", re.I)),
    ("assigned secret", re.compile(r"(?i)\b(api[_-]?key|secret|password|passwd|token|client[_-]?secret)\b\s*[:=]\s*['\"][^'\"\s]{12,}['\"]")),
]


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def which(name: str) -> str | None:
    return shutil.which(name)


def sh(cmd: list[str], cwd: Path, timeout: int, env=None) -> tuple[int, str, float]:
    exe = which(cmd[0]) or cmd[0]
    t0 = time.time()
    try:
        r = subprocess.run([exe, *cmd[1:]], cwd=str(cwd), capture_output=True, text=True, timeout=timeout,
                           env=dict(os.environ, CI="1", FORCE_COLOR="0", NO_COLOR="1", **(env or {})),
                           encoding="utf-8", errors="replace")
        return r.returncode, (r.stdout or "") + (r.stderr or ""), time.time() - t0
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or "") if isinstance(e.stdout, str) else ""
        return 124, out + f"\n[timeout after {timeout}s]", time.time() - t0
    except OSError as e:
        return 127, str(e), time.time() - t0


def git(root: Path, *args) -> str:
    code, out, _ = sh(["git", "-C", str(root), "--no-optional-locks", *args], root, 60,
                      env={"GIT_OPTIONAL_LOCKS": "0"})
    return out.strip() if code == 0 else ""


def tail(text: str, n: int = 30) -> str:
    lines = [l for l in text.splitlines() if l.strip()]
    return "\n".join(lines[-n:])


# --------------------------------------------------------------------------- detection

def node_pm(root: Path) -> str:
    if (root / "pnpm-lock.yaml").exists():
        return "pnpm"
    if (root / "yarn.lock").exists():
        return "yarn"
    if (root / "bun.lockb").exists() or (root / "bun.lock").exists():
        return "bun"
    return "npm"


def detect(root: Path) -> dict:
    """{step: [(label, argv)]} for what this repository defines. Nothing is invented."""
    plan: dict = {s: [] for s in ("lint", "typecheck", "build", "test")}
    pj = root / "package.json"
    if pj.is_file():
        try:
            scripts = json.loads(pj.read_text(encoding="utf-8")).get("scripts", {}) or {}
        except ValueError:
            scripts = {}
        pm = node_pm(root)
        run = [pm, "run"] if pm != "yarn" else ["yarn"]
        pick = {"lint": ["lint"], "typecheck": ["typecheck", "type-check", "check-types", "tsc", "types"],
                "build": ["build"], "test": ["test:ci", "test:unit", "test"]}
        for step, names in pick.items():
            for n in names:
                if n in scripts and "watch" not in scripts[n] and not re.search(r"\bdev\b|serve", scripts[n]):
                    plan[step].append((f"{pm} {n}", run + [n]))
                    break
        if not plan["typecheck"] and (root / "tsconfig.json").is_file() and (root / "node_modules/.bin/tsc").exists():
            plan["typecheck"].append(("tsc --noEmit", ["npx", "--no-install", "tsc", "--noEmit"]))
    pyproj = (root / "pyproject.toml").read_text(encoding="utf-8", errors="ignore") if (root / "pyproject.toml").is_file() else ""
    is_py = bool(pyproj) or any((root / f).is_file() for f in ("requirements.txt", "setup.py", "setup.cfg", "Pipfile"))
    if is_py:
        if which("ruff") and ("ruff" in pyproj or (root / "ruff.toml").exists() or (root / ".ruff.toml").exists()):
            plan["lint"].append(("ruff check", ["ruff", "check", "."]))
        elif which("flake8") and ((root / ".flake8").exists() or "flake8" in pyproj):
            plan["lint"].append(("flake8", ["flake8"]))
        if which("mypy") and ("mypy" in pyproj or (root / "mypy.ini").exists()):
            plan["typecheck"].append(("mypy", ["mypy", "."]))
        if any((root / d).is_dir() for d in ("tests", "test")) or "pytest" in pyproj:
            py = which("pytest")
            plan["test"].append(("pytest", ["pytest", "-q"] if py else [sys.executable, "-m", "pytest", "-q"]))
    if (root / "pom.xml").is_file():
        mvn = "./mvnw" if (root / "mvnw").exists() else "mvn"
        plan["build"].append(("mvn verify", [mvn, "-q", "-B", "verify"]))
    elif (root / "build.gradle").is_file() or (root / "build.gradle.kts").is_file():
        gw = "./gradlew" if (root / "gradlew").exists() else "gradle"
        plan["build"].append(("gradle build", [gw, "build", "-q"]))
    if (root / "go.mod").is_file():
        plan["lint"].append(("go vet", ["go", "vet", "./..."]))
        plan["build"].append(("go build", ["go", "build", "./..."]))
        plan["test"].append(("go test", ["go", "test", "./..."]))
    if (root / "Cargo.toml").is_file():
        plan["build"].append(("cargo build", ["cargo", "build", "-q"]))
        plan["test"].append(("cargo test", ["cargo", "test", "-q"]))
    slns = list(root.glob("*.sln"))
    if slns:
        plan["build"].append(("dotnet build", ["dotnet", "build", str(slns[0].name)]))
        plan["test"].append(("dotnet test", ["dotnet", "test", str(slns[0].name)]))
    return plan


def changed_files(root: Path, base: str) -> list[str]:
    files = set()
    if base:
        files.update(git(root, "diff", "--name-only", f"{base}...HEAD").splitlines())
    files.update(git(root, "diff", "--name-only").splitlines())
    files.update(git(root, "diff", "--name-only", "--cached").splitlines())
    files.update(git(root, "ls-files", "--others", "--exclude-standard").splitlines())
    return sorted(f for f in files if f)


def default_base(root: Path) -> str:
    for cand in ("origin/develop", "develop", "origin/main", "main", "origin/master", "master"):
        if git(root, "rev-parse", "--verify", "--quiet", cand):
            mb = git(root, "merge-base", "HEAD", cand)
            if mb:
                return mb
    return ""


# --------------------------------------------------------------------------- secrets

def secrets_step(root: Path, base: str, files: list[str], timeout: int) -> dict:
    if which("gitleaks"):
        out_all, findings, cmds = "", 0, []
        code_help, help_out, _ = sh(["gitleaks", "--help"], root, 30)
        modern = " git " in help_out or "\n  git" in help_out
        runs = []
        if modern:
            if base:
                runs.append(["gitleaks", "git", "--redact", "--no-banner", "--exit-code", "1", "--log-opts", f"{base}..HEAD", "."])
            runs.append(["gitleaks", "git", "--staged", "--redact", "--no-banner", "--exit-code", "1", "."])
        else:
            if base:
                runs.append(["gitleaks", "detect", "--redact", "--no-banner", "--log-opts", f"{base}..HEAD"])
            runs.append(["gitleaks", "protect", "--staged", "--redact", "--no-banner"])
        for argv in runs:
            code, out, _ = sh(argv, root, timeout)
            cmds.append(" ".join(argv))
            out_all += out
            if code == 1:
                findings += max(1, len(re.findall(r"(?im)^\s*(Finding|RuleID):", out)) // 1)
            elif code not in (0, 1):
                return {"status": "unverified", "tool": "gitleaks", "cmd": cmds, "detail": tail(out, 10)}
        untracked = [f for f in git(root, "ls-files", "--others", "--exclude-standard").splitlines() if f]
        extra = builtin_scan(root, untracked)
        n = findings + len(extra)
        return {"status": "fail" if n else "pass", "tool": "gitleaks" + (" + builtin(untracked)" if untracked else ""),
                "cmd": cmds, "findings": n, "files": sorted({f["file"] for f in extra}), "detail": tail(out_all, 15)}
    found = builtin_scan(root, files)
    return {"status": "fail" if found else "unverified", "tool": "builtin (weaker than gitleaks)",
            "findings": len(found), "files": sorted({f["file"] for f in found}),
            "detail": "; ".join(f"{f['file']}:{f['line']} {f['kind']}" for f in found[:10]),
            "note": "gitleaks not installed — the built-in scan covers high-confidence patterns in changed files only. "
                    "Installing gitleaks is A3: quote the install command for Cecilia."}


def builtin_scan(root: Path, files: list[str]) -> list[dict]:
    hits = []
    for rel in files:
        p = root / rel
        if not p.is_file() or p.stat().st_size > 1_000_000 or any(part in {"node_modules", ".git"} for part in p.parts):
            continue
        if re.search(r"\.(png|jpe?g|gif|webp|ico|pdf|zip|gz|woff2?|ttf|lock|min\.js)$", rel, re.I):
            continue
        if re.search(r"(^|/)\.env\.(example|sample|template)$", rel):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            for kind, rx in SECRET_RX:
                if rx.search(line) and "example" not in line.lower() and "placeholder" not in line.lower():
                    hits.append({"file": rel, "line": i, "kind": kind})
                    break
    return hits


# --------------------------------------------------------------------------- dependencies

def lev1(a: str, b: str) -> bool:
    """Edit distance exactly 1 (or a swapped pair)."""
    if a == b or abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        diff = [i for i in range(len(a)) if a[i] != b[i]]
        return len(diff) == 1 or (len(diff) == 2 and a[diff[0]] == b[diff[1]] and a[diff[1]] == b[diff[0]])
    s, t = (a, b) if len(a) < len(b) else (b, a)
    for i in range(len(t)):
        if t[:i] + t[i + 1:] == s:
            return True
    return False


def fetch_json(url: str, timeout: int = 10):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "cecilia-check"}), timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception:
        return None


def npm_added(root: Path, base: str) -> dict:
    now_pkg = json.loads((root / "package.json").read_text(encoding="utf-8")) if (root / "package.json").is_file() else {}
    old_text = git(root, "show", f"{base}:package.json") if base else ""
    try:
        old_pkg = json.loads(old_text) if old_text else {}
    except ValueError:
        old_pkg = {}
    added = {}
    for sec in ("dependencies", "devDependencies", "optionalDependencies", "peerDependencies"):
        for name, ver in (now_pkg.get(sec) or {}).items():
            if name not in (old_pkg.get(sec) or {}) and not any(name in (old_pkg.get(s) or {}) for s in
                                                                  ("dependencies", "devDependencies")):
                added[name] = ver
    return added


def py_added(root: Path, base: str) -> dict:
    added = {}
    for f in ("requirements.txt", "requirements-dev.txt"):
        cur = (root / f).read_text(encoding="utf-8", errors="ignore") if (root / f).is_file() else ""
        old = git(root, "show", f"{base}:{f}") if base else ""
        names = lambda t: {re.split(r"[<>=!~\[; ]", l.strip())[0].lower(): l.strip() for l in t.splitlines()  # noqa: E731
                           if l.strip() and not l.strip().startswith(("#", "-"))}
        for n, spec in names(cur).items():
            if n and n not in names(old):
                added[n] = spec
    return added


def deps_step(root: Path, base: str, files: list[str], offline: bool, timeout: int) -> dict:
    touched = [f for f in files if Path(f).name in MANIFESTS]
    if not touched:
        return {"status": "skip", "detail": "no dependency manifest changed"}
    report = {"status": "pass", "manifests": touched, "added": [], "flags": [], "audit": None}
    npm_new = npm_added(root, base) if (root / "package.json").is_file() else {}
    py_new = py_added(root, base)
    for name, spec in npm_new.items():
        item = {"eco": "npm", "name": name, "spec": spec}
        close = [p for p in POPULAR_NPM if lev1(name.lower(), p)]
        if close:
            item["typosquat_of"] = close
            report["flags"].append(f"{name}: one edit away from popular '{close[0]}' — typo or typosquat?")
        if not offline:
            meta = fetch_json(f"https://registry.npmjs.org/{name.replace('/', '%2F')}")
            if meta is None:
                item["registry"] = "unverified"
            elif "error" in meta or "name" not in meta:
                item["registry"] = "NOT FOUND"
                report["flags"].append(f"{name}: not on the npm registry — invented name?")
            else:
                created = (meta.get("time") or {}).get("created", "")
                item["created"] = created[:10]
                item["license"] = (meta.get("license") if isinstance(meta.get("license"), str) else
                                   (meta.get("license") or {}).get("type", "")) or ""
                if created and (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(
                        created.replace("Z", "+00:00"))).days < 90:
                    report["flags"].append(f"{name}: first published {created[:10]} (< 90 days)")
                if COPYLEFT.search(item["license"] or ""):
                    report["flags"].append(f"{name}: licence {item['license']} (copyleft) — Cecilia decides")
                dl = fetch_json(f"https://api.npmjs.org/downloads/point/last-week/{name}")
                if dl and isinstance(dl.get("downloads"), int):
                    item["weekly_downloads"] = dl["downloads"]
                    if dl["downloads"] < 500:
                        report["flags"].append(f"{name}: {dl['downloads']} downloads last week")
        size_dir = root / "node_modules" / name
        if size_dir.is_dir():
            item["installed_kb"] = round(dir_size(size_dir) / 1024)
        report["added"].append(item)
    for name, spec in py_new.items():
        item = {"eco": "pypi", "name": name, "spec": spec}
        close = [p for p in POPULAR_PY if lev1(name, p)]
        if close:
            item["typosquat_of"] = close
            report["flags"].append(f"{name}: one edit away from popular '{close[0]}' — typo or typosquat?")
        if not offline:
            meta = fetch_json(f"https://pypi.org/pypi/{name}/json")
            if meta is None:
                item["registry"] = "NOT FOUND or offline"
                report["flags"].append(f"{name}: not found on PyPI (or offline) — invented name?")
            else:
                info = meta.get("info") or {}
                item["license"] = info.get("license") or ""
                if COPYLEFT.search(item["license"] or ""):
                    report["flags"].append(f"{name}: licence {item['license']} (copyleft) — Cecilia decides")
        report["added"].append(item)
    if which("osv-scanner"):
        code, out, _ = sh(["osv-scanner", "--recursive", "--format", "json", "."], root, timeout)
        vulns = len(re.findall(r'"id":\s*"(GHSA|CVE|PYSEC|OSV)-', out))
        report["audit"] = {"tool": "osv-scanner", "vulnerabilities": vulns, "exit": code}
    elif (root / "package-lock.json").is_file() and which("npm") and not offline:
        code, out, _ = sh(["npm", "audit", "--json", "--omit=dev"], root, timeout)
        try:
            meta = json.loads(out[out.index("{"):]).get("metadata", {}).get("vulnerabilities", {})
        except (ValueError, AttributeError):
            meta = {}
        report["audit"] = {"tool": "npm audit", "high": meta.get("high", 0), "critical": meta.get("critical", 0)}
    elif py_new and which("pip-audit") and not offline:
        code, out, _ = sh(["pip-audit", "-r", "requirements.txt", "-f", "json"], root, timeout)
        report["audit"] = {"tool": "pip-audit", "vulnerabilities": len(re.findall(r'"id":', out)), "exit": code}
    else:
        report["audit"] = {"tool": None, "status": "unverified — no osv-scanner / npm audit / pip-audit available"}
    audit = report["audit"] or {}
    if audit.get("critical") or audit.get("high") or audit.get("vulnerabilities"):
        report["flags"].append(f"known vulnerabilities: {json.dumps({k: v for k, v in audit.items() if k != 'tool'})}")
    if any("NOT FOUND" in f or "typosquat" in f for f in report["flags"]):
        report["status"] = "fail"
    elif report["flags"]:
        report["status"] = "review"
    return report


# --------------------------------------------------------------------------- size

def dir_size(p: Path) -> int:
    total = 0
    for f in p.rglob("*"):
        try:
            if f.is_file():
                total += f.stat().st_size
        except OSError:
            continue
    return total


def size_step(root: Path, previous: dict | None) -> dict:
    sizes = {d: dir_size(root / d) for d in BUILD_DIRS if (root / d).is_dir()}
    if not sizes:
        return {"status": "skip", "detail": "no build output directory"}
    out = {"status": "pass", "bytes": sizes}
    prev = ((previous or {}).get("size") or {}).get("first_bytes") or ((previous or {}).get("size") or {}).get("bytes")
    out["first_bytes"] = prev or sizes
    if prev:
        out["delta_bytes"] = {d: sizes.get(d, 0) - prev.get(d, 0) for d in sizes}
    return out


# --------------------------------------------------------------------------- main

def locate(project_arg: str) -> tuple[Path, Path]:
    """(code root, docs home): both the repository given by --project, else the current directory."""
    code = Path(project_arg or ".").resolve()
    return code, code


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--task", required=True, help="task id; evidence goes to tensura/reports/<TASK>/evidence.json")
    ap.add_argument("--project", default="", help="repository root (default: the current directory)")
    ap.add_argument("--steps", default=",".join(STEPS), help="comma list of " + ", ".join(STEPS))
    ap.add_argument("--base", default="", help="base ref for 'what changed' (default: merge-base with develop/main)")
    ap.add_argument("--plan", action="store_true", help="print the detected commands; run nothing")
    ap.add_argument("--offline", action="store_true", help="deps step: no registry look-ups")
    ap.add_argument("--timeout", type=int, default=900, help="seconds per command (default 900)")
    ap.add_argument("--out", default="", help="evidence path (default tensura/reports/<TASK>/evidence.json)")
    a = ap.parse_args()
    root, home = locate(a.project)
    steps = [s.strip() for s in a.steps.split(",") if s.strip()]
    bad = [s for s in steps if s not in STEPS]
    if bad or not re.match(r"^[A-Za-z0-9._-]+$", a.task):
        print(f"usage error: unknown steps {bad}" if bad else "usage error: --task must be an id like SHOP-42")
        return 2
    plan = detect(root)
    if a.plan:
        for s in steps:
            if s in plan:
                print(f"{s:9} " + (" | ".join(label + ": " + " ".join(cmd) for label, cmd in plan[s]) or "(nothing defined)"))
            else:
                print(f"{s:9} (built-in step)")
        return 0
    out_file = Path(a.out) if a.out else home / "tensura" / "reports" / a.task / "evidence.json"
    previous = None
    if out_file.is_file():
        try:
            previous = json.loads(out_file.read_text(encoding="utf-8"))
        except ValueError:
            previous = None
    base = a.base or default_base(root)
    files = changed_files(root, base)
    ev = {"tool": "check", "version": VERSION, "task": a.task, "started": now(), "project": str(root),
          "sha": git(root, "rev-parse", "HEAD"), "branch": git(root, "rev-parse", "--abbrev-ref", "HEAD"),
          "base": base, "dirty": bool(git(root, "status", "--porcelain")), "changed_files": len(files), "steps": []}
    failed = False
    for s in steps:
        if s in plan:
            if not plan[s]:
                ev["steps"].append({"step": s, "status": "skip", "detail": "nothing defined in this repository"})
                continue
            for label, cmd in plan[s]:
                if not which(cmd[0]) and not cmd[0].startswith("./") and cmd[0] != sys.executable:
                    ev["steps"].append({"step": s, "label": label, "cmd": " ".join(cmd), "status": "unverified",
                                        "detail": f"{cmd[0]} not installed"})
                    continue
                code, out, secs = sh(cmd, root, a.timeout)
                rec = {"step": s, "label": label, "cmd": " ".join(cmd), "exit": code, "seconds": round(secs, 1),
                       "status": "pass" if code == 0 else "fail"}
                if code != 0:
                    rec["tail"] = tail(out)
                    failed = True
                counts = list(dict.fromkeys(f"{n} {w}" for n, w in re.findall(r"(\d+)\s+(passed|failed|skipped|tests?)\b", out)))
                if counts:
                    rec["counts"] = " ".join(counts[-4:])
                ev["steps"].append(rec)
        elif s == "secrets":
            r = secrets_step(root, base, files, a.timeout)
            ev["steps"].append({"step": "secrets", **r})
            failed |= r["status"] == "fail"
        elif s == "deps":
            r = deps_step(root, base, files, a.offline, a.timeout)
            ev["steps"].append({"step": "deps", **r})
            failed |= r["status"] == "fail"
        elif s == "size":
            r = size_step(root, previous)
            ev["size"] = r
            ev["steps"].append({"step": "size", "status": r["status"],
                                "detail": ", ".join(f"{k} {v // 1024} KB" for k, v in (r.get("bytes") or {}).items())
                                + ("" if "delta_bytes" not in r else " · Δ " + ", ".join(
                                    f"{k} {v // 1024:+} KB" for k, v in r["delta_bytes"].items()))})
    ev["finished"] = now()
    ev["result"] = "fail" if failed else "pass"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(ev, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [f"check {a.task} @ {ev['sha'][:10] or '?'} ({ev['branch'] or '?'}) → {ev['result'].upper()}"]
    for st in ev["steps"][:12]:
        extra = st.get("counts") or st.get("detail") or ""
        if st["step"] == "deps" and st.get("flags"):
            extra = "; ".join(st["flags"][:2])
        lines.append(f"  {st['step']:9} {st['status']:10} {st.get('cmd', st.get('tool', ''))[:50]}  {str(extra)[:70]}")
    lines.append(f"  evidence: {out_file}")
    print("\n".join(lines[:15]))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
