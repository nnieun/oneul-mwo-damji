"""Export the same OpenAPI schema served by /openapi.json, without opening a camera."""
import json
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'backend'))
from app.main import app
path=root/'docs'/'openapi.json'
path.write_text(json.dumps(app.openapi(),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(path)
