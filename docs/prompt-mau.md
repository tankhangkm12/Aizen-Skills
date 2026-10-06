# Prompt mẫu

Copy, thay phần `<…>`, xoá dòng không cần. Dòng nào bạn chưa biết thì bỏ trống — agent tự đo những gì đo được,
chỉ hỏi bạn về lựa chọn và rủi ro. Cách dùng chung: [huong-dan-su-dung.md](huong-dan-su-dung.md).

## aizen-build — tính năng mới

```text
/aizen-build
Task: <MÃ-TASK, vd SHOP-42>
Tên nghiệp vụ: <2–4 từ, vd checkout-coupon — thành tên nhánh feature/checkout-coupon>
Mục tiêu: <một câu kiểm chứng được>
Tiêu chí xong:
- <AC-1: khi … thì …>
- <AC-2: lỗi … thì trả … / hiển thị …>
- <số liệu nếu có: p95 < 300 ms, tối đa 50 item, …>
Phạm vi: làm <…>; KHÔNG làm <…>
Ràng buộc: <API/schema không đổi · không thêm thư viện · theo pattern của <module mẫu>>
Tài liệu / chỗ cần nhìn: <đường dẫn file, link thiết kế, ticket>
Branch gốc: <develop>
Cho phép sẵn (A3): <cài graphify · chạy Postgres local bằng docker compose · npm install>
Hỏi tôi xác nhận từng module trước khi code; sau khi tôi approve thì làm hết không hỏi thêm.
```

## Nhờ soạn prompt (phỏng vấn trước)

```text
/aizen-prompt-architect
Tôi muốn: <ý tưởng / lỗi / thay đổi, kể bằng lời thường>
Dành cho: <aizen-build | aizen-init>  · Ticket nếu có: <TET-12>
```

Trên AI web: dán [aizen-web-kit.md](aizen-web-kit.md) trước, rồi gửi phần "Tôi muốn: …".

## aizen-build — sửa bug

```text
/aizen-build
Task: <BUG-123>
Lỗi: mong đợi <…>, thực tế <…>
Tái hiện: <các bước / request mẫu / dữ liệu>  · Môi trường: <local/staging, trình duyệt, version>
Bằng chứng: <log, stack trace, ảnh chụp — dán ≤ 30 dòng>
Bắt đầu từ: <khi nào / sau commit/PR nào, nếu biết>
Phạm vi: chỉ sửa nguyên nhân gốc, kèm test hồi quy; không refactor xung quanh.
Cho phép sẵn (A3): <…>
```

## aizen-build — refactor

```text
/aizen-build
Task: <REF-7>
Mục tiêu: <tách / đổi tên / gom … để …>  · Hành vi bên ngoài: KHÔNG đổi
Phạm vi: <thư mục / module>  · Ngoài phạm vi: <…>
Chốt hành vi bằng: <test hiện có / thêm test trước khi chuyển code>
```

## aizen-build — từ ý tưởng tới PR

```text
/aizen-build
Task: <NEW-1>
Ý tưởng: <2–5 câu: ai dùng, vấn đề gì, kết quả mong muốn>
Người dùng và quy mô: <ai, bao nhiêu, thiết bị>
Phải có ở bản đầu: <…>  · Để sau: <…>
Công nghệ: <stack bắt buộc, hoặc "đề xuất giúp tôi">
Đi qua yêu cầu và thiết kế trước (STAGE discover/design), hỏi tôi từng phần, rồi mới lập plan.
```

## aizen-build — tiếp tục / kiểm tra

```text
/aizen-build tiếp tục task <MÃ-TASK>.
/aizen-build trạng thái task <MÃ-TASK>?
```

## Trả lời khi agent xác nhận từng phần

```text
theo đề xuất
module <id>: chọn B, thêm <…>, bỏ <…>
phạm vi: thêm AC-3 <…>
approve plan <MÃ-TASK>
```

## aizen-build — review code

```text
/aizen-build review
Review: <PR #45 | branch feature/x so với develop | git diff main...HEAD>
Thay đổi này để: <mục tiêu>
Phần lõi / rủi ro cao: <auth, migration, …>
Trả về: findings theo mức độ, mỗi cái có file:line và kịch bản lỗi.
```

## aizen-build — chỉ thiết kế bảng

```text
/aizen-build thiết kế (chưa code)
Engine: <MySQL 8.0>
Thực thể: <Order(…), OrderItem(…)> · Quan hệ: <1 Order – n OrderItem>
Quy mô: <rows/tháng, giữ bao lâu>  · Truy vấn chính: <lọc theo user + thời gian, …>
Quy ước team (nếu có): <audit columns, soft delete, …>
Trả về: tài liệu database + DDL có COMMENT, index và lý do.
```

## aizen-build — CI/CD

```text
/aizen-build dựng pipeline
Repo: <đường dẫn / URL>  · CI: <GitHub Actions>  · Deploy tới: <VPS / k8s / …>
Registry: <Docker Hub user/repo>  · Branch → môi trường: <main → prod, develop → staging>
Secret đã có (chỉ tên): <DOCKERHUB_TOKEN, SSH_KEY>
```

## Khởi tạo dự án backend

```text
/aizen-init
Repo: <https://github.com/team/project.git | git@gitlab.com:team/project.git>
Tài liệu dự án: <./docs/SRS.md, ./docs/architecture.md | link Notion>
Stack / infra (nếu tài liệu chưa ghi): <NestJS + PostgreSQL + Redis>
Auth: <JWT access/refresh + RBAC>
Push lên remote: <hỏi tôi mỗi lần>
```

## Skill

```text
/aizen-skill-creator
Skill mới: <tên-gạch-ngang> — giúp agent <làm gì, cho ai>
Phải kích hoạt khi: 1) "<prompt thật>" 2) "<…>" 3) "<…>"
Không kích hoạt khi: "<…>" (để cho skill <tên skill có sẵn>)
Đầu ra: <file nào, định dạng gì / câu trả lời gồm những phần nào>
Các bước: <nếu đã có quy trình: 1 … 2 … 3 …>
Phần nên viết thành script: <việc lặp lại, cần kết quả giống nhau>
Phải hỏi tôi trước khi: <ghi file / gọi API / cài đặt / push>
Tài liệu tham khảo: <link, file>
```

```text
/aizen-skill-creator
Cải thiện skill <tên>: <vấn đề gặp phải, kèm prompt đã dùng và kết quả sai>
Mong muốn: <hành vi đúng>  · Giữ nguyên: <…>
```

```text
/aizen-skill-importer
Nguồn: https://github.com/<owner>/<repo>/tree/<branch>/<đường-dẫn-tới-thư-mục-skill>   (hoặc đường dẫn thư mục skill trên máy)
Tên đích: <tên-gạch-ngang>
Muốn đổi: <quy trình / luật / công cụ / định dạng đầu ra / ngôn ngữ trigger>
Task mẫu cho A/B test: <một yêu cầu thật, vd "đọc file X.pdf và tóm tắt theo mẫu Y">
```

```text
/aizen-skill-importer vendor
Nguồn: https://github.com/<owner>/<repo>  (thư mục skill: <đường-dẫn>)
Đưa vào pack: <aizen-database / aizen-backend / …>  · Topic: <db / backend / …>
Chỉ giữ: <các phần giá trị cao>  · Bỏ: <phần quảng cáo / không thuộc stack>
```

```text
/aizen-skill-eval
Skill: <tên>  · Đạt khi: <…>
Nên kích hoạt: <2–3 prompt>  · Không nên kích hoạt: <2–3 prompt>
```

## Học công nghệ / video

```text
/aizen-tech-learning
Công nghệ: <tên + version>
Workload tham chiếu: <một thao tác cụ thể, vd. "cache 100k GET/s, value 1KB, 1 node">
Muốn hiểu: vì sao nó hiệu quả trong workload này, đi xuống tới kernel/network; khi nào nó hết hiệu quả
So sánh kiến trúc với: <công nghệ A>, <công nghệ B>
Ghi vào Notion dưới trang: <trang cha>  · File md: ./tech-tree/<tên>.md
```

```text
/aizen-video-to-skill
Video: <link YouTube hoặc đường dẫn file>
Skill mới giúp agent: <…>  · Tên skill: <…>  · Ngôn ngữ: <vi/en>
```
