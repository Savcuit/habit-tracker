#!/usr/bin/env bash
# Builds HabitTracker.apk on Linux/arm64 with the Debian Android tools.
# No Gradle, no Android Studio, no Windows.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SDK="$HOME/android-sdk"
BIN="$SDK/debian/bin"
LIB="$SDK/debian/lib"
ANDROID_JAR="$SDK/android-13/android.jar"
D8_JAR="$SDK/android-14/lib/d8.jar"
KEYSTORE="${KEYSTORE:-$HOME/.hermes/keys/habittracker.p12}"
KEY_ALIAS="${KEY_ALIAS:-habittracker}"
STORE_PASS="${STORE_PASS:-$(cat "$HOME/.hermes/keys/habittracker.pass" 2>/dev/null || echo android)}"
OUT="${OUT:-$HERE/../release/HabitTracker.apk}"

export LD_LIBRARY_PATH="$LIB:${LD_LIBRARY_PATH:-}"

rm -rf "$HERE/build"
mkdir -p "$HERE/build/gen" "$HERE/build/classes" "$HERE/build/dex"

echo "1/5 resources"
"$BIN/aapt2" compile --dir "$HERE/res" -o "$HERE/build/res.zip"

echo "2/5 link"
"$BIN/aapt2" link \
  -o "$HERE/build/base.apk" \
  -I "$ANDROID_JAR" \
  --manifest "$HERE/AndroidManifest.xml" \
  -A "$HERE/assets" \
  --java "$HERE/build/gen" \
  --min-sdk-version 24 --target-sdk-version 34 \
  "$HERE/build/res.zip"

echo "3/5 compile java"
find "$HERE/src" "$HERE/build/gen" -name "*.java" > "$HERE/build/sources.txt"
javac -nowarn --release 8 -classpath "$ANDROID_JAR" \
  -d "$HERE/build/classes" @"$HERE/build/sources.txt" 2>&1 | grep -v "bootstrap class path" || true

echo "4/5 dex"
find "$HERE/build/classes" -name "*.class" > "$HERE/build/classes.txt"
java -cp "$D8_JAR" com.android.tools.r8.D8 \
  --lib "$ANDROID_JAR" --min-api 24 --output "$HERE/build/dex" @"$HERE/build/classes.txt"

echo "5/5 package, align, sign"
python3 - "$HERE/build/base.apk" "$HERE/build/dex/classes.dex" "$HERE/build/unsigned.apk" <<'PY'
import sys, zipfile, shutil
src, dex, out = sys.argv[1], sys.argv[2], sys.argv[3]
shutil.copy(src, out)
with zipfile.ZipFile(out, "a", zipfile.ZIP_DEFLATED) as z:
    z.write(dex, "classes.dex")
print("dex added")
PY

"$BIN/zipalign" -f 4 "$HERE/build/unsigned.apk" "$HERE/build/aligned.apk"

mkdir -p "$(dirname "$OUT")"
java -jar "$LIB/apksigner.jar" sign \
  --ks "$KEYSTORE" --ks-type PKCS12 --ks-key-alias "$KEY_ALIAS" \
  --ks-pass "pass:$STORE_PASS" --key-pass "pass:$STORE_PASS" \
  --out "$OUT" "$HERE/build/aligned.apk"

java -jar "$LIB/apksigner.jar" verify "$OUT"
echo "built $OUT ($(stat -c%s "$OUT") bytes)"
