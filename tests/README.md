# Climate Economy Ecosystem Test Scripts

This directory contains test scripts for the Climate Economy Ecosystem.

## Overview

The test scripts are designed to test the following components:

1. **RLHF System**: Tests the Reinforcement Learning from Human Feedback system
2. **Memory Service**: Tests the Memory Service for storing and retrieving memories
3. **Agent**: Tests the agent's responses and tool use

## Test Scripts

### 1. RLHF Test

The `test_rlhf.py` script tests the RLHF system by creating mock feedback data, processing it, and training a reward model.

```bash
python test_rlhf.py
```

### 2. Memory Service Test

The `test_memory_service.py` script tests the Memory Service by creating and retrieving memories, storing and retrieving user profiles, testing EJ community detection, and simulating resume analysis.

```bash
python test_memory_service.py
```

### 3. Agent Test

The `test_agent.py` script tests the agent's responses and tool use by simulating user queries, processing the agent's responses, collecting feedback, and testing different user personas.

```bash
python test_agent.py
```

## Running the Tests

To run all tests, execute the following commands:

```bash
python test_rlhf.py
python test_memory_service.py
python test_agent.py
```

## Test Data

The tests use mock data to simulate user interactions. The mock data includes:

- **User Personas**: Veteran, EJ community member, international professional
- **Queries**: Clean energy job opportunities, training programs, etc.
- **Feedback**: Ratings and comments on agent responses

## Dependencies

The tests require the following dependencies:

```bash
pip install torch transformers datasets trl
```

## Configuration

The tests use the following environment variables:

- `OPENAI_API_KEY`: OpenAI API key for agent simulation
- `SUPABASE_URL`: Supabase URL for database operations
- `SUPABASE_SERVICE_KEY`: Supabase service key for database operations

These can be set in a `.env` file in the project root.

## Logging

The tests include detailed logging to help with debugging. Check the log files for more information:

- `rlhf_training.log`: Logs from the RLHF training process
- `memory_service.log`: Logs from the Memory Service
- `agent_test.log`: Logs from the agent test
