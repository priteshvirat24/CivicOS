# CivicOS

**Static dashboards are dead. This dataset maintains itself.**

CivicOS is a living civic dataset for India, managed entirely by a swarm of autonomous agents. Instead of manual data entry or fragile, single-point-of-failure scraping scripts, CivicOS utilizes a resilient, multi-agent architecture to keep public government and civic data sources continuously up-to-date, verified, and canonicalized.

## Why Multi-Agent Orchestration?

Civic data is messy, distributed, and constantly changing formats. A traditional monolithic ETL pipeline breaks frequently and is hard to scale across hundreds of disparate municipal, state, and central data portals.

By structurally decoupling the system into autonomous agents:
1. **Resilience & Isolation**: Each public data source is owned by a single, isolated **Owner Agent**. If one source's format changes, only its agent breaks, while the rest of the ecosystem continues unaffected.
2. **Scalability**: New data sources can be added dynamically by simply registering a new Owner Agent configuration, without modifying the core system logic. The system is designed to easily scale from 8-12 agents to hundreds.
3. **Trust & Verification**: We implement a robust separation of concerns. Owner Agents propose updates via **Data PRs**. A separate, specialized **Verifier Agent** audits these proposals against strict canonical schemas and live source checks before anything is merged into the production dataset.
4. **Living Infrastructure**: The system doesn't just display data; it actively monitors, detects changes, normalizes, and curates a living representation of reality.

## Architecture

The system is separated into distinct layers for modularity and scalability:

- **Frontend (`/frontend`)**: A Next.js web application that displays the canonical dataset and provides real-time visibility into the system's health, active agents, and pending Data PRs.
- **Backend & Agent Runtime (`/backend`)**: A FastAPI Python application serving as both the API for the frontend and the runtime orchestrator for the agents.
- **Source Registry (`/backend/app/agents/registry.py`)**: A configuration-driven directory of all active data sources, their assigned agents, schemas, and scraping strategies.
- **Dataset Storage**: PostgreSQL database holding the canonical dataset (using `JSONB` for flexibility), agent states, and Data PR records.

## Data Flow

1. **Poll**: An Owner Agent polls its assigned `source_url` at a defined `polling_interval`.
2. **Detect Change**: The agent compares the fetched data against the `current_hash` to detect updates.
3. **Normalize**: New or updated data is normalized into a standard canonical schema.
4. **Propose Data PR**: The Owner Agent creates a Data PR with the proposed changes.
5. **Verify**: The Verifier Agent picks up pending PRs, validates the schema, and ensures data integrity.
6. **Merge & Publish**: Validated PRs are merged into the canonical dataset, instantly updating the live website.

## Getting Started

*(Instructions on running the system via Docker Compose will be added here once fully implemented)*
