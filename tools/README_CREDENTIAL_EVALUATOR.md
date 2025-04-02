# International Credential Evaluator

## Overview

The International Credential Evaluator is a specialized tool designed to help international professionals entering the Massachusetts clean energy workforce. It evaluates foreign credentials and maps them to US equivalents, provides guidance on credential recognition, and recommends additional training or certifications to enhance employability in the clean energy sector.

## Features

- **Credential Evaluation**: Maps international credentials to US equivalents
- **Field-Specific Analysis**: Provides field-specific recommendations for clean energy careers
- **Massachusetts-Specific Guidance**: Includes information on licensing requirements and credential acceptance in Massachusetts
- **Hybrid Approach**: Combines a database of known credential equivalencies with AI-powered evaluation for unknown credentials
- **Resource Recommendations**: Offers suggestions for credential evaluation services and next steps

## Components

### 1. Core Credential Evaluator Tool

- **File**: `credential_evaluator.py`
- **Function**: Evaluates international credentials and returns detailed analysis
- **Usage**: `python credential_evaluator.py "Nigeria" "Bachelor of Engineering" "Electrical Engineering"`

### 2. Database Tables

The system utilizes several database tables:

- **credential_evaluations**: Stores evaluation results for user credentials
- **education_equivalencies**: Reference data for common credential mappings
- **credential_services**: Information about credential evaluation services
- **clean_energy_credential_notes**: Field-specific notes for clean energy relevance

### 3. Integration with User Assessment

The credential evaluator is integrated with the user assessment process in `pages/api/profile/assessment.js`, which:

1. Captures international credentials during user onboarding
2. Processes credentials through the evaluator
3. Stores results in the user's profile
4. Provides personalized recommendations based on evaluation

### 4. Specialized Prompts

The `prompts/international_prompts.py` file contains specialized prompts for:

- Credential equivalency assessment
- Career pathway planning
- Education recommendation
- Resume adaptation
- Interview preparation
- Cultural integration guidance

## Technical Implementation

### Evaluation Process

The credential evaluation follows this sequence:

1. Check if the credential exists in the `CREDENTIAL_EQUIVALENCY_MAP` database
2. If not found, check the country's education system mapping in `EDUCATION_SYSTEMS`
3. If still not found, use AI-powered evaluation via OpenAI
4. Format results with Massachusetts-specific information and clean energy relevance
5. Store in database and update user profile

### Database Schema

The credential evaluation system extends the Supabase database with migration `004_credential_evaluation.sql`, which:

- Creates tables for storing evaluation data
- Adds indexes for efficient querying
- Implements a trigger to keep user profiles in sync with evaluations
- Adds support for international credential acceptance in job listings

### API Integration

The credential evaluator is integrated with:

- User assessment API
- Job matching algorithm
- Career recommendations
- Education pathway suggestions

## Usage Examples

### Command-line Usage

```bash
python credential_evaluator.py "India" "Bachelor of Technology" "Electrical Engineering"
```

### Programmatic Usage

```python
from credential_evaluator import evaluate_credentials

result = evaluate_credentials(
    country="Nigeria",
    credential="Higher National Diploma",
    field="Mechanical Engineering"
)

print(f"US Equivalent: {result['us_equivalent']}")
print(f"Clean Energy Relevance: {result['massachusetts_specific']['clean_energy_relevance']}")
```

### API Response Example

```json
{
  "country": "India",
  "original_credential": "Bachelor of Technology",
  "field": "Electrical Engineering",
  "us_equivalent": "Bachelor of Science in Engineering",
  "evaluation_notes": "Your Electrical Engineering background is most similar to Electrical Engineering, Power Systems Engineering in the US system.",
  "recommended_actions": [
    "Get credential evaluated by a NACES-member organization",
    "Check Massachusetts professional licensing requirements"
  ],
  "confidence": 90,
  "additional_training_needed": [
    "NABCEP (North American Board of Certified Energy Practitioners) certification",
    "BPI (Building Performance Institute) certification",
    "LEED (Leadership in Energy and Environmental Design) certification"
  ],
  "massachusetts_specific": {
    "licensing_required": true,
    "acceptance_level": "High",
    "clean_energy_relevance": "High"
  },
  "resources": [
    {
      "name": "World Education Services (WES)",
      "url": "https://www.wes.org/",
      "description": "NACES-member credential evaluation service"
    },
    {
      "name": "Massachusetts Clean Energy Center",
      "url": "https://www.masscec.com/",
      "description": "Clean energy industry support and workforce development"
    }
  ]
}
```

## Maintenance and Expansion

### Adding New Countries/Credentials

To add support for new countries or credentials:

1. Update the `CREDENTIAL_EQUIVALENCY_MAP` dictionary in `credential_evaluator.py`
2. Add new entries to the `EDUCATION_SYSTEMS` dictionary for broader coverage
3. Insert new rows into the `education_equivalencies` table for database persistence

### Improving AI Evaluation

The AI-based evaluation can be improved by:

1. Providing more examples in the system prompt
2. Adding more field-specific information for clean energy relevance
3. Implementing a feedback loop to learn from corrections

## Technical Requirements

- Python 3.8+
- OpenAI API access
- Supabase database
- Required Python packages:
  - openai
  - dotenv
  - typing
  - logging 