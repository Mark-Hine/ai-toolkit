#!/usr/bin/env bash
# Copies the shared rewards fixture into the empty run workspace.
set -eu
cp -R "$(dirname "$0")/../_fixtures/rewards/." .
