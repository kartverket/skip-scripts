#!/bin/bash

# File to store the resources
resources_file="tmp-resources.txt"

# Run kubectl api-resources and write results to a file
kubectl api-resources --verbs=list -o name > "$resources_file"

echo "Resources file '$resources_file' generated with the list of Kubernetes resources."
