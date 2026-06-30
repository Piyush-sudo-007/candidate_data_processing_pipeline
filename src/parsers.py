from typing import Dict, Any, Optional
from .normalizers import normalize_country, normalize_date, normalize_phone

class DataParser:
  @staticmethod
  def parse_ats_json(raw_json: Dict[str, Any]) -> Dict[str, Any]:
    contact = raw_json.get("contact_info", {})
    loc = raw_json.get("location_data", {})

    return{
      "full_name": contact.get("name"),
      "emails": [contact.get("email")] if contact.get("email") else [],
      "phones": [normalize_phone(contact.get("cell_phone"))] if normalize_phone(contact.get("cell_phone")) else [],
      "location": {
          "city": loc.get("city_name"),
          "region": loc.get("state"),
          "country": normalize_country(loc.get("country"))
      },
      "skills": raw_json.get("tagged_skills", []),
      "experience": [
          {
              "company": exp.get("employer"),
              "title": exp.get("role"),
              "start": normalize_date(exp.get("from_date")),
              "end": normalize_date(exp.get("to_date")),
              "summary": exp.get("desc")
          } for exp in raw_json.get("work_history", [])
      ]
    }
  
  @staticmethod
  def parse_github_api(raw_api_data: Dict[str, Any]) -> Dict[str, Any]:
    bio_skills = []
    bio = raw_api_data.get("bio", "")

    for tech in ["Python", "Docker", "Java", "C++"]:
      if tech.lower() in bio.lower():
        bio_skills.append(tech)

    return{
      "full_name": raw_api_data.get("name"),
      "emails": [raw_api_data.get("email")] if raw_api_data.get("email") else [],
      "links": {"github": raw_api_data.get("html_url")},
      "skills": bio_skills,
      "headline": bio if bio else None
    }