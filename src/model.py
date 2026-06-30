from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Location(BaseModel):
  city: Optional[str] = None
  region: Optional[str] = None
  country: Optional[str] = None

class Skill(BaseModel):
  name: str
  confidence: float
  sources: List[str]

class Experience(BaseModel):
  company: str
  title: str
  start: Optional[str] = None
  end: Optional[str] = None
  summary: Optional[str] = None

class Education(BaseModel):
  institution: str
  degree: Optional[str] = None
  field: Optional[str] = None
  end_year: Optional[str] = None

class Provenance(BaseModel):
  field: str
  source: str
  method: str

class CanonicalProfile(BaseModel):
  candidate_id: str
  full_name: Optional[str] = None
  emails: List[str] = Field(default_factory=List)
  phones: List[str] = Field(validate_default=List)
  location: Optional[Location] = None
  links: Dict[str, Any] = Field(default_factory=lambda: {"linkedin": None, "github": None, "portfolio": None, "other": []})
  headline: Optional[str] = None
  years_experience: Optional[float] = None
  skills: List[Skill] = Field(default_factory=list)
  experience: List[Experience] = Field(default_factory=list)
  education: List[Education] = Field(default_factory=list)
  provenance: List[Provenance] = Field(default_factory=list)
  overall_confidence: float = 0.0