#!/usr/bin/env bash
# this_file: publish.sh
set -e

llms . "*.txt"
uvx hatch clean
gitnextver .

# Ensure HEAD has an exact version tag so hatch-vcs generates a clean version (no local/dev identifier like +g...)
if ! git describe --tags --exact-match HEAD >/dev/null 2>&1; then
    NEXT_TAG=$(python3 -c "import git, re; repo=git.Repo('.'); tags=[t.name for t in repo.tags]; version_tags=[tuple(map(int, m.groups())) for t in tags if (m:=re.match(r'^v?(\d+)\.(\d+)\.(\d+)$', t))]; latest=max(version_tags, default=(1,0,-1)); print(f'v{latest[0]}.{latest[1]}.{latest[2]+1}')")
    echo "[i] HEAD is untagged. Auto-tagging HEAD as ${NEXT_TAG}..."
    git tag "${NEXT_TAG}"
    git push origin "${NEXT_TAG}"
fi

uvx hatch build
uv publish