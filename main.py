#!/usr/bin/env python3
import json
import os
import shlex
import subprocess
import threading
import time
from pathlib import Path
from typing import Annotated

import argplusplus as argpp
from argplusplus.parser import _empty
from argplusplus.parser._alises import Alias
from argplusplus.parser.exceptions import InvalidArgument


manager = argpp.manager.CommandManager("orbit", make_executable=True)

# Global options
manager.define_global("config", _type=str, aliases=("c",))
manager.define_global("dry_run", flag=True)
manager.define_global("verbose", flag=True, aliases=("v",))
manager.define_global("quiet", flag=True, aliases=("q",))
manager.define_global("color", _type=str)


def _global_value(name: str, default):
    value = getattr(manager.globals, name, _empty)
    return default if value is _empty else value


def _config_path() -> Path:
    config = _global_value("config", "")
    if config:
        return Path(config)
    return Path.cwd() / ".orbit.json"


def _validate_color():
    color = _global_value("color", "auto")
    if color not in ("auto", "always", "never"):
        raise InvalidArgument("color must be auto, always, or never")
    return color


def _log(msg: str):
    if _global_value("quiet", False):
        return
    if _global_value("verbose", False):
        print(f"[orbit] {msg}")
    else:
        print(msg)


def _load_db(path: Path) -> dict:
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {"tasks": {}, "pipes": {}, "profiles": []}


def _save_db(path: Path, data: dict):
    if _global_value("dry_run", False):
        _log(f"dry-run: would write {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)


def _parse_csv(value: str) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _apply_env(base: dict, env_csv: str) -> dict:
    env = dict(base)
    for pair in _parse_csv(env_csv):
        if "=" not in pair:
            continue
        key, val = pair.split("=", 1)
        env[key] = val
    return env


# Task commands
task = manager.group("task")


@task.register("test")
def test():
    manager.console.pprint('''[$x:][while:[@lt:[@len:[$x]]:[?now:%H]]][$x:[$x]#][/while][$y:[$x]][$test:0][while:[@lt:[@len:[$y]]:25]][$y:[$y]-][/while][$test]''')

@task.register("add", aliases=("a",))
def task_add(
    name: str,
    *,
    cmd: str = "",
    tags: Annotated[str, Alias["t"]] = "",
    timeout: int = 0,
):
    """Add or update a task."""
    _validate_color()
    path = _config_path()
    data = _load_db(path)
    data["tasks"][name] = {
        "cmd": cmd,
        "tags": _parse_csv(tags),
        "timeout": timeout,
    }
    _save_db(path, data)
    _log(f"task '{name}' saved")


@task.register("run", aliases=("r",))
def task_run(
    name: str,
    *extra: str,
    retries: int = 0,
    env: str = "",
    timeout: int = 0,
):
    """Run a task with optional extra args."""
    _validate_color()
    path = _config_path()
    data = _load_db(path)
    task_data = data["tasks"].get(name)
    if not task_data:
        raise InvalidArgument(f"task '{name}' not found")

    cmd = task_data.get("cmd", "")
    base = shlex.split(cmd) if cmd else []
    full_cmd = base + list(extra)
    if not full_cmd:
        raise InvalidArgument("no command to run")

    env_map = _apply_env(os.environ, env)
    attempts = max(1, retries + 1)
    for idx in range(attempts):
        if _global_value("dry_run", False):
            _log(f"dry-run: would run {' '.join(full_cmd)}")
            return
        try:
            _log(f"run attempt {idx + 1}/{attempts}")
            subprocess.run(full_cmd, env=env_map, check=False, timeout=timeout or None)
            return
        except subprocess.TimeoutExpired:
            if idx + 1 >= attempts:
                raise


@task.register("list", aliases=("ls",))
def task_list(tag: str = "", format: str = "table"):
    """List tasks."""
    _validate_color()
    path = _config_path()
    data = _load_db(path)
    tasks = data["tasks"]
    filtered = []
    for name, item in tasks.items():
        tags = item.get("tags", [])
        if tag and tag not in tags:
            continue
        filtered.append((name, item))

    if format == "json":
        print(json.dumps({name: item for name, item in filtered}, indent=2, sort_keys=True))
        return
    if format != "table":
        raise InvalidArgument("format must be table or json")

    print("name\tcmd\ttags\ttimeout")
    for name, item in filtered:
        tags = ",".join(item.get("tags", []))
        print(f"{name}\t{item.get('cmd', '')}\t{tags}\t{item.get('timeout', 0)}")


@task.register("rm", aliases=("del", "remove"))
def task_remove(name: str):
    """Remove a task."""
    _validate_color()
    path = _config_path()
    data = _load_db(path)
    if name in data["tasks"]:
        del data["tasks"][name]
        _save_db(path, data)
        _log(f"task '{name}' removed")
        return
    raise InvalidArgument(f"task '{name}' not found")


# Pipe commands
pipe = manager.group("pipe")


@pipe.register("build")
def pipe_build(name: str, *step: str):
    """Build a pipeline from steps."""
    _validate_color()
    if not step:
        raise InvalidArgument("pipe requires at least one step")
    path = _config_path()
    data = _load_db(path)
    data["pipes"][name] = {"steps": list(step)}
    _save_db(path, data)
    _log(f"pipe '{name}' saved")


@pipe.register("run")
def pipe_run(name: str, *, parallel: bool = False, limit: int = 0):
    """Run pipeline steps."""
    _validate_color()
    path = _config_path()
    data = _load_db(path)
    pipe_data = data["pipes"].get(name)
    if not pipe_data:
        raise InvalidArgument(f"pipe '{name}' not found")
    steps = pipe_data.get("steps", [])
    if not steps:
        raise InvalidArgument("pipe has no steps")

    if not parallel:
        for step in steps:
            _log(f"step: {step}")
        return

    active = []
    limit = limit or len(steps)
    for step in steps:
        while len(active) >= limit:
            active = [t for t in active if t.is_alive()]
            time.sleep(0.01)
        t = threading.Thread(target=_log, args=(f"step: {step}",))
        t.start()
        active.append(t)
    for t in active:
        t.join()


@pipe.register("graph")
def pipe_graph(name: str, format: str = "dot"):
    """Output a graph for a pipeline."""
    _validate_color()
    path = _config_path()
    data = _load_db(path)
    pipe_data = data["pipes"].get(name)
    if not pipe_data:
        raise InvalidArgument(f"pipe '{name}' not found")
    steps = pipe_data.get("steps", [])
    if format == "json":
        print(json.dumps({"name": name, "steps": steps}, indent=2))
        return
    if format != "dot":
        raise InvalidArgument("format must be dot or json")

    print("digraph pipe {")
    for i in range(len(steps) - 1):
        print(f"  \"{steps[i]}\" -> \"{steps[i + 1]}\";")
    if len(steps) == 1:
        print(f"  \"{steps[0]}\";")
    print("}")


# Profile commands
profile = manager.group("profile")


@profile.register("run")
def profile_run(*cmd: str, sample: int = 10, out: str = ""):
    """Run a command and record timing."""
    _validate_color()
    if not cmd:
        raise InvalidArgument("profile run requires a command")

    start = time.perf_counter()
    if not _global_value("dry_run", False):
        subprocess.run(list(cmd), check=False)
    elapsed_ms = (time.perf_counter() - start) * 1000.0

    record = {
        "cmd": list(cmd),
        "elapsed_ms": elapsed_ms,
        "sample_ms": sample,
    }

    if out:
        out_path = Path(out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(record, f, indent=2)
        _log(f"wrote profile to {out_path}")
        return

    path = _config_path()
    data = _load_db(path)
    data["profiles"].append(record)
    _save_db(path, data)
    _log(f"profile saved ({elapsed_ms:.2f} ms)")


@profile.register("diff")
def profile_diff(a: str, b: str, format: str = "table"):
    """Diff two profile outputs."""
    _validate_color()
    def _read_profile(path: str) -> dict:
        with Path(path).open("r", encoding="utf-8") as f:
            return json.load(f)

    left = _read_profile(a)
    right = _read_profile(b)
    delta = right.get("elapsed_ms", 0) - left.get("elapsed_ms", 0)

    if format == "json":
        print(json.dumps({"a": left, "b": right, "delta_ms": delta}, indent=2))
        return
    if format != "table":
        raise InvalidArgument("format must be table or json")

    print("file\telapsed_ms")
    print(f"{a}\t{left.get('elapsed_ms', 0):.2f}")
    print(f"{b}\t{right.get('elapsed_ms', 0):.2f}")
    print(f"delta\t{delta:.2f}")


@manager.register("repl")
def repl():
    """Interactive shell."""
    _validate_color()
    while True:
        try:
            line = input("orbit> ").strip()
        except EOFError:
            print()
            break
        if not line:
            continue
        if line in ("exit", "quit"):
            break
        try:
            parts = shlex.split(line)
            manager.run(*parts)
        except Exception as exc:
            print(f"error: {exc}")


manager.process()
