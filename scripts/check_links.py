#!/usr/bin/env python3
# this_file: scripts/check_links.py
"""
Documentation Link Checker for PlaywrightAuthor

Scans all markdown files in the documentation directory and validates:
- Internal links to files and sections
- External URLs for accessibility
- Cross-references between documentation files

Suitable for CI/CD integration with configurable reporting.
"""

import argparse
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    print("❌ Missing required dependencies. Install with:")
    print("pip install requests")
    sys.exit(1)


@dataclass
class LinkResult:
    """Result of checking a single link."""

    url: str
    source_file: str
    line_number: int
    is_valid: bool
    error_message: str | None = None
    response_code: int | None = None
    response_time: float | None = None


@dataclass
class CheckSummary:
    """Summary of all link checking results."""

    total_files: int
    total_links: int
    internal_links: int
    external_links: int
    valid_links: int
    broken_links: int
    errors: list[LinkResult]
    warnings: list[LinkResult]


class DocumentationLinkChecker:
    """Comprehensive link checker for markdown documentation."""

    def __init__(self, docs_root: Path, timeout: int = 10, max_workers: int = 10):
        self.docs_root = Path(docs_root).resolve()
        self.timeout = timeout
        self.max_workers = max_workers

        # Setup HTTP session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Common headers to avoid being blocked
        self.session.headers.update(
            {
                "User-Agent": "PlaywrightAuthor-LinkChecker/1.0 (+https://github.com/twardoch/playwrightauthor)"
            }
        )

        # Link patterns
        self.markdown_link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
        self.reference_link_pattern = re.compile(r"\[([^\]]+)\]:\s*(.+)")

        # Results storage
        self.results: list[LinkResult] = []
        self.checked_external_urls: dict[str, LinkResult] = {}

    def find_markdown_files(self) -> list[Path]:
        """Find all markdown files in the documentation directory."""
        md_files = []
        for pattern in ["*.md", "*.markdown"]:
            md_files.extend(self.docs_root.rglob(pattern))
        return sorted(md_files)

    def extract_links_from_file(self, file_path: Path) -> list[tuple[str, str, int]]:
        """Extract all links from a markdown file.

        Returns:
            List of (link_text, url, line_number) tuples
        """
        links = []
        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                # Standard markdown links [text](url)
                for match in self.markdown_link_pattern.finditer(line):
                    link_text, url = match.groups()
                    links.append((link_text, url.strip(), line_num))

                # Reference-style links [text]: url
                for match in self.reference_link_pattern.finditer(line):
                    link_text, url = match.groups()
                    links.append((link_text, url.strip(), line_num))

        except Exception as e:
            print(f"⚠️  Error reading {file_path}: {e}")

        return links

    def is_internal_link(self, url: str) -> bool:
        """Check if a URL is an internal link."""
        if url.startswith(("http://", "https://", "ftp://", "mailto:")):
            return False
        return True

    def resolve_internal_link(
        self, url: str, source_file: Path
    ) -> tuple[bool, str | None]:
        """Resolve and validate an internal link.

        Returns:
            (is_valid, error_message)
        """
        # Handle anchor-only links (e.g., #section)
        if url.startswith("#"):
            return self.check_section_exists(url[1:], source_file)

        # Split URL and anchor
        if "#" in url:
            file_part, anchor = url.split("#", 1)
        else:
            file_part, anchor = url, None

        # Resolve relative path
        if file_part:
            if file_part.startswith("/"):
                # Absolute path from docs root
                target_path = self.docs_root / file_part.lstrip("/")
            else:
                # Relative path from source file
                target_path = (source_file.parent / file_part).resolve()
        else:
            target_path = source_file

        # Check if target file exists
        if not target_path.exists():
            return False, f"File not found: {target_path}"

        # If there's an anchor, check if section exists
        if anchor:
            return self.check_section_exists(anchor, target_path)

        return True, None

    def check_section_exists(
        self, anchor: str, file_path: Path
    ) -> tuple[bool, str | None]:
        """Check if a section anchor exists in a markdown file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Convert anchor to lowercase and replace spaces/special chars
            normalized_anchor = anchor.lower().replace(" ", "-")
            normalized_anchor = re.sub(r"[^a-z0-9\\-_]", "", normalized_anchor)

            # Look for headers that would generate this anchor
            header_patterns = [
                rf"^#{1, 6}\\s+.*{re.escape(anchor)}.*$",
                rf"^#{1, 6}\\s+.*{re.escape(normalized_anchor)}.*$",
            ]

            for pattern in header_patterns:
                if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                    return True, None

            return False, f"Section '#{anchor}' not found in {file_path.name}"

        except Exception as e:
            return False, f"Error checking section: {e}"

    def check_external_link(self, url: str) -> LinkResult:
        """Check if an external URL is accessible."""
        # Return cached result if already checked
        if url in self.checked_external_urls:
            cached = self.checked_external_urls[url]
            return LinkResult(
                url=url,
                source_file="",  # Will be set by caller
                line_number=0,  # Will be set by caller
                is_valid=cached.is_valid,
                error_message=cached.error_message,
                response_code=cached.response_code,
                response_time=cached.response_time,
            )

        start_time = time.time()
        try:
            response = self.session.head(
                url, timeout=self.timeout, allow_redirects=True
            )
            response_time = time.time() - start_time

            is_valid = response.status_code < 400
            result = LinkResult(
                url=url,
                source_file="",
                line_number=0,
                is_valid=is_valid,
                error_message=None if is_valid else f"HTTP {response.status_code}",
                response_code=response.status_code,
                response_time=response_time,
            )

        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            result = LinkResult(
                url=url,
                source_file="",
                line_number=0,
                is_valid=False,
                error_message=str(e),
                response_code=None,
                response_time=response_time,
            )

        # Cache the result (without file-specific info)
        self.checked_external_urls[url] = result
        return result

    def check_file_links(self, file_path: Path) -> list[LinkResult]:
        """Check all links in a single file."""
        file_results = []
        links = self.extract_links_from_file(file_path)

        for _link_text, url, line_num in links:
            if self.is_internal_link(url):
                # Internal link
                is_valid, error_msg = self.resolve_internal_link(url, file_path)
                result = LinkResult(
                    url=url,
                    source_file=str(file_path.relative_to(self.docs_root)),
                    line_number=line_num,
                    is_valid=is_valid,
                    error_message=error_msg,
                )
            else:
                # External link
                result = self.check_external_link(url)
                result.source_file = str(file_path.relative_to(self.docs_root))
                result.line_number = line_num

            file_results.append(result)

        return file_results

    def check_all_links(self) -> CheckSummary:
        """Check all links in all documentation files."""
        md_files = self.find_markdown_files()
        print(f"🔍 Found {len(md_files)} markdown files")

        all_results = []

        # Process files concurrently for external link checking
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(self.check_file_links, file_path): file_path
                for file_path in md_files
            }

            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    results = future.result()
                    all_results.extend(results)
                    print(
                        f"✅ Checked {file_path.relative_to(self.docs_root)} ({len(results)} links)"
                    )
                except Exception as e:
                    print(f"❌ Error checking {file_path}: {e}")

        self.results = all_results

        # Generate summary
        total_links = len(all_results)
        internal_links = sum(1 for r in all_results if self.is_internal_link(r.url))
        external_links = total_links - internal_links
        valid_links = sum(1 for r in all_results if r.is_valid)
        broken_links = total_links - valid_links

        errors = [r for r in all_results if not r.is_valid]
        warnings = []  # Could add warnings for slow responses, redirects, etc.

        return CheckSummary(
            total_files=len(md_files),
            total_links=total_links,
            internal_links=internal_links,
            external_links=external_links,
            valid_links=valid_links,
            broken_links=broken_links,
            errors=errors,
            warnings=warnings,
        )

    def generate_report(
        self, summary: CheckSummary, output_file: Path | None = None
    ) -> str:
        """Generate a detailed report of link checking results."""
        report_lines = [
            "# Documentation Link Check Report",
            f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            f"- **Total Files**: {summary.total_files}",
            f"- **Total Links**: {summary.total_links}",
            f"- **Internal Links**: {summary.internal_links}",
            f"- **External Links**: {summary.external_links}",
            f"- **Valid Links**: {summary.valid_links} ✅",
            f"- **Broken Links**: {summary.broken_links} ❌",
            "",
        ]

        if summary.errors:
            report_lines.extend(["## Broken Links", ""])

            for error in summary.errors:
                report_lines.extend(
                    [
                        f"### {error.source_file}:{error.line_number}",
                        f"- **URL**: {error.url}",
                        f"- **Error**: {error.error_message}",
                        f"- **Type**: {'Internal' if self.is_internal_link(error.url) else 'External'}",
                        "",
                    ]
                )
        else:
            report_lines.extend(
                [
                    "## ✅ All Links Valid!",
                    "No broken links found in the documentation.",
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
    """Main entry point for the link checker."""
    parser = argparse.ArgumentParser(description="Check links in documentation")
    parser.add_argument(
        "docs_dir",
        nargs="?",
        default="docs",
        help="Documentation directory (default: docs)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Timeout for external links (default: 10)",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=10,
        help="Max concurrent workers (default: 10)",
    )
    parser.add_argument(
        "--output", type=str, help="Output report file (default: console only)"
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with error code if broken links found",
    )

    args = parser.parse_args()

    docs_path = Path(args.docs_dir)
    if not docs_path.exists():
        print(f"❌ Documentation directory not found: {docs_path}")
        sys.exit(1)

    print(f"🔗 Checking links in {docs_path}")

    checker = DocumentationLinkChecker(
        docs_root=docs_path, timeout=args.timeout, max_workers=args.max_workers
    )

    summary = checker.check_all_links()

    # Print console summary
    print()
    print("📊 Link Check Summary:")
    print(f"   Files checked: {summary.total_files}")
    print(f"   Total links: {summary.total_links}")
    print(f"   Valid links: {summary.valid_links} ✅")
    print(f"   Broken links: {summary.broken_links} ❌")

    if args.json:
        # Output as JSON
        json_data = {
            "summary": asdict(summary),
            "results": [asdict(r) for r in checker.results],
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

    # Exit with error if requested and broken links found
    if args.fail_on_error and summary.broken_links > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
