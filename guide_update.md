# Hướng dẫn Cập nhật Dữ liệu Trạm ePass và Routing

**SỐ ĐIỆN THOẠI**: 0977497116

**Tạo .venv chạy python**: `python -m venv .venv`

**chạy load các thư viện**: `pip install -r requirements.txt`

**Chạy code script `wsl/Ubuntu$  sh scripts/01_download_data.sh`**

**Chạy `docker-compose.yml` để chạy valhalla local để tìm tuyến đường. Cần có file .osm.pbf đã tải vào `thư_mục_gốc/valhalla-data/` nhé**

# Lấy data và update dữ liệu mới

## TRẠM ĐƠN: Với trạm đơn (không thuộc tuyến đường nào) => thêm vào file **.csv** và **tickets.json** ở trong thư mục **gốc thư mục/routes/IndependentNode/** là được.

**Bước 1: Cập nhật file `.csv`**
Mở file `.csv` bằng Excel hoặc trình soạn thảo, thêm một dòng mới:
- Các cột của trạm mẹ (`epass_name`, `google_name`, `osm_name`, `osm_id`, `latitude`, `longitude`): **Bắt buộc copy y hệt** từ các dòng cũ của trạm mẹ đó để hệ thống gom nhóm (group) bốt mới về đúng trạm.
- Cột `distance_to_origin`: Điền khoảng cách tương đối (hoặc để `0.0`).
- Các cột bốt con (`origin_osm_id`, `origin_osm_name`, `origin_osm_latitude`, `origin_osm_longitude`): **Điền thông tin và tọa độ mới** của cái bốt vừa được xây.

**Bước 2**:

Cấu hình giá cước cho tuyến đường vừa tạo ở Bước 2.
**"ticket"** có thể để [] rỗng nếu chưa có giá vé
```json

    {
        "refType": "NODE",
        "refId": "Đức Hòa",
        "tickets": [
            {
                "ticketType": 1,
                "ticketTypeName": "Vé lượt",
                "prices": [
                    {
                        "priceType": 1,
                        "priceTypeName": "Giá thường",
                        "feeType1": 29000,
                        "feeType2": 49000,
                        "feeType3": 59000,
                        "feeType4": 93000,
                        "feeType5": 172000
                    },
                    {
                        "priceType": 18,
                        "priceTypeName": "Giá miễn giảm loại 1"
                    },
                    {
                        "priceType": 19,
                        "priceTypeName": "Giá miễn giảm loại 2"
                    }
                ]
            },
            {
                "ticketType": 4,
                "ticketTypeName": "Vé tháng",
                "prices": [
                    {
                        "priceType": 1,
                        "priceTypeName": "Giá thường",
                        "feeType1": 707000,
                        "feeType2": 1178000,
                        "feeType3": 1414000,
                        "feeType4": 2239000,
                        "feeType5": 4124000
                    },
                    {
                        "priceType": 18,
                        "priceTypeName": "Giá miễn giảm loại 1"
                    },
                    {
                        "priceType": 19,
                        "priceTypeName": "Giá miễn giảm loại 2"
                    }
                ]
            },
            {
                "ticketType": 5,
                "ticketTypeName": "Vé quý",
                "prices": [
                    {
                        "priceType": 1,
                        "priceTypeName": "Giá thường",
                        "feeType1": 1909000,
                        "feeType2": 3181000,
                        "feeType3": 3817000,
                        "feeType4": 6044000,
                        "feeType5": 11134000
                    },
                    {
                        "priceType": 18,
                        "priceTypeName": "Giá miễn giảm loại 1"
                    },
                    {
                        "priceType": 19,
                        "priceTypeName": "Giá miễn giảm loại 2"
                    }
                ]
            }
        ],
        "osmId": "10196742008"
    }
```
**Quy tắc:**
- `"refType"`: `"NODE"`,
- `"refId"`: **Bắt buộc**. Là phần tử Tên Trạm ứng với tên Epass. được điền ở csv.
- `"tickets"`: **Bắt buộc nhưng có thể để [] rỗng**. Chứa thông tin mảng giá vé các loại xe.
- `"osmId"`: **Tùy chọn**. Có thể để rỗng "".

Sau đó chạy file **generate_ticket_submission.py** ở thư mục **gốc thư mục/routes/IndependentNode/**

## TUYẾN ĐƯỜNG: Với tuyến đường (gồm nhiều trạm) => thêm như bước dưới đây:

Lên epass tra cứu giá vé. mở **chrome tool for developer** -> mục **Network** để bắt API lấy json giá vé.

dữ liệu lấy giá vé lượt, vé tháng, vé quý. Lấy hết và vứt vào 1 file, ví dụ trong thư mục **routes/Cao_tốc_Pháp_Vân-Cầu_Giẽ/** , xem thư mục **new_epass** rồi paste dữ liệu thu thập từ API json vào file **gia_ve.json**.

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

## Cách chạy: QUAN TRỌNG 

Trong từng thư mục con của **thư mục gốc/routes/**, ví dụ **thư mục gốc/routes/Cao_tốc_Pháp_Vân-Cầu_Giẽ/**:

- chạy file **pre_01_update_gia_ve.py** để chuẩn hóa tên trạm- thêm tên trạm mới , loại bỏ trạm ảo và lưu vào `thư mục gốc/mapping.json`

- sau đó chạy **pre_02_build_graph.py**: nó sẽ lấy file **new_epass/gia_ve.json** -> tạo ra các file `nodes_new.json`, `edges_new.json`, `tickets_new.json`. Sau đó code `pre_02....` nó so sánh với `nodes.json`, `edges.json`, `tickets.json` (3 file json này là dữ liệu trạm, cạnh đồ thị nối 2 trạm, giá vé ứng với từng cạnh đồ thị nối 2 trạm). Rồi code **pre_02_build_graph.py** sẽ apply dữ liệu mới từ các file **.._new.json** vào các file **nodes.json**, **edges.json**, **tickets.json**. Đồng thời có print ra **khác biệt, thông báo dữ liệu nào được thêm, sửa , xóa**.

- Xem các file **.txt** trong thư mục **note/** để xem các file : **new_nodes.txt**, **new_edges.txt**, **new_tickets.txt**, **modified_...txt**, **removed_...txt** là lưu cái gì thay đổi, thêm mới, mất đi.

- Nếu còn lo bản json cũ sẽ bị mất thì xem lại thư mục **Cao_tốc_Pháp_Vân-Cầu_Giẽ/backup** để xem lại các file của dữ liệu phiên bản cũ. Các file json cũ sẽ được lưu vào thư mục **backup** 

## Sau khi chạy file pre_02_build_graph.py , ta cần:

- xem các file trong **note/** của từng tuyến đường. Xem **có nodes mới thì phải làm dưới đây**, còn trường hợp **thêm toll_booth của 1 trạm node epass_name đã tồn tại** cũng được xử lý ở dưới đây


# Hướng dẫn cập nhật dữ liệu cho Tuyến đường (gồm nhiều trạm):

**Tài liệu này hướng dẫn cách thêm hoặc sửa đổi dữ liệu trạm thu phí cho luồng xử lý Routing & Ticket Mapping.**

## Các file dữ liệu cốt lõi
Mọi thao tác cập nhật dữ liệu đều diễn ra trong thư mục của từng tuyến đường, ví dụ: `thư mục gốc/routes/Cao_tốc_Pháp_Vân-Cầu_Giẽ/`.
- `merged_Cao_tốc_Pháp_Vân-Cầu_Giẽ.csv`: Chứa tọa độ các bốt thu phí.
- `edges.json`: Khai báo danh sách các cặp trạm (đi - đến) cần tìm đường.
- `tickets.json`: Khai báo bảng giá vé giữa các cặp trạm.
- `nodes.json`: Khai báo vị trí các trạm chính (phục vụ hiển thị/frontend).

> **Lưu ý:** Hệ thống đã được tích hợp cơ chế tự động chuẩn hóa tiếng Việt (NFC) ở file `00_normalize_data.py`. Bạn có thể thoải mái sửa các file bằng tay mà không lo lỗi font chữ khi hệ thống xử lý.

---

## Case 1: Thêm một nhánh/bốt phụ vào Trạm Epass Name đã có sẵn
*Trường hợp áp dụng: Một nút giao (ví dụ Trạm Pháp vân) vừa xây thêm một bốt nhánh/trạm con mới nằm cách đó vài trăm mét. CÓ TOLL_BOOTH TRÊN OSM RỒI.*

**Bước 1: Cập nhật file `.csv`**
Mở file `.csv` bằng Excel hoặc trình soạn thảo, thêm một dòng mới:
- Các cột của trạm mẹ (`epass_name`, `google_name`, `osm_name`, `osm_id`, `latitude`, `longitude`): **Bắt buộc copy y hệt** từ các dòng cũ của trạm mẹ đó để hệ thống gom nhóm (group) bốt mới về đúng trạm.
- Cột `distance_to_origin`: Điền khoảng cách tương đối (hoặc để `0.0`).
- Các cột bốt con (`origin_osm_id`, `origin_osm_name`, `origin_osm_latitude`, `origin_osm_longitude`): **Điền thông tin và tọa độ mới** của cái bốt vừa được xây => **Bắt buộc phải điền**

**Bước 2:** Chỉ vậy là đủ chuyển thẳng tới phần **Giai đoạn Hướng dẫn chạy Script** bên dưới.

---

## Case 2: Thêm một Trạm ePass hoàn toàn mới (Vì code pre_02_build_graph.py đã có rồi, nên chỉ cần check mất file txt trong thư mục note/ để xem thêm mới, thay đổi, đã xóa)
*Trường hợp áp dụng: Mở rộng tuyến cao tốc, khai trương một nút giao/trạm thu phí mới hoàn toàn.*

### Case 2 - Bước 1: Thêm vào file `.csv`
**Phải tự tìm epass_name, google_name, tên trạm osm_name, osm_id, latitude, longitude trên mạng dựa theo tên epass**
Thêm dòng thông tin trạm mới vào file `.csv`. Hãy chú ý đặt tên `epass_name` thống nhất vì nó sẽ dùng làm khóa (key) để liên kết với các file JSON. Nếu trạm có nhiều bốt (nhánh), bạn tạo nhiều dòng với chung `epass_name` nhưng khác thông tin ở các cột `origin_*` giống như Case 1.

### Case 2 - Bước 2: Khai báo đoạn đường vào `edges.json` => ĐÃ CHẠY pre_02_build_graph.py rồi => MUỐN THÌ KHÔNG CẦN LÀM NỮA MÀ CHỈ CHECK LẠI THÔI
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

### Case 2 - Bước 3: Khai báo giá vé vào `tickets.json` => ĐÃ CHẠY build_graph.py rồi => MUỐN THÌ KHÔNG CẦN LÀM NỮA MÀ CHỈ CHECK LẠI THÔI.
Cấu hình giá cước cho tuyến đường vừa tạo ở Bước 2.
**"ticket"** có thể để [] rỗng nếu chưa có giá vé
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
- `"tickets"`: **Bắt buộc nhưng có thể để [] rỗng**. Chứa thông tin mảng giá vé các loại xe.
- `"osmId"`: **Tùy chọn**. Có thể để mảng rỗng `[]` hoặc xóa luôn key này cũng được (hệ thống tự động map theo tên trạm).

### Case 2 - Bước 4: Khai báo vào `nodes.json` => ĐÃ CHẠY build_graph.py rồi. => MUỐN THÌ KHÔNG CẦN LÀM NỮA MÀ CHỈ CHECK LẠI THÔI.
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

****

## Giai đoạn Hướng dẫn chạy Script (Build Pipeline)
Sau khi sửa tay xong dữ liệu CSV và JSON - hoặc `pre_02_build_grpah.py` chạy oke và check lại đúng. Cần chạy script để hệ thống download lại bản đồ đường đi ngắn nhất và compile ra file kết quả. (Đảm bảo Valhalla local đang chạy).

#### Đối với Windows
1. Mở thư mục tuyến đường (ví dụ: `routes/Mai_Sơn-Quốc_Lộ_45`).

2. Chạy file **`run_pipeline.bat`**.

3. Một cửa sổ đen (CMD) sẽ hiện lên. Script sẽ chạy lần lượt:
   - File `00_normalize_data.py`: Dọn dẹp lỗi font chữ tiếng Việt, tự lưu lại file JSON, CSV cho chuẩn.
   - Các file từ `01` đến `05` + `generate_ticket_submission`: Lọc ứng viên -> Download Routes -> Tìm đường ngắn nhất -> Map giá vé.

4. Đợi đến khi màn hình hiện `===== HOÀN THÀNH TẤT CẢ CÁC FILE =====`. Nhấn phím bất kỳ để tắt.

#### Đối với Linux / MacOS
1. Mở Terminal.
2. Dùng lệnh `cd` để trỏ vào thư mục tuyến đường.
4. Chạy script: `<tên tuyến đường>$ sh run_pipeline.sh`

**Thành quả:**
Kiểm tra lại thư mục, bạn sẽ thu được file **`ticket_submission.json`** chứa toàn bộ payload đã được routing chuẩn xác kèm giá vé, sẵn sàng gửi API lên server!


## Giai đoạn Gộp dữ liệu

Ra ngoài thư mục gốc và chạy các file :

- Chạy **merge_ticket.py**, sau đó chạy **verify_merge.py** nếu muốn check.
- Chạy **merge_ticket_restricted.py**, sau đó chạy **verify_merge_restricted.py** nếu muốn check.
- Chạy **process_final_tickets.py** và **process_final_tickets_restricted.py** cuối cùng.

=> Xem kết quả tại: **thư mục gốc/final_ticket_submission_restricted.json**