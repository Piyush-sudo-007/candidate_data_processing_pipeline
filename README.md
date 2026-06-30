# Multi-Source Candidate Data Transformer

An enterprise-grade, deterministic ETL ingestion pipeline built to ingest candidate information from multiple structured and unstructured data sources, resolve entity matching conflicts, and output a canonical candidate profile.

## Key Architectural Decisions

[Source Inputs] ---> [Data Parsers] ---> [Data Normalizers] ---> [Pipeline Engine] ---> [Canonical Profile] ---> [Output Projector]

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

## Sample Inputs

<details>
<summary><b>ATS JSON</b></summary>

```json
{
  "contact_info": {
    "name": "Piyush Dev",
    "cell_phone": "+91 93048 68598",
    "email": "piyushdevmgr@gmail.com"
  },
  "location_data": {
    "city_name": "Munger",
    "state": "Bihar",
    "country": "India"
  },
  "tagged_skills": ["Python", "Backend Development", "Docker"],
  "work_history": [
    {
      "employer": "Google",
      "role": "Software Engineer",
      "from_date": "2023-05",
      "to_date": "2026-06",
      "desc": "Designed scalable microservices and optimized database queries."
    }
  ],
  "education_history": [
    {
      "institution": "National Institute of Technology (NIT) Mizoram",
      "degree": "B.Tech",
      "major": "Computer Science and Engineering",
      "grad_year": "2027"
    }
  ]
}
```

</details>

<details>
<summary><b>GitHub API Response</b></summary>

```json
{
  "name": "Piyush Dev",
  "email": "piyushdev@gmail.com",
  "html_url": "https://github.com/Piyush-sudo-007",
  "bio": "Backend Engineer specializing in Docker setups and Python microservices. Passionate about open-source contribution."
}
```

</details>

<details>
<summary><b>Runtime Projection Configuration</b></summary>

```json
{
  "fields": [
    {
      "path": "full_name",
      "type": "string",
      "required": true
    },
    {
      "path": "primary_email",
      "from": "emails[0]",
      "type": "string",
      "required": true
    },
    {
      "path": "github_link",
      "from": "links.github",
      "type": "string"
    },
    {
      "path": "years_experience",
      "type": "number"
    },
    {
      "path": "skills",
      "type": "array"
    }
  ],
  "include_confidence": true,
  "on_missing": "null"
}
```

</details>

## Expected Output

<details>
<summary><b>Canonical Candidate Profile</b></summary>

```json
{
  "candidate_id": "cand_001",
  "full_name": "Piyush Dev",
  "emails": ["piyushdevmgr@gmail.com", "piyushdev@gmail.com"],
  "phones": ["+919304868598"],
  "location": {
    "city": "Munger",
    "region": "Bihar",
    "country": "INDIA"
  },
  "links": {
    "linkedin": null,
    "github": "https://github.com/Piyush-sudo-007",
    "portfolio": null,
    "other": []
  },
  "headline": "Backend Engineer specializing in Docker setups and Python microservices. Passionate about open-source contribution.",
  "years_experience": 3.1,
  "skills": [
    {
      "name": "Python",
      "confidence": 1.0,
      "sources": ["ats_json", "github_api"]
    },
    {
      "name": "Backend Development",
      "confidence": 0.9,
      "sources": ["ats_json"]
    },
    {
      "name": "Docker",
      "confidence": 1.0,
      "sources": ["ats_json", "github_api"]
    }
  ],
  "experience": [
    {
      "company": "Google",
      "title": "Software Engineer",
      "start": "2023-05",
      "end": "2026-06",
      "summary": "Designed scalable microservices and optimized database queries."
    }
  ],
  "education": [
    {
      "institution": "National Institute of Technology (NIT) Mizoram",
      "degree": "B.Tech",
      "field": "Computer Science and Engineering",
      "end_year": "2027"
    }
  ],
  "provenance": [
    {
      "field": "full_name",
      "source": "ats_json",
      "method": "priority_override"
    },
    {
      "field": "headline",
      "source": "github_api",
      "method": "priority_override"
    },
    {
      "field": "location",
      "source": "ats_json",
      "method": "struct_merge"
    },
    {
      "field": "emails[piyushdevmgr@gmail.com]",
      "source": "ats_json",
      "method": "append_unique"
    },
    {
      "field": "emails[piyushdev@gmail.com]",
      "source": "github_api",
      "method": "append_unique"
    },
    {
      "field": "phones[+919304868598]",
      "source": "ats_json",
      "method": "append_unique"
    },
    {
      "field": "links.github",
      "source": "github_api",
      "method": "dict_merge"
    },
    {
      "field": "experience[Google]",
      "source": "ats_json",
      "method": "append_unique_struct"
    },
    {
      "field": "education[National Institute of Technology (NIT) Mizoram]",
      "source": "ats_json",
      "method": "append_unique_struct"
    }
  ],
  "overall_confidence": 0.85
}
```

</details>

<details>
<summary><b>Runtime Projected Output</b></summary>

```json
{
  "full_name": "Piyush Dev",
  "primary_email": "piyushdevmgr@gmail.com",
  "github_link": "https://github.com/Piyush-sudo-007",
  "years_experience": 3.1,
  "skills": [
    {
      "name": "Python",
      "confidence": 1.0,
      "sources": ["ats_json", "github_api"]
    },
    {
      "name": "Backend Development",
      "confidence": 0.9,
      "sources": ["ats_json"]
    },
    {
      "name": "Docker",
      "confidence": 1.0,
      "sources": ["ats_json", "github_api"]
    }
  ],
  "overall_confidence": 0.85
}
```

</details>

## Testing

Run the complete test suite:

```bash
pytest tests/
```

<details>
<summary><b>Current Test Coverage</b></summary>

- ✅ ATS parser
- ✅ GitHub parser
- ✅ Phone normalization (E.164)
- ✅ Location normalization (ISO-3166)
- ✅ Duplicate email & phone resolution
- ✅ Rule-based priority overrides
- ✅ Provenance tracking
- ✅ Confidence score calculation
- ✅ Runtime projection
- ✅ Pydantic validation
- ✅ End-to-end pipeline execution

</details>

All tests pass successfully.
