import json
from src.parsers import DataParser
from src.engine import CandidatePipeline
from src.projector import OutputProjector

def main():
    raw_ats_input = {
        "contact_info": {
            "name": "Alex Mercer", 
            "cell_phone": "+15550192834",
            "email": "alex@mercer.dev"
        },
        "location_data": {"city_name": "San Francisco", "state": "CA", "country": "United States"},
        "tagged_skills": ["Python", "Backend Development"],
        "work_history": [
            {
                "employer": "TechCorp",
                "role": "Software Engineer",
                "from_date": "2023-01",
                "to_date": "2025-12",
                "desc": "Built core APIs"
            }
        ],
        "education_history": [
            {"institution": "Stanford University", "degree": "B.S.", "major": "Computer Science", "grad_year": "2022"}
        ]
    }

    raw_github_input = {
        "name": "Alex Mercer Jr.",
        "email": "alex.mercer@github.com",
        "html_url": "https://github.com/amercer",
        "bio": "Building microservices in Go and Python containers."
    }

    parsed_ats = DataParser.parse_ats_json(raw_ats_input)
  
    parsed_ats["education"] = [
        {
            "institution": edu["institution"],
            "degree": edu["degree"],
            "field": edu["major"],
            "end_year": edu["grad_year"]
        } for edu in raw_ats_input.get("education_history", [])
    ]
    
    parsed_gh = DataParser.parse_github_api(raw_github_input)

    all_sources = {
        "ats_json": parsed_ats,
        "github_api": parsed_gh
    }

    transformer = CandidatePipeline()
    canonical_profile = transformer.merge_profiles(candidate_id="cand_001", parsed_sources=all_sources)
    
    print("--- INTERNAL CANONICAL PROFILE ---")
    print(json.dumps(canonical_profile.model_dump(), indent=2))

    runtime_config = {
        "fields": [
            {"path": "full_name", "type": "string", "required": True},
            {"path": "primary_email", "from": "emails[0]", "type": "string", "required": True},
            {"path": "github_link", "from": "links.github", "type": "string"},
            {"path": "years_experience", "type": "number"},
            {"path": "skills", "type": "array"}
        ],
        "include_confidence": True,
        "on_missing": "null"
    }

    projected_output = OutputProjector.project(canonical_profile, runtime_config)
    
    print("\n--- SHAPED RUNTIME PROJECTED OUTPUT ---")
    print(json.dumps(projected_output, indent=2))

if __name__ == "__main__":
    main()