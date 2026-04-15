# Star-cubing Iceberg Cube Miner

A Python and SQL project scaffold for computing Iceberg Cubes on large-scale retail POS data using the Star-cubing algorithm.

## Objectives

- Build a reusable data mining pipeline for Iceberg Cube computation.
- Support synthetic POS data generation for development and testing.
- Store fact data and cube aggregates in relational databases (PostgreSQL/SQL Server).

## Project Structure

- `data/`: Raw and processed datasets.
- `src/`: Python source code for configuration, data generation, DB access, and Star-cubing logic.
- `sql/`: Schema and OLAP query scripts.
- `powerbi/`: Placeholder directory for BI reports.
- `main.py`: Entry point for orchestration.

## Quick Start

1. Create and activate a Python virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Fill in environment variables in `.env`.
4. Initialize database schema using `sql/01_schema.sql`.
5. Run the entry point:
   ```bash
   python main.py
   ```

## Status

This scaffold includes boilerplate classes and function signatures. Core Star-cubing logic and optimization steps are intentionally left for implementation.
