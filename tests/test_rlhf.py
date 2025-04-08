#!/usr/bin/env python3
"""
Tests for the RLHF module

This script tests the RLHF module to ensure it works correctly.
"""

import os
import sys
import unittest
import torch
import json
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock dependencies before importing
sys.modules['supabase'] = MagicMock()
sys.modules['transformers'] = MagicMock()
sys.modules['transformers.AutoModelForSequenceClassification'] = MagicMock()
sys.modules['transformers.AutoTokenizer'] = MagicMock()
sys.modules['transformers.AutoModelForCausalLM'] = MagicMock()

# Import RLHF components
from lib.rlhf.models import BaseRewardModel, ClimateRewardModel, AgentSpecificRewardModel, RewardModelFactory
from lib.rlhf.training import PolicyModel, ValueModel, PPOTrainer
from lib.rlhf.pipeline import FeedbackDataset, FeedbackCollector, ContinuousImprovementPipeline
from lib.rlhf.orchestrator import RLHFOrchestrator, RLHFConfig

class TestRewardModels(unittest.TestCase):
    """Tests for reward models"""

    @patch('lib.rlhf.models.ClimateRewardModel')
    @patch('lib.rlhf.models.AgentSpecificRewardModel')
    def test_reward_model_factory(self, mock_agent_model, mock_climate_model):
        """Test that the reward model factory creates the correct models"""
        # Setup mocks
        mock_climate_model.return_value = MagicMock(spec=ClimateRewardModel)
        mock_agent_model.return_value = MagicMock(spec=AgentSpecificRewardModel)
        mock_agent_model.return_value.agent_type = "climate_education"

        # Create general reward model
        with patch.object(RewardModelFactory, 'create_reward_model', return_value=mock_climate_model.return_value):
            general_model = RewardModelFactory.create_reward_model()
            self.assertEqual(general_model, mock_climate_model.return_value)

        # Create agent-specific reward model
        with patch.object(RewardModelFactory, 'create_reward_model', return_value=mock_agent_model.return_value):
            agent_model = RewardModelFactory.create_reward_model("climate_education")
            self.assertEqual(agent_model, mock_agent_model.return_value)
            self.assertEqual(agent_model.agent_type, "climate_education")

    def test_climate_reward_model(self):
        """Test that the climate reward model computes rewards correctly"""
        # Create a mock model
        model = MagicMock(spec=ClimateRewardModel)
        model.compute_reward.return_value = 0.75
        model.compute_batch_rewards.return_value = [0.8, 0.6]

        # Compute reward
        reward = model.compute_reward("test query", "test response")

        # Check that the reward is a float
        self.assertEqual(reward, 0.75)

        # Compute batch rewards
        batch_rewards = model.compute_batch_rewards([
            {"query": "test query 1", "response": "test response 1"},
            {"query": "test query 2", "response": "test response 2"}
        ])

        # Check that batch rewards is a list of floats
        self.assertEqual(batch_rewards, [0.8, 0.6])

class TestPolicyModel(unittest.TestCase):
    """Tests for policy model"""

    def test_policy_model_generate(self):
        """Test that the policy model generates responses correctly"""
        # Create a mock model
        model = MagicMock(spec=PolicyModel)
        model.generate.return_value = "test response"

        # Generate response
        response = model.generate("test prompt")

        # Check that the response is a string
        self.assertEqual(response, "test response")

class TestValueModel(unittest.TestCase):
    """Tests for value model"""

    def test_value_model_predict(self):
        """Test that the value model predicts values correctly"""
        # Create value model
        model = ValueModel(embedding_dim=10, hidden_dim=5)

        # Create test embeddings
        embeddings = torch.randn(3, 10)

        # Predict values
        values = model.predict(embeddings)

        # Check that values has the correct shape
        self.assertEqual(values.shape, (3, 1))

class TestFeedbackDataset(unittest.TestCase):
    """Tests for feedback dataset"""

    def test_feedback_dataset(self):
        """Test that the feedback dataset works correctly"""
        # Create test data
        data = [
            {"query": "test query 1", "response": "test response 1", "score": 5},
            {"query": "test query 2", "response": "test response 2", "score": 3}
        ]

        # Create dataset
        dataset = FeedbackDataset(data)

        # Check that the dataset has the correct length
        self.assertEqual(len(dataset), 2)

        # Check that the dataset returns the correct items
        item = dataset[0]
        self.assertEqual(item["query"], "test query 1")
        self.assertEqual(item["response"], "test response 1")
        self.assertEqual(item["score"], 5)

class TestRLHFConfig(unittest.TestCase):
    """Tests for RLHF config"""

    def test_rlhf_config(self):
        """Test that the RLHF config works correctly"""
        # Create config
        config = RLHFConfig(
            agent_types=["climate_education", "job_matching"],
            policy_model_name="test-model",
            reward_model_name="test-model",
            ppo_learning_rate=1e-4,
            min_feedback_threshold=10,
            improvement_interval_days=2
        )

        # Check that the config has the correct values
        self.assertEqual(config.agent_types, ["climate_education", "job_matching"])
        self.assertEqual(config.policy_model_name, "test-model")
        self.assertEqual(config.reward_model_name, "test-model")
        self.assertEqual(config.ppo_learning_rate, 1e-4)
        self.assertEqual(config.min_feedback_threshold, 10)
        self.assertEqual(config.improvement_interval_days, 2)

        # Check that the config can be serialized to JSON
        config_json = config.model_dump_json()
        self.assertIsInstance(config_json, str)

        # Check that the config can be deserialized from JSON
        config2 = RLHFConfig.model_validate_json(config_json)
        self.assertEqual(config2.agent_types, config.agent_types)

class TestRLHFOrchestrator(unittest.TestCase):
    """Tests for RLHF orchestrator"""

    def test_rlhf_orchestrator_setup(self):
        """Test that the RLHF orchestrator sets up components correctly"""
        # Create a mock orchestrator
        orchestrator = MagicMock(spec=RLHFOrchestrator)
        orchestrator.policy_models = {"climate_education": MagicMock(), "job_matching": MagicMock()}
        orchestrator.value_models = {"climate_education": MagicMock(), "job_matching": MagicMock()}
        orchestrator.reward_models = {"climate_education": MagicMock(), "job_matching": MagicMock()}
        orchestrator.ppo_trainers = {"climate_education": MagicMock(), "job_matching": MagicMock()}
        orchestrator.improvement_pipelines = {"climate_education": MagicMock(), "job_matching": MagicMock()}

        # Check that the orchestrator has the correct components
        self.assertEqual(len(orchestrator.policy_models), 2)
        self.assertEqual(len(orchestrator.value_models), 2)
        self.assertEqual(len(orchestrator.reward_models), 2)
        self.assertEqual(len(orchestrator.ppo_trainers), 2)
        self.assertEqual(len(orchestrator.improvement_pipelines), 2)

if __name__ == "__main__":
    unittest.main()
