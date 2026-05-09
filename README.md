# Autonomous Code Review Agent

An autonomous multi-agent system that reviews code for bugs, security vulnerabilities, style issues, and performance problems, along with providing solutions and code fixes for users to learn and implement, powered by OpenAI GPT-4o and LangGraph.

## Live Demo
[autonomous-code-review-agent.vercel.app](https://autonomous-code-review-agent.vercel.app)

## How It Works

Code is passed through 4 specialized AI agents, which are bug, security, style, and performance agents that run in parallel, each focused on a specific domain of concern. A synthesizer agent then combines all findings into a structured report, followed by an auto-fix agent that rewrites the code with all fixes applied.

```mermaid
graph TD
    A[Code Input\nPaste Code or GitHub URL] --> B[GitHub Integration\nFetch code from repo or PR]
    B --> C[LangGraph Orchestrator]
    A --> C

    C --> D[Bug Detector Agent]
    C --> E[Security Scanner Agent]
    C --> F[Style Checker Agent]
    C --> G[Performance Agent]

    D --> H[Synthesizer Agent\nCombines all findings]
    E --> H
    F --> H
    G --> H

    H --> I[Auto-Fix Agent\nRewrites code with fixes]

    I --> J[Final Report + Fixed Code]

    style A fill:#1a1a1a,color:#ffffff,stroke:#555
    style C fill:#1a1a1a,color:#ffffff,stroke:#555
    style H fill:#1a1a1a,color:#ffffff,stroke:#555
    style I fill:#1a1a1a,color:#ffffff,stroke:#555
    style J fill:#2d5a27,color:#ffffff,stroke:#555
    style D fill:#1a3a5c,color:#ffffff,stroke:#555
    style E fill:#1a3a5c,color:#ffffff,stroke:#555
    style F fill:#1a3a5c,color:#ffffff,stroke:#555
    style G fill:#1a3a5c,color:#ffffff,stroke:#555
    style B fill:#3a2a1a,color:#ffffff,stroke:#555
```