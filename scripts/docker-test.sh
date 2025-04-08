#!/bin/bash

# Run tests in Docker

# Ensure the script exits if any command fails
set -e

echo "Running tests in Docker..."

# Run the test container
docker-compose run --rm test

echo "Tests completed!"
