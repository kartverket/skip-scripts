#!/bin/bash
set -eo pipefail

CONTEXT=$(kubectl config current-context)

echo "Getting dangling Argo-managed namespaces for context $CONTEXT"

MANAGED_BY_LABEL_KEY="app.kubernetes.io/managed-by"
MANAGED_BY_ARGO_VALUE="argocd"

MANAGED_NAMESPACES=($(kubectl get ns -l "$MANAGED_BY_LABEL_KEY"="$MANAGED_BY_ARGO_VALUE" -o custom-columns=":metadata.name" --no-headers))
ACTIVE_APPLICATIONS=($(kubectl get applications.argoproj.io -n argocd -o custom-columns=":metadata.name" --no-headers))

INACTIVE_NAMESPACES=()

for namespace in "${MANAGED_NAMESPACES[@]}"; do
    FOUND=false
    for application in "${ACTIVE_APPLICATIONS[@]}"; do
        if [ "$application" == "$namespace" ]; then
            FOUND=true
            break
        fi
    done

    if [ $FOUND == false ]; then
        INACTIVE_NAMESPACES+=("$namespace")
    fi
done

INACTIVE_NAMESPACES_STRING=$(printf "%s\n" "${INACTIVE_NAMESPACES[@]}")

read -p "Are you sure you want to remove the following namespaces for context $CONTEXT:

$INACTIVE_NAMESPACES_STRING

Press Y or y to continue " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    for namespace in "${INACTIVE_NAMESPACES[@]}"; do
        kubectl delete ns "$namespace"
    done

    echo "Namespaces deleted, exiting"

    exit 0
fi

echo "Exiting without deleting namespaces"
exit 0
