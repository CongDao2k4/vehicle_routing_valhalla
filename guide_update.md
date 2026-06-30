# Hướng dẫn Cập nhật Dữ liệu Trạm ePass và Routing

Lên epass tra cứu giá vé. mở **chrome tool for developer** -> mục **Network** để bắt API lấy json giá vé.

dữ liệu lấy giá vé lượt, vé tháng, vé quý. Lấy hết và vứt vào 1 file ví dụ trong thư mục **routes/Cao_tốc_Pháp_Vân-Cầu_Giẽ/** , xem thư mục **new_epass** rồi paste dữ liệu thu thập từ API json vào file **gia_ve.json**.

Cấu trúc có dạng:
```json
[
    {
        "ticketType": 1,
        "ticketTypeName": "Vé lượt",
        "routeName": "Cao tốc Pháp Vân – Cầu Giẽ",
        "stationType": 0,
        "stationTypeName": "CLOSED",
        "stageName": "Đại Xuyên - Vạn Điểm",
        "stationInName": "Đại Xuyên",
        "stationOutName": "Vạn Điểm",
        "priceType": 1,
        "priceTypeName": "Giá thường",
        "feeType1": 11585,
        "feeType2": 11585,
        "feeType3": 17378,
        "feeType4": 23170,
        "feeType5": 34756
    },
    ...
    ...
    {
        "ticketType": 4,
        "ticketTypeName": "Vé tháng",
        "routeName": "Cao tốc Pháp Vân – Cầu Giẽ",
        "stationType": 0,
        "stationTypeName": "CLOSED",
        "stageName": "Đại Xuyên - Vạn Điểm",
        "stationInName": "Đại Xuyên",
        "stationOutName": "Vạn Điểm",
        "priceType": 1,
        "priceTypeName": "Giá thường",
        "feeType1": 347563,
        "feeType2": 347563,
        "feeType3": 521345,
        "feeType4": 695127,
        "feeType5": 1042690
    },
    ...
    ...
    {
        "ticketType": 5,
        "ticketTypeName": "Vé quý",
        "routeName": "Cao tốc Pháp Vân – Cầu Giẽ",
        "stationType": 0,
        "stationTypeName": "CLOSED",
        "stageName": "Đại Xuyên - Vạn Điểm",
        "stationInName": "Đại Xuyên",
        "stationOutName": "Vạn Điểm",
        "priceType": 1,
        "priceTypeName": "Giá thường",
        "feeType1": 938421,
        "feeType2": 938421,
        "feeType3": 1407632,
        "feeType4": 1876843,
        "feeType5": 2815265
    }
]
```

## Cách chạy:
Trong từng thư mục con của **routes/**, ví dụ **routes/Cao_tốc_Pháp_Vân-Cầu_Giẽ/**:
- chạy file **build_graph.py**: nó sẽ lấy file **new_epass/gia_ve.json** -> tạo ra các file `nodes_new.json`, `edges_new.json`, `tickets_new.json` .
- Sau đó nó so sánh với `nodes.json`, `edges.json`, `tickets.json` (3 file json này là dữ liệu trạm, cạnh đồ thị nối 2 trạm, giá vé ứng với từng cạnh đồ thị nối 2 trạm).
- Sau đó code **build_graph.py** sẽ apply dữ liệu mới từ các file **.._new.json** vào các file **nodes.json**, **edges.json**, **tickets.json**. Đồng thời có print ra kahsc biệt, thông báo dữ liệu nào được thêm, sửa , xóa.

- Xem các file **.txt** trong thư mục **note/** để xem các file : **new_nodes.txt**, **new_edges.txt**, **new_tickets.txt**, **modified_...txt**, **removed_...txt**

- Nếu còn lo bản json cũ sẽ bị mất thì xem lại thư mục **Cao_tốc_Pháp_Vân-Cầu_Giẽ/backup** để xem lại các file của dữ liệu phiên bản cũ. Các file json cũ sẽ được lưu vào thư mục **backup** 

### Sau khi chạy file build_graph.py 

- xem các file trong note/ của từng tuyến đường. Xem có nodes mới thì phải làm dưới đây, còn trường hợp thêm toll_booth của 1 trạm node epass_name đã tồn tại cũng được xử lý ở dưới đây

# Tài liệu này hướng dẫn cách thêm hoặc sửa đổi dữ liệu trạm thu phí cho luồng xử lý Routing & Ticket Mapping (engine Valhalla).

## Các file dữ liệu cốt lõi
Mọi thao tác cập nhật dữ liệu đều diễn ra trong thư mục của từng tuyến đường, ví dụ: `routes/Mai_Sơn-Quốc_Lộ_45/`.
- `merged_Mai_Sơn-Quốc_Lộ_45.csv`: Chứa tọa độ các bốt thu phí.
- `edges.json`: Khai báo danh sách các cặp trạm (đi - đến) cần tìm đường.
- `tickets.json`: Khai báo bảng giá vé giữa các cặp trạm.
- `nodes.json`: Khai báo vị trí các trạm chính (phục vụ hiển thị/frontend).

> **Lưu ý:** Hệ thống đã được tích hợp cơ chế tự động chuẩn hóa tiếng Việt (NFC) ở file `00_normalize_data.py`. Bạn có thể thoải mái sửa các file bằng tay mà không lo lỗi font chữ khi hệ thống xử lý.

---

## Case 1: Thêm một nhánh/bốt phụ vào Trạm Epass Name đã có sẵn
*Trường hợp áp dụng: Một nút giao (ví dụ Nút giao Gia Miêu) vừa xây thêm một bốt nhánh/trạm con mới nằm cách đó vài trăm mét.*

**Bước 1: Cập nhật file `.csv`**
Mở file `.csv` bằng Excel hoặc trình soạn thảo, thêm một dòng mới:
- Các cột của trạm mẹ (`epass_name`, `google_name`, `osm_name`, `osm_id`, `latitude`, `longitude`): **Bắt buộc copy y hệt** từ các dòng cũ của trạm mẹ đó để hệ thống gom nhóm (group) bốt mới về đúng trạm.
- Cột `distance_to_origin`: Điền khoảng cách tương đối (hoặc để `0.0`).
- Các cột bốt con (`origin_osm_id`, `origin_osm_name`, `origin_osm_latitude`, `origin_osm_longitude`): **Điền thông tin và tọa độ mới** của cái bốt vừa được xây.

**Bước 2:** Chỉ vậy là đủ! Hãy chuyển thẳng tới phần **Hướng dẫn chạy Script** bên dưới. Không cần sửa file JSON vì tên trạm mẹ đã có sẵn trong danh sách tuyến và bảng vé.

---

## Case 2: Thêm một Trạm ePass hoàn toàn mới
*Trường hợp áp dụng: Mở rộng tuyến cao tốc, khai trương một nút giao/trạm thu phí mới hoàn toàn.*

### Bước 1: Thêm vào file `.csv`
**Phải tự tìm epass_name, google_name, tên trạm osm_name, osm_id, latitude, longitude trên mạng dựa theo tên epass**
Thêm dòng thông tin trạm mới vào file `.csv`. Hãy chú ý đặt tên `epass_name` thống nhất vì nó sẽ dùng làm khóa (key) để liên kết với các file JSON. Nếu trạm có nhiều bốt (nhánh), bạn tạo nhiều dòng với chung `epass_name` nhưng khác thông tin ở các cột `origin_*` giống như Case 1.

### Bước 2: Khai báo đoạn đường vào `edges.json`
Định nghĩa trạm mới này sẽ có các tuyến kết nối (edges) với những trạm nào. Cấu trúc JSON khi thêm 1 đoạn đường mới:

```json
{
    "source": "Tên Trạm Đi (vd: Nút giao Mới)",
    "target": "Tên Trạm Đến (vd: Nút giao Hà Lĩnh)",
    "routeName": "<tên route từ các json khác trong file edges.json>",
    "stageName": "<tên trạm đi> - <tên trạm đến>",
    "stationType": 0,
    "stationTypeName": "CLOSED",
    "sourceOsmId": "",
    "targetOsmId": ""
}
```
**Quy tắc:**
- `"source"` và `"target"` , `"stationType"` và `"stationTypeName"`: **Bắt buộc gõ chính xác** tên trạm (`epass_name`) đã khai báo ở file CSV.
- Các trường còn lại (`routeName`, `stageName`, `sourceOsmId`, ``): Không bắt buộc với pipeline xử lý, có thể để **chuỗi rỗng `""` hoặc số `0`** để tiết kiệm thời gian.

### Bước 3: Khai báo giá vé vào `tickets.json`
Cấu hình giá cước cho tuyến đường vừa tạo ở Bước 2.

```json
{
    "refType": "EDGE",
    "refId": [
        "Nút giao Mới",
        "Nút giao Hà Lĩnh"
    ],
    "tickets": [
        {
            "ticketType": 1,
            "ticketTypeName": "Vé lượt",
            "prices": [
                {
                    "priceType": 1,
                    "priceTypeName": "Giá thường",
                    "feeType1": 15000,
                    "feeType2": 25000,
                    "feeType3": 35000,
                    "feeType4": 45000,
                    "feeType5": 60000
                }
            ]
        }
    ],
    "osmId": []
}
```
**Quy tắc:**
- `"refId"`: **Bắt buộc**. Là mảng chứa đúng 2 phần tử Tên Trạm đi và Trạm đến. (Khớp với `source` và `target` ở Bước 2).
- `"tickets"`: **Bắt buộc**. Chứa thông tin mảng giá vé các loại xe.
- `"osmId"`: **Tùy chọn**. Có thể để mảng rỗng `[]` hoặc xóa luôn key này cũng được (hệ thống tự động map theo tên trạm).

### Bước 4: Khai báo vào `nodes.json`
hiển thị các điểm Node lớn.
```json
{
    "stationName": "Nút giao Mới",
    "stationType": 0,
    "stationTypeName": "CLOSED",
    "latitude": 19.827975,
    "longitude": 105.691807,
    "stationOsmId": "123456789",
    "incoming_edges": [],
    "outgoing_edges": []
}
```
- **Bắt buộc:** Tên trạm (`stationName`) là `epass_name`, Tọa độ (`latitude`, `longitude`) là tọa độ tương ứng.
- **Để trống:** `"incoming_edges"` và `"outgoing_edges"` có thể để mảng rỗng `[]`.

---

## 🚀 Hướng dẫn chạy Script (Build Pipeline)
Sau khi bạn đã sửa tay xong dữ liệu CSV và JSON, bạn cần chạy script để hệ thống download lại bản đồ đường đi ngắn nhất và compile ra file kết quả. (Đảm bảo Valhalla local đang chạy).

### Đối với Windows
1. Mở thư mục tuyến đường (ví dụ: `routes/Mai Sơn - Quốc Lộ 45`).
2. Click đúp vào file **`run_pipeline.bat`**.
3. Một cửa sổ đen (CMD) sẽ hiện lên. Script sẽ chạy lần lượt:
   - File `00_normalize_data.py`: Dọn dẹp lỗi font chữ tiếng Việt, tự lưu lại file JSON, CSV cho chuẩn.
   - Các file từ `01` đến `06`: Lọc ứng viên -> Download Routes -> Tìm đường ngắn nhất -> Map giá vé.
4. Đợi đến khi màn hình hiện `===== HOÀN THÀNH TẤT CẢ CÁC FILE =====`. Nhấn phím bất kỳ để tắt.

### Đối với Linux / MacOS
1. Mở Terminal.
2. Dùng lệnh `cd` để trỏ vào thư mục tuyến đường.
3. Cấp quyền thực thi (nếu là lần đầu): `chmod +x run_pipeline.sh`
4. Chạy script: `./run_pipeline.sh`
*(Chú ý: Hãy đảm bảo file `run_pipeline.sh` của bạn cũng đã được bổ sung lệnh gọi `python "00_normalize_data.py"` ở phần đầu).*

**Thành quả:**
Kiểm tra lại thư mục, bạn sẽ thu được file **`ticket_submission.json`** chứa toàn bộ payload đã được routing chuẩn xác kèm giá vé, sẵn sàng gửi API lên server!
