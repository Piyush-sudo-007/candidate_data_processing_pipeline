from typing import List, Dict, Any
from .model import CanonicalProfile, Location, Skill, Experience, Provenance, Education
from datetime import datetime

class CandidatePipeline:
  def __init__(self):
    self.source_priority = ["ats_json", "github_api"]

  def _calculate_years_exp(self, experience_list: List[Experience]) -> float:
    total_days = 0
    for exp in experience_list:
      if not exp.start:
        continue

      try:
        start_dt = datetime.strptime(exp.start, "%Y-%m")
        end_dt = datetime.strptime(exp.end, "%Y-%m") if exp.end else datetime.now()
        total_days += (end_dt - start_dt).days
      except Exception:
        continue
    return round(total_days/ 365.25, 1) if total_days > 0 else 0.0

  def merge_profiles(self, candidate_id: str, parsed_sources: Dict[str, Dict[str, Any]]) -> CanonicalProfile:
    profile_data = {
      "candidate_id": candidate_id
    }
    provenance_list = []

    for field in ["full_name", "headline"]:
      resolved_val = None
      chosen_source = None

      for source in self.source_priority:
        if source in parsed_sources and parsed_sources[source].get(field):
          resolved_val = parsed_sources[source][field]
          chosen_source = source
          break
      
      profile_data[field] = resolved_val
      if chosen_source:
        provenance_list.append(Provenance(field=field, source=chosen_source, method="priority_override"))
      
    resolved_location = Location()
    location_source = None

    for source in self.source_priority:
      if source in parsed_sources and parsed_sources[source].get("location"):
        loc_src = parsed_sources[source]["location"]
        resolved_location = Location(
          city=loc_src.get("city"),
          region=loc_src.get("region"),
          country=loc_src.get("country")
        )
        location_source = source
        break
    profile_data["location"] = resolved_location
    if location_source:
      provenance_list.append(Provenance(field="location", source=location_source, method="struct_merge"))

    for field_name in ["emails", "phones"]:
      all_vals = []
      for source, payload in parsed_sources.items():
        for val in payload.get(field_name, []):
          if val and val not in all_vals:
            all_vals.append(val)
            provenance_list.append(Provenance(field=f"{field_name}[{val}]", source=source, method="append_unique"))
      profile_data[field_name]= all_vals

    merged_links = {"linkedin": None, "github": None, "portfolio": None, "other": []}
    for source, payload in parsed_sources.items():
      source_links = payload.get("links", {})
      for platform, url in source_links.items():
        if platform == "other":
          for link in url:
            if link not in merged_links["other"]:
              merged_links["other"].append(link)
        elif not merged_links[platform] and url:
          merged_links[platform] = url
          provenance_list.append(Provenance(field=f"links.{platform}", source=source, method="dict_merge"))
    profile_data["links"] = merged_links

    merged_exp: List[Experience] = []
    for source, payload in parsed_sources.items():
      for exp in payload.get("experience", []):
        comp = exp.company if isinstance(exp, Experience) else exp.get("company")
        ttl = exp.title if isinstance(exp, Experience) else exp.get("title")
        
        if not any(e.company.lower() == comp.lower() and e.title.lower() == ttl.lower() for e in merged_exp):
          if isinstance(exp, Experience):
            merged_exp.append(exp)
          else:
            merged_exp.append(Experience(**exp))
          provenance_list.append(Provenance(field=f"experience[{comp}]", source=source, method="append_unique_struct"))
    profile_data["experience"] = merged_exp

    merged_edu: List[Education] = []
    for source, payload in parsed_sources.items():
      for edu in payload.get("education", []):
        if not any(e.institution.lower() == edu["institution"].lower() for e in merged_edu):
          if isinstance(edu, Education):
            merged_edu.append(edu)
          else:
            merged_edu.append(Education(**edu))
          provenance_list.append(Provenance(field=f"education[{edu['institution']}]", source=source, method="append_unique_struct"))
    profile_data["education"] = merged_edu

    skill_map: Dict[str, Skill] = {}
    for source, payload in parsed_sources.items():
      base_confidence = 0.9 if source == "ats_json" else 0.6
      for skill_item in payload.get("skills", []):
        skill_name = skill_item if isinstance(skill_item, str) else skill_item.get("name")
        canonical_name= skill_name.strip().upper()

        if canonical_name in skill_map:
          if source not in skill_map[canonical_name].sources:
            skill_map[canonical_name].sources.append(source)
            skill_map[canonical_name].confidence = min(skill_map[canonical_name].confidence + 0.1, 1.0)
        else:
          skill_map[canonical_name] = Skill(name=skill_name, confidence=base_confidence, sources=[source])

    profile_data["skills"] = list(skill_map.values())

    profile_data["years_experience"] = self._calculate_years_exp(merged_exp)
    profile_data["provenance"] = provenance_list
    profile_data["overall_confidence"] = 0.85 if "ats_json" in parsed_sources else 0.5

    return CanonicalProfile(**profile_data)