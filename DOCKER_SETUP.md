# Climate Economy Ecosystem - Docker Setup Guide

This guide explains how to run the Climate Economy Ecosystem application using Docker, making it easy to set up and share with colleagues.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- Git

No other dependencies are required as everything runs inside Docker containers.

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/climate-economy-ecosystem.git
   cd climate-economy-ecosystem
   ```

2. Create a `.env` file with your configuration:
   ```bash
   cp .env.example .env
   ```

3. Generate secure keys for local development:
   ```bash
   npm run generate-keys
   ```

   This script will generate secure random keys for JWT tokens and other secrets, and update your `.env` file with these values.

4. Edit the `.env` file to add any additional API keys if needed. For local development, the default values should work.

5. Start the application in production mode:
   ```bash
   npm run docker:prod
   ```

4. Access the application at [http://localhost:3000](http://localhost:3000)

## Available Docker Commands

### Production Environment

- **Start production environment**: `npm run docker:prod`
- **Build production containers**: `npm run docker:prod:build`
- **Start production containers**: `npm run docker:prod:up`
- **Stop production containers**: `npm run docker:prod:down`

### Development Environment

- **Start development environment**: `npm run docker:dev`
- **Build development containers**: `npm run docker:build`
- **Start development containers**: `npm run docker:up`
- **Stop development containers**: `npm run docker:down`
- **Run frontend only**: `npm run docker:dev:frontend`
- **Run Python backend only**: `npm run docker:dev:python`

### Testing

- **Run all tests**: `npm run docker:test`
- **Run frontend tests only**: `npm run docker:test:frontend`
- **Run Python tests only**: `npm run docker:test:python`

### Database

- **Run migrations**: `npm run docker:migrate`

## Architecture

The application is composed of several Docker containers:

1. **Frontend**: Next.js application serving the user interface
2. **Python**: Python backend for LangGraph and LangChain components
3. **Redis**: Caching and temporary storage
4. **Supabase**: Database and authentication

## Accessing Container Logs

To view logs from all containers:
```bash
docker-compose -f docker-compose.prod.yml logs -f
```

To view logs from a specific container:
```bash
docker-compose -f docker-compose.prod.yml logs -f frontend
```

## Troubleshooting

### Container Health Checks

The production environment includes health checks for all containers. To check the status:
```bash
docker-compose -f docker-compose.prod.yml ps
```

### Common Issues

1. **Port conflicts**: If port 3000 is already in use, you can change it in the docker-compose.prod.yml file.

2. **Database connection issues**: Check that Supabase is running correctly:
   ```bash
   docker-compose -f docker-compose.prod.yml logs supabase
   ```

3. **Python dependencies**: If you encounter issues with Python dependencies, you can rebuild the Python container:
   ```bash
   docker-compose -f docker-compose.prod.yml build python
   ```

## Customizing the Environment

To customize the environment variables, edit the `.env` file. The most important variables are:

- `OPENAI_API_KEY`: Your OpenAI API key
- `NEXT_PUBLIC_SUPABASE_URL`: Supabase URL (default works for local development)
- `SUPABASE_SERVICE_KEY`: Supabase service key (default works for local development)
- `NEXTAUTH_SECRET`: Secret for NextAuth (default works for local development)

## Sharing with Colleagues

There are two ways to share this application with colleagues:

### Option 1: Share the Repository

1. Make sure they have Docker and Docker Compose installed
2. Share the repository with them (via Git or as a zip file)
3. Ask them to follow the Quick Start guide above

They don't need to install Node.js, Python, or any other dependencies as everything runs inside Docker containers.

### Option 2: Share Pre-built Docker Images

This option is faster as colleagues won't need to build the images themselves:

1. Export the Docker images:
   ```bash
   npm run docker:export
   ```

2. Share the exported image files from the `docker-exports` directory with your colleagues

3. Colleagues should load the images:
   ```bash
   # Load the frontend image
   docker load < frontend.tar.gz

   # Load the Python image
   docker load < python.tar.gz

   # Load the Redis image
   docker load < redis.tar.gz

   # Load the Supabase image
   docker load < supabase.tar.gz
   ```

4. Share the repository code (without node_modules and other build artifacts)

5. Colleagues can start the application:
   ```bash
   npm run docker:prod:up
   ```

This approach is faster for colleagues as they don't need to build the images, which can take time especially for the Python dependencies.

## Security Considerations

### Environment Variables and Secrets

When sharing the application with colleagues, be careful with sensitive information:

1. **Never share your `.env` file directly**
   - Each developer should create their own `.env` file using the `.env.example` template
   - They should run `npm run generate-keys` to create their own secure keys

2. **Use different secrets for shared environments**
   - Development, staging, and production environments should use different secrets
   - Store production secrets in a secure vault or secret management system

3. **Docker security**
   - When exporting Docker images, ensure they don't contain sensitive information
   - The `.env` file is mounted as a volume and not baked into the image
   - Review Docker images for security vulnerabilities before sharing
