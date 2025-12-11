import os
import sys
from pathlib import Path

# Add project root to Python path to import main_ann
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
model_path = Path(__file__).parent.parent / "models"

from main_ann import Net

MODEL_FILE = {
    'handwrite_digit': 'model_oldtype.pkl'
}

def get_digit_classify_model():
    use_model_file = MODEL_FILE.get('handwrite_digit')
    model = Net.load(os.path.join(model_path,use_model_file),Net)
    return model