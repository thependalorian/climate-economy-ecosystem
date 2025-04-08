#!/bin/bash

# Run frontend tests in Docker

# Ensure the script exits if any command fails
set -e

echo "Running frontend tests in Docker..."

# Run the test container
docker-compose run --rm test-frontend

echo "Frontend tests completed!"
