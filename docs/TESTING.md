# Testing the Climate Economy Ecosystem

This document provides an overview of the test scripts created to test the Climate Economy Ecosystem's backend components.

## 1. RLHF Testing

The `test_rlhf.py` script tests the Reinforcement Learning from Human Feedback (RLHF) system by:

1. Creating mock feedback data
2. Processing the feedback
3. Training a simple reward model
4. Using the reward model to score responses

### Running the RLHF Test

```bash
python test_rlhf.py
```

### Key Components Tested

- **FeedbackProcessor**: Tests the ability to process feedback data from the database
- **ClimateRewardModel**: Tests the reward model's ability to learn from feedback and score responses
- **Reward Model Training**: Tests the end-to-end training process

## 2. Memory Service Testing

The `test_memory_service.py` script tests the Memory Service by:

1. Creating and retrieving memories
2. Storing and retrieving user profiles
3. Testing EJ community detection
4. Simulating resume analysis

### Running the Memory Service Test

```bash
python test_memory_service.py
```

### Key Components Tested

- **Memory Operations**: Tests basic memory operations like adding, retrieving, and searching memories
- **User Profile Operations**: Tests storing and retrieving user profiles
- **EJ Community Detection**: Tests the ability to identify Environmental Justice communities
- **Resume Analysis**: Tests the ability to analyze resumes and extract skills

## 3. Agent Testing

The `test_agent.py` script tests the agent's responses and tool use by:

1. Simulating user queries
2. Processing the agent's responses
3. Collecting feedback
4. Testing different user personas (veteran, EJ community member, international professional)

### Running the Agent Test

```bash
python test_agent.py
```

### Key Components Tested

- **Veteran Persona**: Tests the agent's ability to provide relevant information for veterans
- **EJ Community Persona**: Tests the agent's ability to provide relevant information for residents of Environmental Justice communities
- **International Persona**: Tests the agent's ability to provide relevant information for international professionals
- **Military Skill Translation**: Tests the integration with the military skill translator
- **Feedback Collection**: Tests the feedback collection process

## 4. Integration Testing

To test the full integration of all components, run all three test scripts:

```bash
python test_rlhf.py
python test_memory_service.py
python test_agent.py
```

## 5. Troubleshooting

### Common Issues

1. **Missing Dependencies**: Make sure all required packages are installed:
   ```bash
   pip install torch transformers datasets trl
   ```

2. **Database Connection Issues**: If you encounter database connection issues, check your Supabase credentials in the `.env` file.

3. **Memory Service Issues**: If the Memory Service fails, it will fall back to the mock implementation. Check the logs for warnings.

4. **OpenAI API Issues**: If you encounter OpenAI API issues, check your API key in the `.env` file.

### Debugging

- All test scripts include detailed logging to help with debugging
- Check the log files for more information:
  - `rlhf_training.log`: Logs from the RLHF training process
  - `memory_service.log`: Logs from the Memory Service
  - `agent_test.log`: Logs from the agent test

## 6. Next Steps

After running the tests, you can:

1. **Analyze the Results**: Check the test output to see how well the components are working
2. **Improve the Models**: Use the feedback collected to improve the RLHF models
3. **Enhance the Agent**: Use the test results to enhance the agent's responses
4. **Add More Tests**: Add more test cases to cover additional scenarios
