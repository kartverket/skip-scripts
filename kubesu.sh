#!/bin/bash

kubesu() {
    # Ensure fzf is installed
    if ! command -v fzf >/dev/null 2>&1; then
        echo "fzf is not installed. Please install it first. https://github.com/junegunn/fzf"
        return 1
    fi

    # Get a list of accounts
    accounts=$(gcloud auth list --format="value(account)")

    # Use fzf to let the user select an account
    ACCOUNT=$(echo "$accounts" | fzf --height 40% --header "Select GCP Account")

    if [ -n "$ACCOUNT" ]; then
        # User made a selection. Set the active account.
        gcloud config set account "$ACCOUNT"
        # Delete the GKE gcloud auth plugin cache to force a refresh of the access token
        rm -f ~/.kube/gke_gcloud_auth_plugin_cache
        echo "Switched to $ACCOUNT and cleared GKE auth cache."
    else
        echo "No selection made."
    fi
}
