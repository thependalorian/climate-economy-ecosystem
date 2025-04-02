# RLHF Workflow Diagrams

This document provides visual representations of the RLHF system workflow.

## Feedback Collection Flow

```mermaid
sequenceDiagram
    participant User
    participant UI as Chat Interface
    participant API as Feedback API
    participant DB as Supabase Database
    participant Metrics as Metrics Service

    User->>UI: Interacts with AI response
    UI->>UI: Displays feedback UI components
    User->>UI: Provides feedback (thumbs up/down, rating)
    UI->>API: POST /api/assistant/feedback
    API->>DB: Store feedback data
    API->>Metrics: Track feedback event
    API->>DB: Update user satisfaction score
    API-->>UI: Confirmation response
    UI-->>User: Display feedback confirmation
```

## Training Pipeline Flow

```mermaid
flowchart TD
    A[Collect User Feedback] --> B[Store in Supabase]
    B --> C[Process Feedback Data]
    C --> D{Training Type}
    D -->|Reward Model| E[Train Reward Model]
    D -->|PPO| F[Fine-tune Using PPO]
    E --> G[Evaluate Reward Model]
    F --> H[Evaluate Policy Model]
    G --> I[Deploy Reward Model]
    H --> J[Deploy Policy Model]
    I --> K[Monitor Performance]
    J --> K
    K --> L{Performance Improved?}
    L -->|Yes| M[Continue Using Model]
    L -->|No| N[Rollback to Previous Model]
    M --> A
    N --> A
```

## Data Flow

```mermaid
flowchart LR
    A[User Feedback] --> B[Raw Feedback Data]
    B --> C[Feedback Processor]
    C --> D[Preprocessed Data]
    D --> E[Train/Test Split]
    E --> F1[Reward Model Training]
    E --> F2[PPO Training]
    F1 --> G1[Trained Reward Model]
    F2 --> G2[Fine-tuned Policy Model]
    G1 --> H[Model Registry]
    G2 --> H
    H --> I[Deployment]
    I --> J[Inference API]
    J --> K[New User Interactions]
    K --> A
```

## Component Architecture

```mermaid
graph TD
    subgraph Frontend
        A[Chat Component] --> B[StreamingResponse]
        B --> C[StepFeedback]
        B --> D[MessageFeedback]
        C --> E[Feedback Actions]
        D --> E
    end

    subgraph Backend
        F[Feedback API] --> G[Auth Middleware]
        G --> H[Feedback Controller]
        H --> I[Database Service]
        H --> J[Metrics Service]
    end

    subgraph ML
        K[Feedback Processor] --> L[Data Pipeline]
        L --> M[Reward Model]
        L --> N[PPO Trainer]
        M --> O[Model Registry]
        N --> O
    end

    subgraph Automation
        P[GitHub Workflow] --> Q[Training Script]
        Q --> R[Model Evaluation]
        R --> S[Model Deployment]
    end

    E -->|API Call| F
    J -->|Data| K
    S -->|New Model| A
```

## Continuous Improvement Cycle

```mermaid
graph TD
    A[Collect User Feedback] --> B[Analyze Feedback]
    B --> C[Identify Improvement Areas]
    C --> D[Train Models]
    D --> E[Deploy Models]
    E --> F[Monitor Performance]
    F --> A
``` 