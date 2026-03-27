#!/usr/bin/env bash
# На CI перезаписывает FLUTTER_BUILD_NUMBER на уровне Xcode (ios/Flutter/CIVersion.xcconfig),
# чтобы даже при коллизии с переменной Codemagic BUILD_NUMBER=11 в IPA не попадала чужая версия.
# Локально скрипт ничего не делает (нет CM_BUILD_ID / GITHUB_ACTIONS / CI=true).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

is_ci() {
  [ -n "${CM_BUILD_ID:-}" ] \
    || [ -n "${GITHUB_ACTIONS:-}" ] \
    || [ -n "${GITLAB_CI:-}" ] \
    || [ -n "${CONTINUOUS_INTEGRATION:-}" ] \
    || [ "${CI:-false}" = "true" ]
}

if ! is_ci; then
  echo "ci_ios_version_override: не CI — CIVersion.xcconfig не создаём (локальные сборки через pubspec)."
  exit 0
fi

VERSION_LINE=$(grep "^version:" pubspec.yaml)
IOS_VERSION_NAME=$(echo "$VERSION_LINE" | sed 's/version: //' | sed 's/+.*//')
PUBSPEC_BUILD=$(echo "$VERSION_LINE" | sed 's/.*+//')
if ! [[ "$PUBSPEC_BUILD" =~ ^[0-9]+$ ]]; then
  echo "ERROR: в pubspec.yaml нужна строка вида version: 1.0.3+N"
  exit 1
fi

BN=$(date +%s)
if [ "$BN" -le "$PUBSPEC_BUILD" ]; then
  BN=$((PUBSPEC_BUILD + 1))
fi
if [ "$BN" -le 11 ]; then
  BN=12
fi

OUT="$ROOT/ios/Flutter/CIVersion.xcconfig"
cat > "$OUT" <<EOF
// Сгенерировано scripts/ci_ios_version_override.sh (только CI). Перекрывает значения из Generated.xcconfig.
FLUTTER_BUILD_NAME=$IOS_VERSION_NAME
FLUTTER_BUILD_NUMBER=$BN
EOF

echo "ci_ios_version_override: записан $OUT"
echo "  FLUTTER_BUILD_NAME=$IOS_VERSION_NAME"
echo "  FLUTTER_BUILD_NUMBER=$BN"
