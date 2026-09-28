#!/usr/bin/env python3
# Released under the MIT License. See LICENSE for details.
"""Script to extract chat command metadata from Python source files into JSON and Markdown."""

import ast
import json
import os

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
COMMANDS_DIR = os.path.join(
    REPO_ROOT,
    'dist/ba_root/mods/chathandle/chatcommands/commands'
)
OUTPUT_JSON = os.path.join(REPO_ROOT, 'docs/commands.json')
OUTPUT_MD = os.path.join(REPO_ROOT, 'docs/COMMANDS.md')


def parse_docstring(docstring: str | None, primary_name: str) -> dict[str, str | list[str]]:
    """Parse docstring into description, usage, and examples."""
    if not docstring:
        return {
            'description': 'No description provided.',
            'usage': f'/{primary_name}',
            'examples': []
        }

    lines = docstring.strip().splitlines()
    desc_lines = []
    usage = f'/{primary_name}'
    examples = []
    in_examples = False

    for line in lines:
        raw_strip = line.strip()
        if not raw_strip:
            continue

        if raw_strip.lower().startswith('usage:'):
            usage = raw_strip[6:].strip()
            in_examples = False
        elif raw_strip.lower().startswith('example:') or raw_strip.lower().startswith('examples:'):
            in_examples = True
            ex = raw_strip.split(':', 1)[1].strip()
            if ex:
                examples.append(ex)
        elif in_examples:
            if raw_strip.startswith('/') or raw_strip.startswith('-') or line.startswith(' ') or line.startswith('\t'):
                ex_clean = raw_strip.lstrip('- ').strip()
                if ex_clean:
                    examples.append(ex_clean)
            else:
                in_examples = False
                desc_lines.append(raw_strip)
        else:
            desc_lines.append(raw_strip)

    description = ' '.join(desc_lines) if desc_lines else 'No description provided.'
    return {
        'description': description,
        'usage': usage,
        'examples': examples
    }


def extract_commands() -> list[dict]:
    """Scan all Python command files and extract registry commands."""
    commands = []

    if not os.path.exists(COMMANDS_DIR):
        print(f"Error: Commands directory not found at {COMMANDS_DIR}")
        return commands

    for filename in sorted(os.listdir(COMMANDS_DIR)):
        if filename.endswith('.py') and filename != '__init__.py':
            filepath = os.path.join(COMMANDS_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            try:
                tree = ast.parse(content, filename=filename)
            except SyntaxError as e:
                print(f"Syntax error parsing {filename}: {e}")
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Call) and getattr(decorator.func, 'attr', '') == 'register':
                            names = []
                            category = 'General'
                            shop_cost = 0

                            if decorator.args and isinstance(decorator.args[0], ast.List):
                                names = [
                                    elt.s if hasattr(elt, 's') else getattr(elt, 'value', '')
                                    for elt in decorator.args[0].elts
                                ]

                            for kw in decorator.keywords:
                                if kw.arg == 'category' and isinstance(kw.value, ast.Constant):
                                    category = kw.value.value
                                elif kw.arg == 'shop_cost' and isinstance(kw.value, ast.Constant):
                                    shop_cost = kw.value.value

                            doc = ast.get_docstring(node)
                            primary_name = names[0] if names else node.name
                            aliases = names[1:] if len(names) > 1 else []
                            parsed_doc = parse_docstring(doc, primary_name)

                            commands.append({
                                'name': f"/{primary_name}",
                                'aliases': [f"/{a}" for a in aliases],
                                'category': category,
                                'shopCost': shop_cost,
                                'usage': parsed_doc['usage'],
                                'description': parsed_doc['description'],
                                'examples': parsed_doc['examples'],
                                'file': filename
                            })

    return commands


def write_json(commands: list[dict]) -> None:
    """Save extracted commands to JSON file."""
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(commands, f, indent=2)
    print(f"Generated JSON output at: {OUTPUT_JSON}")


def write_markdown(commands: list[dict]) -> None:
    """Save extracted commands to a formatted Markdown file."""
    categories: dict[str, list[dict]] = {}
    for cmd in commands:
        cat = cmd['category']
        categories.setdefault(cat, []).append(cmd)

    md = [
        "# Server Chat Commands Documentation",
        "",
        "> Auto-generated command list from Python server source code.",
        ""
    ]

    for cat in sorted(categories.keys()):
        md.append(f"## {cat} Commands\n")
        md.append("| Command | Usage | Aliases | Cost | Description |")
        md.append("| --- | --- | --- | --- | --- |")
        for cmd in categories[cat]:
            aliases_str = ", ".join([f"`{a}`" for a in cmd['aliases']]) if cmd['aliases'] else "-"
            cost_str = f"🎟️ {cmd['shopCost']}" if cmd['shopCost'] > 0 else "Free"
            usage_str = f"`{cmd['usage']}`"
            md.append(f"| `{cmd['name']}` | {usage_str} | {aliases_str} | {cost_str} | {cmd['description']} |")
        md.append("\n")

    os.makedirs(os.path.dirname(OUTPUT_MD), exist_ok=True)
    with open(OUTPUT_MD, 'w', encoding='utf-8') as f:
        f.write("\n".join(md))
    print(f"Generated Markdown output at: {OUTPUT_MD}")


if __name__ == '__main__':
    extracted = extract_commands()
    write_json(extracted)
    write_markdown(extracted)
    print(f"Successfully processed {len(extracted)} chat commands.")
