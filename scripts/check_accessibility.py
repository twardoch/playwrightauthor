#!/usr/bin/env python3
# this_file: scripts/check_accessibility.py
"""
Documentation Accessibility Checker for PlaywrightAuthor

Analyzes markdown documentation for accessibility issues including:
- Heading structure and hierarchy
- Image alt text quality
- Link text accessibility
- Table structure and headers
- Language clarity and readability
- Document structure and navigation

Designed for CI/CD integration with detailed reporting and remediation guidance.
"""

import argparse
import json
import re
import sys
import time
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class AccessibilityIssue:
    """Represents a single accessibility issue found in documentation."""

    file_path: str
    line_number: int
    issue_type: str
    severity: str  # 'error', 'warning', 'info'
    description: str
    recommendation: str
    element_content: str | None = None
    wcag_guideline: str | None = None


@dataclass
class AccessibilitySummary:
    """Summary of accessibility check results."""

    total_files: int
    total_issues: int
    errors: int
    warnings: int
    info: int
    issues_by_type: dict[str, int]
    issues_by_file: dict[str, int]
    all_issues: list[AccessibilityIssue]


class DocumentationAccessibilityChecker:
    """Comprehensive accessibility checker for markdown documentation."""

    def __init__(self, docs_root: Path):
        self.docs_root = Path(docs_root).resolve()
        self.issues: list[AccessibilityIssue] = []

        # Problematic link text patterns
        self.bad_link_text_patterns = {
            r"^click\s+here$": "Use descriptive text that explains the destination",
            r"^here$": "Use descriptive text that explains the destination",
            r"^read\s+more$": 'Use specific text like "Read more about X"',
            r"^more$": 'Use specific text like "Learn more about X"',
            r"^link$": "Use descriptive text that explains the destination",
            r"^this$": 'Use descriptive text that explains what "this" refers to',
            r"^download$": "Specify what is being downloaded",
            r"^continue$": "Specify what the user is continuing to",
            r"^next$": "Specify what comes next",
            r"^back$": "Specify where the user is going back to",
        }

        # Heading level pattern
        self.heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

        # Link patterns
        self.markdown_link_pattern = re.compile(r"\[([^\]]+)\]\([^)]+\)")
        self.image_pattern = re.compile(r"!\[([^\]]*)\]\([^)]+\)")

        # Table patterns
        self.table_row_pattern = re.compile(r"^\|(.+)\|$", re.MULTILINE)

        # List patterns
        self.list_item_pattern = re.compile(r"^[\s]*[-*+]\s+", re.MULTILINE)
        self.ordered_list_pattern = re.compile(r"^[\s]*\d+\.\s+", re.MULTILINE)

    def find_markdown_files(self) -> list[Path]:
        """Find all markdown files in the documentation directory."""
        md_files = []
        for pattern in ["*.md", "*.markdown"]:
            md_files.extend(self.docs_root.rglob(pattern))
        return sorted(md_files)

    def add_issue(
        self,
        file_path: Path,
        line_number: int,
        issue_type: str,
        severity: str,
        description: str,
        recommendation: str,
        element_content: str | None = None,
        wcag_guideline: str | None = None,
    ):
        """Add an accessibility issue to the results."""
        issue = AccessibilityIssue(
            file_path=str(file_path.relative_to(self.docs_root)),
            line_number=line_number,
            issue_type=issue_type,
            severity=severity,
            description=description,
            recommendation=recommendation,
            element_content=element_content,
            wcag_guideline=wcag_guideline,
        )
        self.issues.append(issue)

    def check_heading_structure(self, file_path: Path, content: str):
        """Check heading hierarchy and structure."""
        lines = content.split("\n")
        headings = []

        for line_num, line in enumerate(lines, 1):
            heading_match = re.match(r"^(#{1,6})\s+(.+)$", line.strip())
            if heading_match:
                level = len(heading_match.group(1))
                text = heading_match.group(2).strip()
                headings.append((line_num, level, text))

        if not headings:
            self.add_issue(
                file_path,
                1,
                "heading_structure",
                "warning",
                "Document has no headings",
                "Add headings to create a clear document structure",
                wcag_guideline="WCAG 2.1 SC 2.4.6 (Headings and Labels)",
            )
            return

        # Check if first heading is H1
        if headings[0][1] != 1:
            self.add_issue(
                file_path,
                headings[0][0],
                "heading_structure",
                "error",
                f"First heading is H{headings[0][1]}, should be H1",
                "Start documents with an H1 heading",
                element_content=headings[0][2],
                wcag_guideline="WCAG 2.1 SC 1.3.1 (Info and Relationships)",
            )

        # Check heading hierarchy
        for i in range(1, len(headings)):
            prev_level = headings[i - 1][1]
            curr_level = headings[i][1]

            if curr_level > prev_level + 1:
                self.add_issue(
                    file_path,
                    headings[i][0],
                    "heading_structure",
                    "error",
                    f"Heading level jumps from H{prev_level} to H{curr_level}",
                    f"Use H{prev_level + 1} instead, or restructure content",
                    element_content=headings[i][2],
                    wcag_guideline="WCAG 2.1 SC 1.3.1 (Info and Relationships)",
                )

        # Check for duplicate headings at the same level
        heading_texts = defaultdict(list)
        for line_num, level, text in headings:
            heading_texts[(level, text.lower())].append((line_num, text))

        for (level, text), occurrences in heading_texts.items():
            if len(occurrences) > 1:
                for line_num, original_text in occurrences[1:]:
                    self.add_issue(
                        file_path,
                        line_num,
                        "heading_structure",
                        "warning",
                        f"Duplicate H{level} heading: '{original_text}'",
                        "Use unique headings or add distinguishing context",
                        element_content=original_text,
                        wcag_guideline="WCAG 2.1 SC 2.4.6 (Headings and Labels)",
                    )

    def check_image_alt_text(self, file_path: Path, content: str):
        """Check image alt text quality."""
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            for match in self.image_pattern.finditer(line):
                alt_text = match.group(1).strip()
                image_syntax = match.group(0)

                if not alt_text:
                    self.add_issue(
                        file_path,
                        line_num,
                        "image_alt_text",
                        "error",
                        "Image has no alt text",
                        "Add descriptive alt text that explains the image content",
                        element_content=image_syntax,
                        wcag_guideline="WCAG 2.1 SC 1.1.1 (Non-text Content)",
                    )
                elif len(alt_text) < 3:
                    self.add_issue(
                        file_path,
                        line_num,
                        "image_alt_text",
                        "warning",
                        f"Image alt text is too short: '{alt_text}'",
                        "Provide more descriptive alt text that explains the image content",
                        element_content=image_syntax,
                        wcag_guideline="WCAG 2.1 SC 1.1.1 (Non-text Content)",
                    )
                elif alt_text.lower() in [
                    "image",
                    "picture",
                    "photo",
                    "screenshot",
                    "graphic",
                ]:
                    self.add_issue(
                        file_path,
                        line_num,
                        "image_alt_text",
                        "warning",
                        f"Generic alt text: '{alt_text}'",
                        "Use specific, descriptive alt text that explains what the image shows",
                        element_content=image_syntax,
                        wcag_guideline="WCAG 2.1 SC 1.1.1 (Non-text Content)",
                    )

    def check_link_text_quality(self, file_path: Path, content: str):
        """Check link text for accessibility issues."""
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            for match in self.markdown_link_pattern.finditer(line):
                link_text = match.group(1).strip().lower()
                link_syntax = match.group(0)

                # Check against problematic patterns
                for pattern, recommendation in self.bad_link_text_patterns.items():
                    if re.match(pattern, link_text, re.IGNORECASE):
                        self.add_issue(
                            file_path,
                            line_num,
                            "link_text",
                            "error",
                            f"Non-descriptive link text: '{match.group(1)}'",
                            recommendation,
                            element_content=link_syntax,
                            wcag_guideline="WCAG 2.1 SC 2.4.4 (Link Purpose)",
                        )
                        break

                # Check for URL as link text
                if link_text.startswith(("http://", "https://", "www.")):
                    self.add_issue(
                        file_path,
                        line_num,
                        "link_text",
                        "warning",
                        f"URL used as link text: '{match.group(1)}'",
                        "Use descriptive text instead of raw URLs when possible",
                        element_content=link_syntax,
                        wcag_guideline="WCAG 2.1 SC 2.4.4 (Link Purpose)",
                    )

                # Check for very long link text
                if len(match.group(1)) > 100:
                    self.add_issue(
                        file_path,
                        line_num,
                        "link_text",
                        "warning",
                        f"Very long link text ({len(match.group(1))} characters)",
                        "Consider shorter, more concise link text",
                        element_content=link_syntax[:50] + "...",
                        wcag_guideline="WCAG 2.1 SC 2.4.4 (Link Purpose)",
                    )

    def check_table_accessibility(self, file_path: Path, content: str):
        """Check table structure for accessibility."""
        lines = content.split("\n")
        in_table = False
        table_start_line = 0
        table_has_header = False

        for line_num, line in enumerate(lines, 1):
            line = line.strip()

            # Detect table rows
            if "|" in line and line.startswith("|") and line.endswith("|"):
                if not in_table:
                    in_table = True
                    table_start_line = line_num
                    table_has_header = False

                # Check if this is a header separator row
                if re.match(r"^\|[\s\-:|]+\|$", line):
                    table_has_header = True

            elif in_table and line == "":
                # End of table
                if not table_has_header:
                    self.add_issue(
                        file_path,
                        table_start_line,
                        "table_accessibility",
                        "error",
                        "Table has no header row",
                        "Add a header row with column names and separator line",
                        wcag_guideline="WCAG 2.1 SC 1.3.1 (Info and Relationships)",
                    )
                in_table = False

            elif in_table and line and "|" not in line:
                # End of table (non-empty line that's not a table row)
                if not table_has_header:
                    self.add_issue(
                        file_path,
                        table_start_line,
                        "table_accessibility",
                        "error",
                        "Table has no header row",
                        "Add a header row with column names and separator line",
                        wcag_guideline="WCAG 2.1 SC 1.3.1 (Info and Relationships)",
                    )
                in_table = False

        # Check for table at end of file
        if in_table and not table_has_header:
            self.add_issue(
                file_path,
                table_start_line,
                "table_accessibility",
                "error",
                "Table has no header row",
                "Add a header row with column names and separator line",
                wcag_guideline="WCAG 2.1 SC 1.3.1 (Info and Relationships)",
            )

    def check_language_clarity(self, file_path: Path, content: str):
        """Check for language clarity issues."""
        lines = content.split("\n")

        # Common problematic phrases
        problematic_phrases = {
            r"\babove\b": 'Use specific references instead of "above"',
            r"\bbelow\b": 'Use specific references instead of "below"',
            r"\bhere\s+and\s+there\b": "Use specific locations",
            r"\bthis\s+and\s+that\b": "Use specific references",
            r"\bobviously\b": "Avoid assumptions about what is obvious",
            r"\bclearly\b": "Avoid assumptions about what is clear",
            r"\bsimply\b": "Avoid assumptions about difficulty",
            r"\bjust\b": "Avoid minimizing complexity",
        }

        for line_num, line in enumerate(lines, 1):
            for pattern, recommendation in problematic_phrases.items():
                if re.search(pattern, line, re.IGNORECASE):
                    self.add_issue(
                        file_path,
                        line_num,
                        "language_clarity",
                        "info",
                        "Potentially unclear language detected",
                        recommendation,
                        element_content=line.strip()[:50] + "..."
                        if len(line) > 50
                        else line.strip(),
                        wcag_guideline="WCAG 2.1 SC 3.1.3 (Unusual Words)",
                    )

    def check_list_structure(self, file_path: Path, content: str):
        """Check list structure and formatting."""
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            # Check for inconsistent list markers
            if re.match(r"^[\s]*[-*+]\s+", line):
                # This is a bullet list item
                stripped = line.lstrip()
                if len(stripped) > 0:
                    marker = stripped[0]
                    # Check if previous or next lines use different markers
                    for check_line_num in [line_num - 1, line_num + 1]:
                        if 1 <= check_line_num <= len(lines):
                            check_line = lines[check_line_num - 1]
                            if re.match(r"^[\s]*[-*+]\s+", check_line):
                                check_stripped = check_line.lstrip()
                                if check_stripped[0] != marker:
                                    self.add_issue(
                                        file_path,
                                        line_num,
                                        "list_structure",
                                        "warning",
                                        f"Inconsistent list markers (using '{marker}' and '{check_stripped[0]}')",
                                        "Use consistent list markers throughout the document",
                                        element_content=line.strip(),
                                    )
                                    break

    def check_file_accessibility(self, file_path: Path) -> list[AccessibilityIssue]:
        """Check all accessibility issues in a single file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            self.add_issue(
                file_path,
                1,
                "file_error",
                "error",
                f"Could not read file: {e}",
                "Ensure file is readable and properly encoded",
            )
            return []

        # Run all accessibility checks
        self.check_heading_structure(file_path, content)
        self.check_image_alt_text(file_path, content)
        self.check_link_text_quality(file_path, content)
        self.check_table_accessibility(file_path, content)
        self.check_language_clarity(file_path, content)
        self.check_list_structure(file_path, content)

        return self.issues

    def check_all_files(self) -> AccessibilitySummary:
        """Check accessibility for all documentation files."""
        md_files = self.find_markdown_files()
        print(f"🔍 Found {len(md_files)} markdown files")

        for file_path in md_files:
            initial_issue_count = len(self.issues)
            self.check_file_accessibility(file_path)
            new_issues = len(self.issues) - initial_issue_count
            print(
                f"{'✅' if new_issues == 0 else '⚠️'} Checked {file_path.relative_to(self.docs_root)} ({new_issues} issues)"
            )

        # Generate summary
        total_issues = len(self.issues)
        errors = sum(1 for issue in self.issues if issue.severity == "error")
        warnings = sum(1 for issue in self.issues if issue.severity == "warning")
        info = sum(1 for issue in self.issues if issue.severity == "info")

        issues_by_type = defaultdict(int)
        issues_by_file = defaultdict(int)

        for issue in self.issues:
            issues_by_type[issue.issue_type] += 1
            issues_by_file[issue.file_path] += 1

        return AccessibilitySummary(
            total_files=len(md_files),
            total_issues=total_issues,
            errors=errors,
            warnings=warnings,
            info=info,
            issues_by_type=dict(issues_by_type),
            issues_by_file=dict(issues_by_file),
            all_issues=self.issues,
        )

    def generate_report(
        self, summary: AccessibilitySummary, output_file: Path | None = None
    ) -> str:
        """Generate a detailed accessibility report."""
        report_lines = [
            "# Documentation Accessibility Report",
            f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            f"- **Total Files**: {summary.total_files}",
            f"- **Total Issues**: {summary.total_issues}",
            f"- **Errors**: {summary.errors} ❌",
            f"- **Warnings**: {summary.warnings} ⚠️",
            f"- **Info**: {summary.info} ℹ️",
            "",
        ]

        if summary.issues_by_type:
            report_lines.extend(["## Issues by Type", ""])
            for issue_type, count in sorted(summary.issues_by_type.items()):
                report_lines.append(
                    f"- **{issue_type.replace('_', ' ').title()}**: {count}"
                )
            report_lines.append("")

        if summary.all_issues:
            report_lines.extend(["## Detailed Issues", ""])

            # Group issues by file
            issues_by_file = defaultdict(list)
            for issue in summary.all_issues:
                issues_by_file[issue.file_path].append(issue)

            for file_path in sorted(issues_by_file.keys()):
                file_issues = issues_by_file[file_path]
                report_lines.extend(
                    [f"### {file_path}", f"**{len(file_issues)} issues found**", ""]
                )

                # Sort issues by line number
                for issue in sorted(file_issues, key=lambda x: x.line_number):
                    severity_emoji = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}[
                        issue.severity
                    ]
                    report_lines.extend(
                        [
                            f"#### Line {issue.line_number}: {issue.issue_type.replace('_', ' ').title()} {severity_emoji}",
                            f"**Description**: {issue.description}",
                            f"**Recommendation**: {issue.recommendation}",
                        ]
                    )

                    if issue.element_content:
                        report_lines.append(f"**Element**: `{issue.element_content}`")

                    if issue.wcag_guideline:
                        report_lines.append(f"**WCAG**: {issue.wcag_guideline}")

                    report_lines.append("")
        else:
            report_lines.extend(
                [
                    "## ✅ No Accessibility Issues Found!",
                    "The documentation meets basic accessibility standards.",
                    "",
                ]
            )

        report_lines.extend(
            [
                "## Accessibility Guidelines",
                "",
                "This report checks for compliance with:",
                "- **WCAG 2.1 Level AA** standards",
                "- **Section 508** accessibility requirements",
                "- **Markdown accessibility** best practices",
                "",
                "For more information:",
                "- [Web Content Accessibility Guidelines (WCAG) 2.1](https://www.w3.org/WAI/WCAG21/quickref/)",
                "- [Markdown Accessibility Guide](https://daringfireball.net/projects/markdown/syntax)",
                "",
            ]
        )

        report_content = "\n".join(report_lines)

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report_content)
            print(f"📄 Report saved to {output_file}")

        return report_content


def main():
    """Main entry point for the accessibility checker."""
    parser = argparse.ArgumentParser(description="Check accessibility of documentation")
    parser.add_argument(
        "docs_dir",
        nargs="?",
        default="docs",
        help="Documentation directory (default: docs)",
    )
    parser.add_argument(
        "--output", type=str, help="Output report file (default: console only)"
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with error code if accessibility issues found",
    )
    parser.add_argument(
        "--severity-threshold",
        choices=["error", "warning", "info"],
        default="error",
        help="Minimum severity to cause failure",
    )

    args = parser.parse_args()

    docs_path = Path(args.docs_dir)
    if not docs_path.exists():
        print(f"❌ Documentation directory not found: {docs_path}")
        sys.exit(1)

    print(f"♿ Checking accessibility in {docs_path}")

    checker = DocumentationAccessibilityChecker(docs_root=docs_path)
    summary = checker.check_all_files()

    # Print console summary
    print()
    print("📊 Accessibility Check Summary:")
    print(f"   Files checked: {summary.total_files}")
    print(f"   Total issues: {summary.total_issues}")
    print(f"   Errors: {summary.errors} ❌")
    print(f"   Warnings: {summary.warnings} ⚠️")
    print(f"   Info: {summary.info} ℹ️")

    if args.json:
        # Output as JSON
        json_data = {
            "summary": asdict(summary),
            "issues": [asdict(issue) for issue in summary.all_issues],
        }
        json_output = json.dumps(json_data, indent=2)

        if args.output:
            with open(args.output, "w") as f:
                f.write(json_output)
        else:
            print("\n" + json_output)
    else:
        # Generate markdown report
        output_file = Path(args.output) if args.output else None
        report = checker.generate_report(summary, output_file)

        if not args.output:
            print("\n" + report)

    # Exit with error if requested and issues found
    if args.fail_on_error:
        threshold_counts = {
            "error": summary.errors,
            "warning": summary.errors + summary.warnings,
            "info": summary.total_issues,
        }

        if threshold_counts[args.severity_threshold] > 0:
            sys.exit(1)


if __name__ == "__main__":
    main()
