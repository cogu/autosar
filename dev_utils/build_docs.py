#!/usr/bin/env python3
"""Markdown Documentation Generator.

Renders Jinja2 templates in doc/templates to doc/markdown, automatically
embedding source code and captured execution output from usage tests.
"""

import argparse
import os
import subprocess
import sys
import jinja2

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def get_file_content(rel_path: str) -> str:
    """Read file content relative to repo root and return stripped string."""
    abs_path = os.path.join(REPO_ROOT, rel_path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"File not found: {rel_path} ({abs_path})")
    with open(abs_path, 'r', encoding='utf-8') as fh:
        return fh.read().strip()


def include_code(rel_path: str,
                 lang: str = "python",
                 wrap_code: bool = True) -> str:
    """Include file content, optionally wrapped in markdown code fence."""
    content = get_file_content(rel_path)
    if wrap_code:
        return f"```{lang}\n{content}\n```"
    return content


def run_code(rel_path: str,
             lang: str = "text",
             wrap_code: bool = True) -> str:
    """Execute Python file and capture stdout, optionally wrapped in fence."""
    abs_path = os.path.join(REPO_ROOT, rel_path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"File not found: {rel_path}")

    working_dir = os.path.dirname(abs_path)
    env = dict(os.environ)
    env['PYTHONPATH'] = os.path.join(REPO_ROOT, 'src')

    result = subprocess.run(
        [sys.executable, abs_path],
        capture_output=True,
        text=True,
        cwd=working_dir,
        env=env,
        check=False
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Failed running {rel_path}:\n{result.stderr.strip()}")

    output = result.stdout.strip()
    if wrap_code:
        return f"```{lang}\n{output}\n```"
    return output


def create_jinja_env(template_dir: str) -> jinja2.Environment:
    """Create and configure Jinja2 template environment with custom helpers."""
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
        autoescape=False
    )
    env.globals['include_code'] = include_code
    env.globals['run_code'] = run_code
    env.globals['file_content'] = get_file_content
    return env


def build_documentation(template_dir: str,
                        output_dir: str,
                        check_only: bool = False,
                        verbose: bool = False) -> bool:
    """Render all template files in template_dir into output_dir.

    If check_only is True, verifies that rendered output matches existing files.
    """
    if not os.path.isdir(template_dir):
        if verbose:
            print(f"Template directory does not exist: {template_dir}")
        return True

    env = create_jinja_env(template_dir)
    os.makedirs(output_dir, exist_ok=True)

    has_diffs = False

    for root, _, files in os.walk(template_dir):
        for f in sorted(files):
            if not f.endswith(('.j2', '.jinja2', '.template')):
                continue

            rel_tmpl_path = os.path.relpath(os.path.join(root, f), template_dir)
            template = env.get_template(rel_tmpl_path.replace('\\', '/'))
            rendered = template.render()

            # Strip extension (.j2, .jinja2, .template)
            out_filename = f
            for ext in ('.j2', '.jinja2', '.template'):
                if out_filename.endswith(ext):
                    out_filename = out_filename[:-len(ext)]
                    break

            rel_out_dir = os.path.relpath(root, template_dir)
            target_file_dir = os.path.join(output_dir, rel_out_dir)
            os.makedirs(target_file_dir, exist_ok=True)
            out_path = os.path.join(target_file_dir, out_filename)

            if check_only:
                if not os.path.exists(out_path):
                    print(f"Missing documentation file: {out_path}")
                    has_diffs = True
                else:
                    with open(out_path, 'r', encoding='utf-8') as fh:
                        existing = fh.read()
                    if existing != rendered:
                        print(f"Documentation out of sync: {out_path}")
                        has_diffs = True
                    elif verbose:
                        print(f"In sync: {out_path}")
            else:
                with open(out_path, 'w', encoding='utf-8', newline='\n') as fh:
                    fh.write(rendered)
                if verbose:
                    print(f"Rendered: {os.path.relpath(out_path, REPO_ROOT)}")

    return not has_diffs


def main():
    """CLI entry point for doc generation."""
    parser = argparse.ArgumentParser(
        description="Render Jinja2 documentation templates to Markdown."
    )
    parser.add_argument(
        '--template-dir',
        default=os.path.join(REPO_ROOT, 'doc', 'templates'),
        help="Directory containing Jinja2 templates (default: doc/templates)"
    )
    parser.add_argument(
        '--output-dir',
        default=os.path.join(REPO_ROOT, 'doc', 'markdown'),
        help="Target output directory (default: doc/markdown)"
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help="Check if generated docs are in sync without writing"
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help="Verbose output"
    )

    args = parser.parse_args()

    success = build_documentation(
        template_dir=args.template_dir,
        output_dir=args.output_dir,
        check_only=args.check,
        verbose=args.verbose
    )

    if not success:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
