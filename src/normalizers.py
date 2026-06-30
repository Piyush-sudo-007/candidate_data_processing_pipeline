import re
import phonenumbers
from iso3166 import countries
from typing import Any, Optional

def normalize_phone(phone_str: Any) -> Optional[str]:
  if not phone_str or not isinstance(phone_str, str):
    return None
  
  try:
    parsed = phonenumbers.parse(phone_str, "IN")

    if phonenumbers.is_possible_number(parsed):
      return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    
  except Exception:
    pass

  return None

def normalize_country(country_str: Any) -> Optional[str]:
  if not country_str or not isinstance(country_str, str):
    return None
  
  clean_name = country_str.strip().upper()

  if clean_name in countries:
    return clean_name
  
  for country in countries:
    if clean_name in country.name.upper() or clean_name == country.alpha2:
      return country.alpha2
  
  return None
  
def normalize_date(date_str: Any) -> Optional[str]:
  if not date_str or not isinstance(date_str, str):
    return None
  clean_date = date_str.strip()

  match = re.match(r'^(\d{4})[-\/]((?:0[1-9]|1[0-2]))', clean_date)

  if match:
    return f"{match.group(1)}-{match.group(2)}"
  
  return None