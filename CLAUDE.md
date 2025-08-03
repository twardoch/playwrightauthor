# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 1. Project Overview

PlaywrightAuthor is a convenience package for Microsoft Playwright that handles browser automation setup. It automatically manages Chrome for Testing installation, authentication with user profiles, and provides ready-to-use Browser objects through simple context managers.

## 2. Key Architecture

**Core Design Pattern**: The library follows a context manager pattern with `Browser()` and `AsyncBrowser()` classes that return authenticated Playwright browser objects.

**Main Components** (planned structure):
- `playwrightauthor/author.py` - Core Browser/AsyncBrowser classes (main API)
- `playwrightauthor/browser_manager.py` - Chrome installation/process management 
- `playwrightauthor/onboarding.py` - User guidance for authentication
- `playwrightauthor/cli.py` - Fire-powered CLI interface
- `playwrightauthor/utils/` - Logger and cross-platform path utilities

**Current State**: The project is in early development. The main implementation exists as a legacy scraper in `old/google_docs_scraper_simple.py` that demonstrates the core concept of connecting to an existing Chrome debug session.

## 3. Development Commands

### 3.1. Environment Setup
```bash
# Initial setup with uv
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv --python 3.12
uv init
uv add playwright rich fire loguru platformdirs requests psutil
```

### 3.2. Code Quality Pipeline
After any Python changes, run:
```bash
fd -e py -x uvx autoflake -i {}; \
fd -e py -x uvx pyupgrade --py312-plus {}; \
fd -e py -x uvx ruff check --output-format=github --fix --unsafe-fixes {}; \
fd -e py -x uvx ruff format --respect-gitignore --target-version py312 {}; \
python -m pytest
```

### 3.3. Testing
- Run tests: `python -m pytest`
- Tests are located in `tests/` directory
- Current tests may be integration tests requiring live Chrome instance

### 3.4. CLI Usage
Once implemented:
```bash
python -m playwrightauthor status  # Check browser status
```

## 4. Code Standards

- **File headers**: Every Python file should include a `this_file:` comment with the relative path
- **Dependencies**: Use uv script headers with `# /// script` blocks
- **Type hints**: Use modern Python type hints (list, dict, | for unions)
- **Logging**: Use loguru with verbose flag support
- **CLI**: Use Fire for command-line interfaces with Rich for output

## 5. Browser Management Strategy

The core technical challenge is reliably managing Chrome for Testing:

1. **Detection**: Check if Chrome is running with `--remote-debugging-port=9222`
2. **Installation**: Prefer `npx puppeteer browsers install`, fallback to LKGV JSON downloads
3. **Process Management**: Kill non-debug instances, launch with persistent user-data-dir
4. **Connection**: Use Playwright's `connect_over_cdp()` to attach to debug session

## 6. Project Workflow

The project follows a documentation-driven development approach:
1. Read `WORK.md` and `PLAN.md` before making changes
2. Update documentation files after implementation
3. Use "Wait, but" reflection methodology for code review
4. Maintain minimal, self-contained commits

## 7. Dependencies

Core runtime dependencies:
- `playwright` - Browser automation
- `rich` - Terminal output formatting  
- `fire` - CLI generation
- `loguru` - Logging
- `platformdirs` - Cross-platform paths
- `requests` - HTTP client for downloads
- `psutil` - Process management

# Software Development Rules

## 8. Pre-Work Preparation

### 8.1. Before Starting Any Work
- **ALWAYS** read `WORK.md` in the main project folder for work progress
- Read `README.md` to understand the project
- STEP BACK and THINK HEAVILY STEP BY STEP about the task
- Consider alternatives and carefully choose the best option
- Check for existing solutions in the codebase before starting

### 8.2. Project Documentation to Maintain
- `README.md` - purpose and functionality
- `CHANGELOG.md` - past change release notes (accumulative)
- `PLAN.md` - detailed future goals, clear plan that discusses specifics
- `TODO.md` - flat simplified itemized `- [ ]`-prefixed representation of `PLAN.md`
- `WORK.md` - work progress updates

## 9. General Coding Principles

### 9.1. Core Development Approach
- Iterate gradually, avoiding major changes
- Focus on minimal viable increments and ship early
- Minimize confirmations and checks
- Preserve existing code/structure unless necessary
- Check often the coherence of the code you're writing with the rest of the code
- Analyze code line-by-line

### 9.2. Code Quality Standards
- Use constants over magic numbers
- Write explanatory docstrings/comments that explain what and WHY
- Explain where and how the code is used/referred to elsewhere
- Handle failures gracefully with retries, fallbacks, user guidance
- Address edge cases, validate assumptions, catch errors early
- Let the computer do the work, minimize user decisions
- Reduce cognitive load, beautify code
- Modularize repeated logic into concise, single-purpose functions
- Favor flat over nested structures

## 10. Tool Usage (When Available)

### 10.1. Additional Tools
- If we need a new Python project, run `curl -LsSf https://astral.sh/uv/install.sh | sh; uv venv --python 3.12; uv init; uv add fire rich; uv sync`
- Use `tree` CLI app if available to verify file locations
- Check existing code with `.venv` folder to scan and consult dependency source code
- Run `DIR="."; uvx codetoprompt --compress --output "$DIR/llms.txt"  --respect-gitignore --cxml --exclude "*.svg,.specstory,*.md,*.txt,ref,testdata,*.lock,*.svg" "$DIR"` to get a condensed snapshot of the codebase into `llms.txt`

## 11. File Management

### 11.1. File Path Tracking
- **MANDATORY**: In every source file, maintain a `this_file` record showing the path relative to project root
- Place `this_file` record near the top:
- As a comment after shebangs in code files
- In YAML frontmatter for Markdown files
- Update paths when moving files
- Omit leading `./`
- Check `this_file` to confirm you're editing the right file

## 12. Python-Specific Guidelines

### 12.1. PEP Standards
- PEP 8: Use consistent formatting and naming, clear descriptive names
- PEP 20: Keep code simple and explicit, prioritize readability over cleverness
- PEP 257: Write clear, imperative docstrings
- Use type hints in their simplest form (list, dict, | for unions)

### 12.2. Modern Python Practices
- Use f-strings and structural pattern matching where appropriate
- Write modern code with `pathlib`
- ALWAYS add "verbose" mode loguru-based logging & debug-log
- Use `uv add` 
- Use `uv pip install` instead of `pip install`
- Prefix Python CLI tools with `python -m` (e.g., `python -m pytest`)

### 12.3. CLI Scripts Setup
For CLI Python scripts, use `fire` & `rich`, and start with:
```python
#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["PKG1", "PKG2"]
# ///
# this_file: PATH_TO_CURRENT_FILE
```

### 12.4. Post-Edit Python Commands
```bash
fd -e py -x uvx autoflake -i {}; fd -e py -x uvx pyupgrade --py312-plus {}; fd -e py -x uvx ruff check --output-format=github --fix --unsafe-fixes {}; fd -e py -x uvx ruff format --respect-gitignore --target-version py312 {}; python -m pytest;
```

## 13. Post-Work Activities

### 13.1. Critical Reflection
- After completing a step, say "Wait, but" and do additional careful critical reasoning
- Go back, think & reflect, revise & improve what you've done
- Don't invent functionality freely
- Stick to the goal of "minimal viable next version"

### 13.2. Documentation Updates
- Update `WORK.md` with what you've done and what needs to be done next
- Document all changes in `CHANGELOG.md`
- Update `TODO.md` and `PLAN.md` accordingly

## 14. Work Methodology

### 14.1. Virtual Team Approach
Be creative, diligent, critical, relentless & funny! Lead two experts:
- **"Ideot"** - for creative, unorthodox ideas
- **"Critin"** - to critique flawed thinking and moderate for balanced discussions

Collaborate step-by-step, sharing thoughts and adapting. If errors are found, step back and focus on accuracy and progress.

### 14.2. Continuous Work Mode
- Treat all items in `PLAN.md` and `TODO.md` as one huge TASK
- Work on implementing the next item
- Review, reflect, refine, revise your implementation
- Periodically check off completed issues
- Continue to the next item without interruption

## 15. Special Commands

### 15.1. `/plan` Command - Transform Requirements into Detailed Plans

When I say "/plan [requirement]", you must:

1. **DECONSTRUCT** the requirement:
- Extract core intent, key features, and objectives
- Identify technical requirements and constraints
- Map what's explicitly stated vs. what's implied
- Determine success criteria

2. **DIAGNOSE** the project needs:
- Audit for missing specifications
- Check technical feasibility
- Assess complexity and dependencies
- Identify potential challenges

3. **RESEARCH** additional material: 
- Repeatedly call the `perplexity_ask` and request up-to-date information or additional remote context
- Repeatedly call the `context7` tool and request up-to-date software package documentation
- Repeatedly call the `codex` tool and request additional reasoning, summarization of files and second opinion

4. **DEVELOP** the plan structure:
- Break down into logical phases/milestones
- Create hierarchical task decomposition
- Assign priorities and dependencies
- Add implementation details and technical specs
- Include edge cases and error handling
- Define testing and validation steps

5. **DELIVER** to `PLAN.md`:
- Write a comprehensive, detailed plan with:
 - Project overview and objectives
 - Technical architecture decisions
 - Phase-by-phase breakdown
 - Specific implementation steps
 - Testing and validation criteria
 - Future considerations
- Simultaneously create/update `TODO.md` with the flat itemized `- [ ]` representation

**Plan Optimization Techniques:**
- **Task Decomposition:** Break complex requirements into atomic, actionable tasks
- **Dependency Mapping:** Identify and document task dependencies
- **Risk Assessment:** Include potential blockers and mitigation strategies
- **Progressive Enhancement:** Start with MVP, then layer improvements
- **Technical Specifications:** Include specific technologies, patterns, and approaches

### 15.2. `/report` Command

1. Read all `./TODO.md` and `./PLAN.md` files
2. Analyze recent changes
3. Document all changes in `./CHANGELOG.md`
4. Remove completed items from `./TODO.md` and `./PLAN.md`
5. Ensure `./PLAN.md` contains detailed, clear plans with specifics
6. Ensure `./TODO.md` is a flat simplified itemized representation

### 15.3. `/work` Command

1. Read all `./TODO.md` and `./PLAN.md` files and reflect
2. Write down the immediate items in this iteration into `./WORK.md`
3. Work on these items
4. Think, contemplate, research, reflect, refine, revise
5. Be careful, curious, vigilant, energetic
6. Verify your changes and think aloud
7. Consult, research, reflect
8. Periodically remove completed items from `./WORK.md`
9. Tick off completed items from `./TODO.md` and `./PLAN.md`
10. Update `./WORK.md` with improvement tasks
11. Execute `/report`
12. Continue to the next item

## 16. Additional Guidelines

- Ask before extending/refactoring existing code that may add complexity or break things
- Work tirelessly without constant updates when in continuous work mode
- Only notify when you've completed all `PLAN.md` and `TODO.md` items

## 17. Command Summary

- `/plan [requirement]` - Transform vague requirements into detailed `PLAN.md` and `TODO.md`
- `/report` - Update documentation and clean up completed tasks
- `/work` - Enter continuous work mode to implement plans
- You may use these commands autonomously when appropriate

**TL;DR for PlaywrightAuthor Codebase**

**1. Core Purpose & Value Proposition:**
PlaywrightAuthor is a Python convenience library built on top of Microsoft Playwright. Its primary goal is to eliminate the boilerplate setup for browser automation. It automatically finds or installs a "Chrome for Testing" instance, manages its process (ensuring it runs in debug mode), handles user authentication by reusing a persistent profile, and provides a ready-to-use, authenticated Playwright `Browser` object within a simple context manager (`with Browser() as browser:`).

**2. Key Architectural Components:**
*   **Main API (`author.py`):** Exposes the core `Browser()` and `AsyncBrowser()` context managers, which are the main entry points for the user.
*   **Browser Management (`browser/` & `browser_manager.py`):** This is the technical core of the library. It's a modular system responsible for:
    *   `finder.py`: Robustly discovering the Chrome executable across macOS, Windows, and Linux, checking over 20 standard and non-standard locations per platform.
    *   `installer.py`: Downloading the correct Chrome for Testing build using official JSON endpoints, with progress bars and SHA256 validation.
    *   `launcher.py`: Launching the Chrome process with the remote debugging port (`--remote-debugging-port=9222`).
    *   `process.py`: Managing the Chrome process, including gracefully killing existing non-debug instances and verifying the new process is ready.
*   **User Experience (`onboarding.py`, `cli.py`):**
    *   `onboarding.py`: If the user is not logged into necessary services, it serves a local HTML page (`templates/onboarding.html`) to guide them through the login process.
    *   `cli.py`: A `fire`-powered command-line interface for status checks (`status`) and cache clearing (`clear-cache`), with `rich` for formatted output.
*   **Configuration & State (`config.py`, `state_manager.py`):** Handles library configuration (e.g., timeouts, paths) and persists the state of the browser (e.g., installation path, version) to avoid redundant work.
*   **Utilities (`utils/`):** Cross-platform path management (`paths.py`) and `loguru`-based logging (`logger.py`).

**3. Development & Quality:**
*   **Workflow:** The project is documentation-driven, using `PLAN.md`, `TODO.md`, and `WORK.md` to guide development. It emphasizes iterative, minimal commits.
*   **Tooling:** Uses `uv` for environment and dependency management. The build system is `hatch` with `hatch-vcs` for versioning based on git tags.
*   **CI/CD (`.github/workflows/ci.yml`):** A comprehensive GitHub Actions pipeline tests the library on Ubuntu, Windows, and macOS. It runs linting (`ruff`), type checking (`mypy`), and a full `pytest` suite with coverage reporting to Codecov.
*   **Code Quality:** The codebase is fully type-hinted. A strict quality pipeline (`ruff`, `autoflake`, `pyupgrade`) is enforced and documented. Every file includes a `this_file:` comment for easy path reference.

**4. Current Status & Roadmap:**
The project has completed its initial phases focused on robustness, error handling, and cross-platform compatibility. It is now in the "Elegance and Performance" phase, which involves refactoring the architecture (e.g., separating state and config management), optimizing performance (e.g., lazy loading), and adding advanced features like browser profile management. Future phases will focus on improving the CLI, documentation, and user experience.
