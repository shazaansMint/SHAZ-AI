# SHAZ Architecture

## Vision

SHAZ is a personal AI operating system designed to become Shaz's always-available AI companion, coder, website builder, co-founder, assistant, and digital operator.

SHAZ should feel like one natural AI.

Internally, SHAZ may use multiple models, tools, skills, and services.

## Core Principles

1. SHAZ is personal.
2. SHAZ should communicate naturally.
3. SHAZ should understand intent before acting.
4. SHAZ should use the correct skill for the task.
5. SHAZ should remember important context.
6. SHAZ should ask for permission before dangerous or irreversible actions.
7. SHAZ should verify its own work where possible.
8. SHAZ should be modular and continuously expandable.
9. SHAZ should be local-first where practical.
10. SHAZ should feel like one AI even when multiple internal systems are used.

## Core System

SHAZ Core is responsible for:

- Understanding user intent
- Loading SHAZ identity
- Selecting skills
- Selecting models
- Managing task execution
- Managing permissions
- Recording activity
- Accessing memory

## Capability Worlds

### Coding

- Write code
- Read repositories
- Fix bugs
- Refactor code
- Run tests
- Work with Git

### Website Building

- Plan websites
- Build websites
- Review designs
- Test websites
- Prepare deployments

### Business / Co-Founder

- Business brainstorming
- Strategic planning
- Honest feedback
- Market research
- Project planning

### Research

- Research topics
- Compare information
- Summarize information
- Analyze findings

### Personal Assistant

- Calendar
- Reminders
- Tasks
- Notes
- Daily planning

### Calculator / Finance

- Calculations
- Budgeting
- Expense tracking
- Financial analysis

### Health

- General health information
- Health-related research
- Health tracking support

SHAZ must not pretend to be a medical professional.

### Entertainment

- Movies
- Music
- Games
- Recommendations

## Project Worlds

SHAZ should understand separate project contexts.

Initial project worlds:

- Eternelle
- SHAZ AI
- Client Projects
- Personal
- Sandbox

Each project world may have:

- Its own memory
- Its own goals
- Its own files
- Its own tools
- Its own activity

## Memory

SHAZ will eventually use a long-term memory system.

Odysseus is planned as part of the SHAZ memory architecture.

Memory should distinguish between:

- User memories
- Project memories
- Decisions
- Preferences
- Activity
- Conversation context

## Skills

Skills are modular capabilities.

A skill should:

1. Receive a task
2. Validate the task
3. Perform its function
4. Return a result
5. Report activity to SHAZ Core

## Permissions

SHAZ permissions will use levels.

### Safe

Reading and explaining.

### Approval Required

Editing files, sending messages, and deploying.

### High Risk

Deleting data, deleting files, financial actions, and irreversible actions.

## Task Planning

SHAZ should convert complex requests into tasks.

Example:

"Build me a website."

Possible plan:

1. Understand the website goal
2. Identify the project world
3. Create a project plan
4. Build the website
5. Test the website
6. Review the result
7. Ask for approval before deployment

## Self-Criticism

SHAZ should eventually review its own work.

A task may pass through:

1. Planning
2. Execution
3. Verification
4. Criticism
5. Improvement

## Future Integrations

Planned integrations include:

- GitHub
- Vercel
- Supabase
- Shopify
- Notion
- Gmail

More integrations will be added over time.

## Models

Initial model:

- Qwen3 8B

Future specialist models may include:

- Coding model
- Reasoning model
- Vision model
- Embedding model

The user should interact with SHAZ, not manually choose models.

## Long-Term Vision

SHAZ should become a personal AI operating system that can understand Shaz, remember important context, work across projects, use tools, build software, assist with life and business, and naturally grow over time.
