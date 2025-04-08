#!/bin/bash

# Run the production environment in Docker

# Ensure the script exits if any command fails
set -e

echo "Starting production environment in Docker..."

# Build the production containers
docker-compose -f docker-compose.prod.yml build

# Start the production containers
docker-compose -f docker-compose.prod.yml up -d

echo "Production environment started successfully!"
echo "The application is now running at http://localhost:3000"
echo ""
echo "To check the status of the containers, run:"
echo "  docker-compose -f docker-compose.prod.yml ps"
echo ""
echo "To view logs, run:"
echo "  docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "To stop the production environment, run:"
echo "  docker-compose -f docker-compose.prod.yml down"
