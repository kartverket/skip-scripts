#!/usr/bin/env bash

# Delete all pods with a given Istio revision

# Ensure jq and kubectl are available on the classpath
for cmd in jq kubectl; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Error: $cmd is not found on the classpath. Please install it and try again."
    exit 1
  fi
done

# Check for required arguments
if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <kubecontext> <revision> [--no-dry-run]"
  exit 1
fi

CONTEXT="$1"
REVISION="$2"
DRY_RUN=1

if [ "$#" -eq 3 ] && [ "$3" == "--no-dry-run" ]; then
  DRY_RUN=0
fi

echo "Running against context '$CONTEXT'. Looking for pods with revision=$REVISION"

# Fetch pods with the given annotation for the specified revision
PODS_TO_DELETE=$(kubectl get pods --all-namespaces --context="$CONTEXT" -o json | jq -r --arg REVISION "$REVISION" '.items[] | select((.metadata.annotations["sidecar.istio.io/status"] | fromjson? | .revision? // empty) == $REVISION) | .metadata.namespace + "/" + .metadata.name' | grep -v '^$')

# Check if PODS_TO_DELETE is empty
if [ -z "$PODS_TO_DELETE" ]; then
  echo "No pods found with revision $REVISION"
  exit 0
fi

# Either echo the pods or delete them based on the dry-run flag
if [ "$DRY_RUN" -eq 1 ]; then
  echo "$PODS_TO_DELETE" | while read -r pod; do
    echo "Would have deleted $pod"
  done
else
  echo "$PODS_TO_DELETE" | while read -r pod; do
    kubectl delete pod --context="$CONTEXT" "$pod"
  done
fi
