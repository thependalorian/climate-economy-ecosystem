#!/bin/bash

# Run database migrations in Docker

# Ensure the script exits if any command fails
set -e

echo "Running database migrations in Docker..."

# Run the migrations using the frontend container
docker-compose run --rm frontend node scripts/run-migrations.js

echo "Migrations completed successfully!"
