# download WCA export then build dataset
# Windows:  powershell -File scripts/download_data.ps1
# POSIX:    bash scripts/download_data.sh
python scripts/download_data.py
python scripts/build_dataset.py --source raw
