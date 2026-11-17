import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'app'))
from guidance import basic_guidance

def test_goat_guidance():
    message = basic_guidance('goat pox?')
    assert 'veterinarian' in message.lower()
    assert 'goatpox' in message.lower()

def test_healthy_is_not_assurance():
    assert 'does not exclude' in basic_guidance('healthy').lower()
