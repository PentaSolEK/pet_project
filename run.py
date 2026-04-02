import sys
from pathlib import Path

# Корень проекта (каталог с pyproject.toml)
root = Path(__file__).resolve().parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.ticketshop.main:app",
        port=8000,
        reload=True,
    )
