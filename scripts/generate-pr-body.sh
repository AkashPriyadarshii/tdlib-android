#!/bin/bash
# Generate PR body for version bump PRs
# Usage: ./scripts/generate-pr-body.sh <old_version> <new_version>
set -euo pipefail

OLD_VERSION="${1:?}"
NEW_VERSION="${2:?}"

# Extract CHANGELOG section for new version from upstream
CHANGELOG=$(curl -s "https://raw.githubusercontent.com/tdlib/td/master/CHANGELOG.md" \
    | awk "/^## Changes in $NEW_VERSION/,/^## Changes in /" \
    | head -50 \
    || echo "Could not extract CHANGELOG section. See: https://github.com/tdlib/td/blob/master/CHANGELOG.md")

# Read checksums
CHECKSUMS=$(cat checksums.txt 2>/dev/null || echo "Not available")

# Read TdApi diff summary
DIFF_LINES=$(wc -l < tdapi_diff.txt 2>/dev/null || echo "0")

cat << EOF
## TDLib ${OLD_VERSION} → ${NEW_VERSION}

### TdApi.java changes
${DIFF_LINES} lines changed. Review for breaking API changes before merging.

<details>
<summary>View TdApi.java diff</summary>

\`\`\`diff
$(head -200 tdapi_diff.txt 2>/dev/null || echo "Diff not available — first release")
\`\`\`
</details>

### Upstream CHANGELOG
${CHANGELOG}

### Artifact Checksums
\`\`\`
${CHECKSUMS}
\`\`\`

### Smoke Test
$(cat smoke_test_result.txt 2>/dev/null || echo "Not available")

---
**Merge this PR to publish TDLib ${NEW_VERSION} to Maven Central.**

_If TdApi.java diff shows breaking changes (removed methods, changed signatures): check if ktx wrapper needs updates before merging._
EOF
