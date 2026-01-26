import json
from backend.models.extraction_result import ExtractionResult

schema = ExtractionResult.model_json_schema()
print(json.dumps(schema, indent=2))
