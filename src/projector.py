from typing import Dict, Any, List
from src.model import CanonicalProfile

class OutputProjector:
  @staticmethod
  def _get_nested_value(data: Dict[str, Any], path: str) -> Any:
    parts = path.split('.')
    current = data
    for part in parts:
      if isinstance(current, dict):
        current = current.get(part)
      else:
        return None
    return current

  @staticmethod
  def project(profile: CanonicalProfile, config: Dict[str, Any]) -> Dict[str, Any]:
    output = {}
    profile_dict = profile.model_dump()
    
    fields_config: List[Dict[str, Any]] = config.get("fields", [])
    on_missing = config.get("on_missing", "null")
    
    for item in fields_config:
      target_path = item.get("path")
      custom_name = item.get("from", item.get("path"))
      
      if "[" in custom_name:
        base_key = custom_name.split("[")[0]
        try:
          idx = int(custom_name.split("[")[1].replace("]", ""))
          source_list = profile_dict.get(base_key, [])
          val = source_list[idx] if idx < len(source_list) else None
        except Exception:
          val = None
      elif "." in custom_name:
        val = OutputProjector._get_nested_value(profile_dict, custom_name)
      else:
        val = profile_dict.get(custom_name)

      if val is None or val == [] or val == {}:
        if on_missing == "error" and item.get("required", False):
          raise ValueError(f"Required field target '{custom_name}' is missing.")
        elif on_missing == "omit":
          continue
        else:
          output[target_path] = None
      else:
          output[target_path] = val

    if config.get("include_confidence", True):
      output["overall_confidence"] = profile_dict.get("overall_confidence")
        
    return output