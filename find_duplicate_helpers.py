from pathlib import Path
import re
from collections import defaultdict

TARGET_FILE = Path("web/app.py")

# These are the helper names that commonly got duplicated in your app file.
PRIORITY_NAMES = {
    "safe_list",
    "safe_dict",
    "safe_run",
    "_safe_int",
    "_norm_text",
    "_norm_upper",
    "_top_count_item",
    "is_logged_in",
    "is_master",
    "current_tier_title",
    "current_tier_lower",
    "get_current_tier_for_routes",
    "can_access_all_symbols",
    "get_theme",
    "get_unread_notifications",
    "get_current_user",
    "current_user_context",
    "template_context",
    "inject_global_context",
    "get_symbol_detail",
}

def find_function_defs(lines):
    pattern = re.compile(r"^def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")
    found = defaultdict(list)

    for idx, line in enumerate(lines, start=1):
        match = pattern.match(line)
        if match:
            name = match.group(1)
            found[name].append(idx)

    return found

def extract_block(lines, start_line):
    start_idx = start_line - 1
    header = lines[start_idx]
    base_indent = len(header) - len(header.lstrip())

    block = [header]
    i = start_idx + 1

    while i < len(lines):
        line = lines[i]

        if line.strip() == "":
            block.append(line)
            i += 1
            continue

        indent = len(line) - len(line.lstrip())

        # Stop when we hit another top-level def, class, or decorator.
        if indent == 0 and (
            line.startswith("def ")
            or line.startswith("class ")
            or line.startswith("@")
        ):
            break

        block.append(line)
        i += 1

    return "".join(block).rstrip()

def main():
    if not TARGET_FILE.exists():
        print(f"File not found: {TARGET_FILE}")
        return

    lines = TARGET_FILE.read_text(encoding="utf-8").splitlines(keepends=True)
    defs = find_function_defs(lines)

    duplicates = {name: locs for name, locs in defs.items() if len(locs) > 1}

    report_lines = []
    report_lines.append(f"Duplicate function report for {TARGET_FILE}\n")
    report_lines.append("=" * 72 + "\n")

    if not duplicates:
        msg = "No duplicate function names found.\n"
        print(msg)
        report_lines.append(msg)
        Path("duplicate_helper_report.txt").write_text("".join(report_lines), encoding="utf-8")
        return

    print("\nDUPLICATE FUNCTION NAMES FOUND\n")
    report_lines.append("Duplicate function names found:\n\n")

    for name in sorted(duplicates.keys(), key=lambda x: (x not in PRIORITY_NAMES, x)):
        locs = duplicates[name]
        priority_flag = "  <-- PRIORITY CHECK" if name in PRIORITY_NAMES else ""
        line = f"{name}: lines {locs}{priority_flag}"
        print(line)
        report_lines.append(line + "\n")

    report_lines.append("\n" + "=" * 72 + "\n")
    report_lines.append("FULL DUPLICATE BLOCKS\n\n")

    print("\n" + "=" * 72)
    print("FULL DUPLICATE BLOCKS")
    print("=" * 72)

    for name in sorted(duplicates.keys(), key=lambda x: (x not in PRIORITY_NAMES, x)):
        locs = duplicates[name]
        for n, line_no in enumerate(locs, start=1):
            header = f"\n--- {name} occurrence {n}/{len(locs)} at line {line_no} ---\n"
            print(header)
            report_lines.append(header)
            block = extract_block(lines, line_no)
            print(block)
            print()
            report_lines.append(block + "\n\n")

    out_path = Path("duplicate_helper_report.txt")
    out_path.write_text("".join(report_lines), encoding="utf-8")
    print(f"\nSaved report to: {out_path}")

if __name__ == "__main__":
    main()
