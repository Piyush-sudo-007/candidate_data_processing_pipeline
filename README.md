# Multi-Source Candidate Data Transformer

An enterprise-grade, deterministic ETL ingestion pipeline built to ingest candidate information from multiple structured and unstructured data sources, resolve entity matching conflicts, and output a canonical candidate profile.

## Key Architectural Decisions

1. **Strict Type Safety & Enforcement**: Built using `Pydantic v2` models to ensure malformed inputs or unintended type mutations are caught instantly at runtime before database entry points.
2. **Deterministic Priority Overrides**: Implements strict rule-based hierarchies (e.g., ATS entries override unverified social hooks) to ensure data transformations are reproducible and predictable.
3. **Traceable Provenance**: Every field modification tracks its origin source and internal consolidation method, supporting transparent auditing for automated data tracking.
4. **Decoupled Projection Layer**: The canonical candidate schema remains separate from custom output requests. A runtime translation utility allows end-users to rename paths, isolate items, and change target formats without modifying underlying business logic.

## Start Guide

1. Clone the Repository

```
git clone https://github.com/Piyush-sudo-007/candidate_data_processing_pipeline.git
```

2. Go Inside Folder

```
cd candidate_data_processing_pipeline
```

3. Create a virtual environment

```
python -m venv myenv
```

4. Activate Virtual Environment(Windows)

```
./myenv/Scripts/activate
```

5. Install Dependencies

```
pip install -r requirements.txt
```

6. Execute file

```
python main.py
```

7. Run tests

```
pytest tests/
```
