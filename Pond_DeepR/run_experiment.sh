#!/usr/bin/env bash
# Usage: ./run_experiment.sh <variant_file> <run_name>
# Example: ./run_experiment.sh reward_functions/variant_1_baseline.py run_v1

set -e

VARIANT="${1:?Usage: $0 <reward_file> <run_name>}"
RUN_NAME="${2:?Usage: $0 <reward_file> <run_name>}"

echo "==> Copying reward function: $VARIANT"
cp "$VARIANT" custom_files/reward_function.py

echo "==> Starting training: $RUN_NAME"
export DR_LOCAL_S3_MODEL_PREFIX="$RUN_NAME"
source bin/activate.sh
dr-start-training -w

echo "==> Training finished. Saving logs to logs/$RUN_NAME/"
mkdir -p "logs/$RUN_NAME"
cp -r logs/training "logs/$RUN_NAME/" 2>/dev/null || true

echo "==> Done. Review logs/$RUN_NAME/ for metrics."
