#!/usr/bin/env python3
"""
Example Scripts Validator

Discovers and executes all example scripts under examples/ to verify
they run successfully without errors or unexpected output.
"""
import argparse
import os
import subprocess
import sys
from typing import List


def discover_example_scripts(examples_dir: str) -> List[str]:
    """
    Discovers all runnable example scripts under examples_dir.
    """
    scripts = []
    for root, dirs, files in os.walk(examples_dir):
        for f in files:
            if f.endswith(".py") and not f.startswith("__"):
                rel_path = os.path.relpath(os.path.join(root, f), examples_dir)
                # Skip package internal helper modules
                if "demo_system" in rel_path:
                    continue
                scripts.append(os.path.join(root, f))
    scripts.sort()
    return scripts


def run_example(script_path: str, repo_root: str, verbose: bool = True) -> bool:
    """
    Runs a single example script and returns True if successful and silent.
    """
    rel_path = os.path.relpath(script_path, repo_root)
    script_dir = os.path.dirname(script_path)
    env = os.environ.copy()
    src_dir = os.path.join(repo_root, "src")
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{src_dir}{os.pathsep}{existing_pythonpath}" if existing_pythonpath else src_dir

    res = subprocess.run([sys.executable, script_path],
                         cwd=script_dir,
                         capture_output=True,
                         text=True,
                         env=env,
                         check=False)

    stdout = res.stdout.strip()
    stderr = res.stderr.strip()

    if res.returncode != 0 or stdout or stderr:
        print(f"FAILED: {rel_path} (exit code {res.returncode})", file=sys.stderr)
        if stdout:
            print("STDOUT:\n" + stdout, file=sys.stderr)
        if stderr:
            print("STDERR:\n" + stderr, file=sys.stderr)
        return False

    if verbose:
        print(f"PASSED: {rel_path}")

    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate all example scripts.")
    parser.add_argument("scripts", nargs="*", help="Optional specific script(s) to validate")
    parser.add_argument("-s", "--silent", action="store_true", help="Run silently (only report failures)")
    args = parser.parse_args()

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    examples_dir = os.path.join(repo_root, "examples")

    if args.scripts:
        target_scripts = [os.path.abspath(s) for s in args.scripts]
    else:
        target_scripts = discover_example_scripts(examples_dir)

    verbose = not args.silent
    failed = 0
    for script in target_scripts:
        if not run_example(script, repo_root, verbose=verbose):
            failed += 1

    if failed > 0:
        if verbose:
            print(f"\n{failed} out of {len(target_scripts)} example(s) failed.", file=sys.stderr)
        sys.exit(1)

    if verbose:
        print(f"\nAll {len(target_scripts)} example(s) passed successfully.")
    sys.exit(0)


if __name__ == "__main__":
    main()
