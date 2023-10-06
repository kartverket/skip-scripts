#!/bin/bash

# File containing the list of resources
resources_file="tmp_resources.txt"

# Function to handle kubectl get for a specific kind
function get_kind_resources {
    local kind=$1
    local output
    output=$(kubectl get --show-kind --ignore-not-found --selector=app.kubernetes.io/managed-by=configmanagement.gke.io $kind 2>&1)
    local error_too_many_requests="the server has received too many requests"

    if [[ $output == *"$error_too_many_requests"* ]]; then
        echo "Retrying in 5 seconds for kind: $kind"
        sleep 5
        get_kind_resources $kind
    elif [ -n "$output" ]; then
        echo "$output" >> tmp-acm-resources.txt
    fi
}

# Iterate over the resources in the file
while IFS= read -r kind; do
    echo "Getting resources for kind: $kind"
    while true; do
        # Run kubectl get for the current kind
        get_kind_resources $kind
        if [ $? -eq 0 ]; then
            break
        fi
    done
done < "$resources_file"

echo "Resources retrieved and saved to 'tmp-acm-resources.txt'."

# Clean up resources file if needed
# rm "$resources_file"
