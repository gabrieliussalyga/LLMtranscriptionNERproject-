import os
import glob

# Path to entity files
ENTITY_DIR = "backend/models/entities/v1"

def update_file(filepath):
    with open(filepath, "r") as f:
        content = f.read()

    # Skip if already updated
    if "MedicalEntityBase" in content:
        print(f"Skipping {filepath} (already updated)")
        return

    # Replace imports
    new_content = content.replace("from pydantic import BaseModel", "from pydantic import Field")
    if "from pydantic import Field" not in new_content:
         new_content = content.replace("from pydantic import BaseModel", "from pydantic import Field")
    
    # Add Base import
    new_content = "from backend.models.base import MedicalEntityBase\n" + new_content

    # Replace inheritance
    new_content = new_content.replace("(BaseModel)", "(MedicalEntityBase)")

    # Clean up potentially duplicate or unused imports (simple heuristic)
    new_content = new_content.replace("from pydantic import Field, Field", "from pydantic import Field")

    with open(filepath, "w") as f:
        f.write(new_content)
    print(f"Updated {filepath}")

files = glob.glob(os.path.join(ENTITY_DIR, "*.py"))
for f in files:
    if "__init__.py" not in f:
        update_file(f)
