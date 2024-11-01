#!/bin/bash

# Function to display usage
usage() {
    echo "Usage: $0 [-s storage_type]"
    echo "Options:"
    echo "  -s storage_type    Specify storage type (postgres or qdrant, default: postgres)"
    exit 1
}

# Default storage type
STORAGE_TYPE="postgres"

# Parse command line options
while getopts "s:h" opt; do
    case $opt in
        s)
            STORAGE_TYPE="$OPTARG"
            ;;
        h)
            usage
            ;;
        \?)
            usage
            ;;
    esac
done

# Validate storage type
if [ "$STORAGE_TYPE" != "postgres" ] && [ "$STORAGE_TYPE" != "qdrant" ]; then
    echo "Error: Invalid storage type. Must be either 'postgres' or 'qdrant'"
    usage
fi

# Stop any running containers
docker-compose down

# Start the appropriate compose file
if [ "$STORAGE_TYPE" = "qdrant" ]; then
    echo "Starting OpenExcept with Qdrant storage..."
    docker-compose -f docker-compose.qdrant.yml -f Dockerfile.qdrant up --build
else
    echo "Starting OpenExcept with PostgreSQL storage..."
    docker-compose up --build
fi
