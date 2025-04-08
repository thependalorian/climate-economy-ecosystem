#!/bin/bash

# Run Python tests in Docker

# Ensure the script exits if any command fails
set -e

echo "Running Python tests in Docker..."

# Run the test container
docker-compose run --rm test-python

echo "Python tests completed!"
