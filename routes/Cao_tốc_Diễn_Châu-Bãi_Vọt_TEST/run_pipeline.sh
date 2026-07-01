#!/bin/bash

# Force Python output encoding to UTF-8
export PYTHONIOENCODING=utf-8

echo "===== BẮT ĐẦU CHẠY CÁC FILE PYTHON ====="
echo ""

# Determine python command (python3 or python)
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

run_script() {
    local script_name=$1
    echo "Chạy ${script_name}..."
    $PYTHON_CMD "${script_name}"
    echo "Đang chờ 3 giây..."
    sleep 3
    echo "------------------------------------------"
}

run_script "00_normalize_data.py"
run_script "01_build_station_tree.py"
run_script "02_build_origin_candidates.py"
run_script "03_download_routes.py"
run_script "04_analyze_origin_routes.py"
run_script "05_build_final_edges.py"
run_script "generate_ticket_submission.py"
run_script "04_analyze_origin_routes_restricted.py"
run_script "05_build_final_edges_restricted.py"
run_script "generate_ticket_submission_restricted.py"

echo "===== HOÀN THÀNH TẤT CẢ CÁC FILE ====="
read -p "Press Enter to continue..."
