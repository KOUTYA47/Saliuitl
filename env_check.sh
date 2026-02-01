#!/usr/bin/env bash
set -euo pipefail

echo "[env_check] repo root: $(pwd)"
python -c "import torch; print('torch', torch.__version__, 'cuda', torch.cuda.is_available())"
python -c "import sklearn, skimage, PIL; print('sklearn', sklearn.__version__, 'skimage', skimage.__version__, 'PIL', PIL.__version__)"
echo "[env_check] OK"
