# Use Node.js LTS as the base image
FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
WORKDIR /app

# Install Python and pip for the Python components
RUN apk add --no-cache python3 py3-pip

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci

# Install Python dependencies in a virtual environment
COPY requirements.txt ./
RUN python3 -m venv /app/venv \
    && . /app/venv/bin/activate \
    && pip3 install --upgrade pip \
    && pip3 install --no-cache-dir -r requirements.txt

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build the Next.js application
RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production

# Create a non-root user to run the application
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy necessary files from the builder stage
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/climate_economy_ecosystem ./climate_economy_ecosystem
COPY --from=deps /app/node_modules ./node_modules

# Copy Python virtual environment
COPY --from=deps /app/venv /app/venv
COPY --from=deps /usr/bin/python3 /usr/bin/python3
COPY --from=deps /usr/lib/python3.* /usr/lib/
COPY --from=deps /usr/lib/libpython3.* /usr/lib/

# Set up environment variables for Python
ENV PATH="/app/venv/bin:$PATH"
ENV PYTHONPATH="/app"

# Set the correct permissions
RUN chown -R nextjs:nodejs /app

# Switch to the non-root user
USER nextjs

# Expose the port the app runs on
EXPOSE 3000

# Set the command to run the application
CMD ["node", "server.js"]
