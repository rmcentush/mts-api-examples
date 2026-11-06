#!/bin/sh
# Download the Archive (every past MTS event) and unpack it to mts-events.csv.
#   MTS_KEY=mts_... sh archive.sh
set -eu
BASE_URL="${MTS_BASE_URL:-https://monitor-the-situation.com}"
curl --fail-with-body --silent --show-error \
  -H "Authorization: Bearer $MTS_KEY" \
  -o mts-events.csv.gz "$BASE_URL/v1/archive.csv.gz"
gunzip -f mts-events.csv.gz
echo "Saved mts-events.csv ($(($(wc -l < mts-events.csv) - 1)) events)"
