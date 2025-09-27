#!/usr/bin/env bash
llms . "*.txt"
uvx hatch clean
gitnextver .
uvx hatch build
uv publish
