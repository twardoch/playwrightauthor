#!/usr/bin/env bash
# this_file: src_docs/build.sh
# Build the adjacent site; remaining arguments are forwarded to the renderer.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
export PYTHONPATH="$PWD:$PWD/src:$PWD/../src:$PWD/..${PYTHONPATH:+:$PYTHONPATH}"

if [[ "${1:-}" == build ]]; then shift; fi
exec uvx --python 3.12 --from mkdocs==1.6.1 \
  --with mkdocs-material \
  --with 'mkdocstrings[python]' \
  --with pymdown-extensions \
  mkdocs build --config-file mkdocs.yml "$@"
