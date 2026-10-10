#!/bin/sh
# usage: preview.sh <svg> <png>  (A3 SVG → 1680px PNG)
S=$(mktemp --suffix=.svg)
sed 's/width="420mm" height="297mm"/width="1680" height="1188"/' "$1" > "$S"
node "$(dirname "$0")/shot.mjs" "$S" "$2" 1680 1188
rm -f "$S"
