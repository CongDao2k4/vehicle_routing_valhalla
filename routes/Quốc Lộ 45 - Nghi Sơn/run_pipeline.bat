@echo off
:: Định dạng tiếng Việt cho CMD
chcp 65001 > nul

:: ÉP PYTHON LUÔN CHẠY Ở CHẾ ĐỘ UTF-8 (Sửa lỗi UnicodeEncodeError)
set PYTHONIOENCODING=utf-8

echo ===== BẮT ĐẦU CHẠY CÁC FILE PYTHON =====
echo.

:: File 1
echo Chạy 01_build_station_tree.py...
python "01_build_station_tree.py"
echo Đang chờ 3 giây...
ping 127.0.0.1 -n 4 > nul
echo ------------------------------------------

:: File 2
echo Chạy 02_build_origin_candidates.py...
python "02_build_origin_candidates.py"
echo Đang chờ 3 giây...
ping 127.0.0.1 -n 4 > nul
echo ------------------------------------------

:: File 3
echo Chạy 03_download_routes.py...
python "03_download_routes.py"
echo Đang chờ 3 giây...
ping 127.0.0.1 -n 4 > nul
echo ------------------------------------------

:: File 4
echo Chạy 04_analyze_origin_routes.py...
python "04_analyze_origin_routes.py"
echo Đang chờ 3 giây...
ping 127.0.0.1 -n 4 > nul
echo ------------------------------------------

:: File 5
echo Chạy 05_build_final_edges.py...
python "05_build_final_edges.py"
echo Đang chờ 3 giây...
ping 127.0.0.1 -n 4 > nul
echo ------------------------------------------

:: File 6
echo Chạy generate_ticket_submission.py...
python "generate_ticket_submission.py"
echo Đang chờ 3 giây...
ping 127.0.0.1 -n 4 > nul
echo ------------------------------------------

:: File 7
echo Chạy 04_analyze_origin_routes_restricted.py...
python "04_analyze_origin_routes_restricted.py"
echo Đang chờ 3 giây...
ping 127.0.0.1 -n 4 > nul
echo ------------------------------------------

:: File 8
echo Chạy 05_build_final_edges_restricted.py...
python "05_build_final_edges_restricted.py"
echo Đang chờ 3 giây...
ping 127.0.0.1 -n 4 > nul
echo ------------------------------------------

:: File 9
echo Chạy generate_ticket_submission_restricted.py...
python "generate_ticket_submission_restricted.py"
echo Đang chờ 3 giây...
ping 127.0.0.1 -n 4 > nul
echo ------------------------------------------

echo ===== HOÀN THÀNH TẤT CẢ CÁC FILE =====
pause