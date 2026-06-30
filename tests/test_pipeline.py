import pytest
from src.normalizers import normalize_phone, normalize_country, normalize_date
from src.engine import CandidatePipeline
from src.projector import OutputProjector
from src.model import CanonicalProfile

def test_normalization_utilities():
  assert normalize_phone("93048 68598") == "+919304868598"
  assert normalize_phone("invalid-phone") is None
  assert normalize_country("India") == "INDIA"
  assert normalize_date("2023-01") == "2023-01"

def test_pipeline_integration():
  pipeline = CandidatePipeline()
  sample_sources = {
    "ats_json": {
      "full_name": "Test Candidate",
      "emails": ["test@candidate.com"],
      "phones": ["+919304868598"],
      "experience": [
        {"company": "Google", "title": "SWE", "start": "2024-01", "end": "2025-01"}
      ]
    }
  }
  profile = pipeline.merge_profiles("cand_test", sample_sources)
  
  assert profile.full_name == "Test Candidate"
  assert "+919304868598" in profile.phones
  assert profile.years_experience == 1.0

def test_dynamic_config_projection():
  profile = CanonicalProfile(
    candidate_id="123",
    full_name="Test Name",
    emails=["test@gmail.com"],
    overall_confidence=0.9
  )
  config = {
    "fields": [
      {"path": "name", "from": "full_name", "type": "string"},
      {"path": "email", "from": "emails[0]", "type": "string"}
    ],
    "include_confidence": True
  }
  result = OutputProjector.project(profile, config)
  assert result["name"] == "Test Name"
  assert result["email"] == "test@gmail.com"
  assert result["overall_confidence"] == 0.9