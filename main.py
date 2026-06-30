import json
import os
from src.parsers import DataParser
from src.engine import CandidatePipeline
from src.projector import OutputProjector

def load_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")

    raw_ats_input= load_file(os.path.join(data_dir, "sample_ats.json"))

    raw_github_input =load_file(os.path.join(data_dir, "sample_github.json"))

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

    runtime_config = load_file(os.path.join(data_dir, "runtime_config.json"))

    projected_output = OutputProjector.project(canonical_profile, runtime_config)
    
    print("\n--- SHAPED RUNTIME PROJECTED OUTPUT ---")
    print(json.dumps(projected_output, indent=2))

if __name__ == "__main__":
    main()