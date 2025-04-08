#!/bin/bash

# Export Docker images for sharing with colleagues

# Ensure the script exits if any command fails
set -e

# Define the output directory
OUTPUT_DIR="./docker-exports"
mkdir -p $OUTPUT_DIR

echo "Exporting Docker images for sharing..."

# Build the images first
echo "Building production images..."
docker-compose -f docker-compose.prod.yml build

# Export the frontend image
echo "Exporting frontend image..."
docker save climate_economy_ecosystem_frontend | gzip > $OUTPUT_DIR/frontend.tar.gz

# Export the Python image
echo "Exporting Python image..."
docker save climate_economy_ecosystem_python | gzip > $OUTPUT_DIR/python.tar.gz

# Export the Redis image
echo "Exporting Redis image..."
docker save redis:alpine | gzip > $OUTPUT_DIR/redis.tar.gz

# Export the Supabase image
echo "Exporting Supabase image..."
docker save supabase/supabase-local:latest | gzip > $OUTPUT_DIR/supabase.tar.gz

echo "All images exported successfully to $OUTPUT_DIR"
echo ""
echo "To share with colleagues:"
echo "1. Send them the exported image files"
echo "2. They should run: docker load < frontend.tar.gz"
echo "3. They should run: docker load < python.tar.gz"
echo "4. They should run: docker load < redis.tar.gz"
echo "5. They should run: docker load < supabase.tar.gz"
echo "6. They can then start the application with: npm run docker:prod:up"
