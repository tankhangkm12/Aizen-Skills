# Chu Trình Phát Triển Toàn Trình Dự Án (Aizen Full Studio Workflow)

Quy trình `aizen-full` điều phối nhịp nhàng giữa **Plugin Design** và **Plugin Code**, đảm bảo sản phẩm hoàn thiện phản ánh 100% bản vẽ kiến trúc và thiết kế giao diện Canvas.

```mermaid
graph TD
    subgraph DiscoveryAndDesign["1. Khảo Sát & Thiết Kế (aizen-design)"]
        D1[Ý Tưởng & SRS] --> D2[Kiến Trúc Archify HLD/LLD]
        D2 --> D3[Mô Hình CSDL & API Contracts]
        D1 --> D4[Thiết Kế Canvas Penpot / Taste]
    end

    subgraph Implementation["2. Lập Trình & Kiểm Thử (aizen-code)"]
        C1[Lập Kế Hoạch Micro-modular 1-3 files] --> C2[Đóng Băng Acceptance Test]
        C2 --> C3[Lập Trình Go Backend & React Frontend]
        C3 --> C4[Kiểm Thử Trình Duyệt Thật Playwright E2E]
        C4 --> C5[Phản Biện Độc Lập Adversarial Review]
    end

    subgraph Deployment["3. Đóng Gói & Triển Khai"]
        O1[Hạ Tầng Docker & K8s Manifests] --> O2[Git Pre-Push Guard Check]
        O2 --> O3[Mở Pull Request Bàn Giao]
    end

    D3 --> C1
    D4 --> C1
    C5 --> O1
```

---

## 1. Pha Khởi Tạo & Thiết Kế (Design Stage)
- Điều phối viên kích hoạt các chuyên gia của `aizen-design`:
  - `system-architect` trực quan hóa sơ đồ HLD/LLD bằng `archify`.
  - `uiux-designer` dựng giao diện, components và design tokens trực tiếp trên Canvas `penpot`.
  - `database-architect` hoàn tất file `docs/data/ddl.sql` và bảng mã lỗi API.

## 2. Pha Hiện Thực Hóa Siêu Nhỏ (Micro-modular Coding Stage)
- Điều phối viên chuyển tiếp thông số sang `aizen-code`:
  - `task-planner` chia nhỏ yêu cầu thành các micro-modules (tối đa 1–3 file).
  - Lập trình viên Backend và Frontend xây dựng logic theo ranh giới write-set độc lập.
  - Sử dụng **Playwright MCP** để đối chiếu giao diện chạy thật trên `localhost` với canvas Penpot.
  - Chuyên gia `adversarial-reviewer` phản biện độc lập, yêu cầu dẫn chứng `path:line` cụ thể.

## 3. Pha Nghiệm Thu & Đẩy Mã Nguồn (Delivery Stage)
- Chuyên gia `devops-engineer` hoàn tất kịch bản CI/CD và Dockerfile.
- Chốt chặn `.git/hooks/pre-push` xác nhận toàn bộ bằng chứng kiểm thử đạt chuẩn `PASS` trước khi cho phép đẩy code lên GitHub.
