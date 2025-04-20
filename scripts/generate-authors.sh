#!/usr/bin/env bash
set -e

# Navigate to the root of the repo (in case someone runs it from elsewhere)
cd "$(git rev-parse --show-toplevel)"

{
  cat <<-'EOH'
# This file lists all individuals who have contributed content
# to this repository.
# It is automatically generated using scripts/generate-authors.sh.
EOH
  echo
  git log --format='%aN <%aE>' | LC_ALL=C.UTF-8 sort -uf
} > AUTHORS

echo "✅ AUTHORS file has been updated!"
