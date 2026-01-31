# User Scripts

Developer- und Utility-Scripts für SoundTouchBridge.

## 📁 Scripts

### Testing & Development

- **test-all.ps1**: Vollständiger Test-Suite (Unit + Integration + E2E)
  ```powershell
  cd scripts/
  .\test-all.ps1              # All tests + Docker build + E2E
  .\test-all.ps1 -SkipBuild   # Nur Tests (kein Docker)
  .\test-all.ps1 -SkipE2E     # Nur Unit/Integration Tests
  ```

### Deployment & Maintenance

- **clear-database.ps1**: Löscht Geräte-Datenbank auf TrueNAS
  ```powershell
  .\clear-database.ps1
  ```
  Interaktiv mit Confirmation Prompt.

### Radio API Demos

- **demo_radio_api.py**: Radio Search Demo (Absolut Relax)
  ```bash
  python scripts/demo_radio_api.py
  ```

- **test_absolut_relax.py**: Radio Stream Test (HTTP HEAD request)
  ```bash
  python scripts/test_absolut_relax.py
  ```

## 🔧 Prerequisites

### PowerShell Scripts
- PowerShell 7+
- Python Virtual Environment: `.venv/` (im Repository Root)
- Docker / Podman (für test-all.ps1 Docker build)

### Python Scripts
- Python 3.11+
- Dependencies aus `backend/requirements.txt`

## 📝 Usage Examples

### Backend Tests ausführen
```powershell
cd scripts/
.\test-all.ps1 -SkipBuild -SkipE2E
```

### Radio API testen
```bash
# Virtuelle Umgebung aktivieren
source ../.venv/bin/activate  # Linux/Mac
..\.venv\Scripts\Activate.ps1  # Windows

# Demo ausführen
python demo_radio_api.py
```

### TrueNAS Datenbank zurücksetzen
```powershell
.\clear-database.ps1
# Confirmation: yes
```

## 🗂️ Related Folders

- **backend/**: Backend Source Code + Tests
- **deployment/**: Container Deployment Scripts
- **e2e/**: End-to-End Demo Scripts (veraltet, siehe backend/tests/e2e/)

## 🧪 Test Coverage

Scripts verwenden `backend/pytest.ini` Konfiguration:
- Coverage Threshold: 75%
- HTML Report: `backend/htmlcov/index.html`
- Testpath: `backend/tests/` (unit, integration, e2e)

## 📚 Documentation

- [Main README](../README.md)
- [Backend README](../backend/README.md)
- [Deployment README](../deployment/README.md)
