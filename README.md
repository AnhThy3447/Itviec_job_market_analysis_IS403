_IS403 - Phân tích dữ liệu kinh doanh_
# PHÂN TÍCH XU HƯỚNG TUYỂN DỤNG NGÀNH IT TẠI TP. HỒ CHÍ MINH VÀ HÀ NỘI

# Mục lục

- [1. Giới thiệu](#1-giới-thiệu)
- [2. Công nghệ & Công cụ](#2-công-nghệ--công-cụ)
- [3. Bộ dữ liệu](#3-bộ-dữ-liệu)
- [4. Hệ thống Dashboard & Mô hình dữ liệu](#4-hệ-thống-dashboard--mô-hình-dữ-liệu)
- [5. Kết quả khám phá & khai phá dữ liệu (EDA & Data Mining)](#5-kết-quả-khám-phá--khai-phá-dữ-liệu-eda--data-mining)
- [6. Thành viên](#6-thành-viên)

## 1. Giới thiệu
Dự án này tập trung phân tích và giải mã thị trường tuyển dụng Công nghệ thông tin (IT) tại hai trung tâm kinh tế lớn nhất Việt Nam là TP. Hồ Chí Minh và Hà Nội. Dữ liệu thực tế được thu thập trực tiếp từ nền tảng ITviec, qua quá trình làm sạch, chuẩn hóa, và mô hình hóa để khám phá các xu hướng kĩ năng cốt lõi, cơ cấu tuyển dụng và sự tác động của AI đến thị trường lao động hiện nay.

## 2. Công nghệ & Công cụ
- **Thu thập dữ liệu (Web Scraping):** Python, Selenium, BeautifulSoup.
- **Trích xuất & Xử lý (Data Extraction):** Triển khai Mô hình LLM Qwen/Qwen2.5-3B-Instruct để bóc tách dữ liệu văn bản.
- **Tích hợp dữ liệu (ETL):** Sử dụng SQL Server Integration Services (SSIS) xây dựng cấu trúc Star Schema.
- **Trực quan hóa (BI):** Microsoft Power BI.
- **Mô hình hóa (Machine Learning):** Ridge Regression, Random Forest, Extra Trees, LightGBM, XGBoost, CatBoost, Poisson,  Thuật toán Apriori.

## 3. Bộ dữ liệu
Hệ thống dữ liệu của dự án được thiết kế chuẩn hóa theo **Kiến trúc Medallion (Medallion Architecture)**, đảm bảo luồng dữ liệu (Data Pipeline) được xử lý qua từng lớp từ thô đến tinh, phục vụ hiệu quả cho cả hai mục tiêu: Trực quan hóa và Huấn luyện mô hình.

### Bronze Layer
Lớp này lưu trữ dữ liệu nguyên bản thu thập được từ quá trình Web Scraping, giữ nguyên trạng thái ban đầu để đảm bảo khả năng truy xuất lịch sử.
| Dataset | Mô tả |
|---|---|
| summary_crawled_12_04.csv | Dữ liệu tracking vòng đời. Ghi nhận thời điểm bài đăng xuất hiện lần đầu và lần cuối nhằm tính toán thời gian tồn tại của bài đăng trên thị trường. |

### Silver Layer
Lớp dữ liệu đã qua làm sạch, loại bỏ trùng lặp và được làm giàu (Enrichment).
| Dataset | Mô tả |
|---|---|
| df_clean_llm_enriched_kaggle.csv | Bộ dữ liệu chính sau pipeline xử lý bằng LLM (`Qwen/Qwen2.5-3B-Instruct`). Các trường văn bản tự do như mô tả công việc, yêu cầu và phúc lợi được chuẩn hóa thành dữ liệu có cấu trúc như kỹ năng, cấp bậc, kinh nghiệm,... Đây là dataset chính dùng cho EDA. |
| job_domain_group.xlsx | Ánh xạ các `domain_name` rời rạc về các `domain_group` (nhóm ngành) cấp cao hơn. |
| job_expertise_new_groups.xlsx | Chuẩn hóa các `job_expertise` cụ thể thành các `expertise_group` (nhóm chuyên môn) để phục vụ phân tích vĩ mô. |
 
### Gold Layer
Lớp dữ liệu cuối cùng, được tổng hợp và tối ưu hóa hoàn toàn để phục vụ trực tiếp cho các bài toán phân tích và học máy.
| Dataset | Mô tả |
|---|---|
| model_data.csv | Bộ dữ liệu chuyên biệt cho huấn luyện mô hình dự báo. Dữ liệu đã được tổng hợp (aggregated) theo chuỗi thời gian (tuần), xử lý độ thưa và khởi tạo thêm các biến phát sinh (Feature Engineering). |

## 4. Hệ thống Dashboard & Mô hình dữ liệu
Hệ thống được thiết kế để cung cấp cái nhìn đa chiều từ bức tranh tổng thể đến từng chi tiết kỹ thuật.

* **Trang Overview (Tổng quan):** Theo dõi các chỉ số KPI cốt lõi như Tổng số tin đăng, Tỷ lệ công việc liên quan đến AI (AI Job Rate), và cơ cấu hình thức làm việc (At office/Hybrid/Remote).
* **Trang Company (Doanh nghiệp):** - Phân tích chéo loại hình công ty theo khu vực địa lý.
  - **Tính năng Drill-down:** Biểu diễn dữ liệu theo cấp bậc: Ngành hoạt động → Loại hình → Quy mô → Tên công ty cụ thể.
* **Trang Skills (Kỹ năng):** - Lọc dữ liệu linh hoạt theo từng nhóm kỹ năng (Cloud, Database, Framework, Programming Language...).
  - Phân tích mối tương quan giữa kỹ năng cụ thể với nhóm nghề nghiệp (Job Expertise) và cấp bậc (Seniority).
<img width="1745" height="333" alt="image" src="https://github.com/user-attachments/assets/97cdc5b7-3a18-4280-9019-1e8adeb90d7f" />


## 5. Kết quả khám phá & khai phá dữ liệu (EDA & Data Mining)
Phần cốt lõi của dự án được chia làm hai giai đoạn: Phân tích Khám phá (EDA) trên 1,735 tin tuyển dụng và Khai phá dữ liệu (Data Mining) sử dụng thuật toán học máy.

<img width="1554" height="609" alt="image" src="https://github.com/user-attachments/assets/9a21bb86-f442-446b-8dc3-0d2d17de60c1" />


### 1. Bức tranh toàn cảnh & Đối sánh Không gian
* Thị trường IT vận hành theo một hệ thống đa lớp, trong đó loại hình doanh nghiệp là biến cấu trúc chi phối nhu cầu nhân lực.
* **Thành phố Hồ Chí Minh:** Linh hoạt hơn về hình thức làm việc, tập trung xây dựng và phát triển phần mềm sản phẩm với nhiều công ty đa quốc gia và các doanh nghiệp quy mô vừa/nhỏ (1-150 nhân sự).
* **Hà Nội:** Tập trung hơn vào các vai trò mang tính hệ thống và nền tảng với nhiều doanh nghiệp nội địa (Local) và các tập đoàn quy mô lớn (1000+ nhân sự).

### 2. Định vị Kỹ năng & Lõi Công nghệ
* **Lõi ngôn ngữ:** Python, Java và JavaScript là ba ngôn ngữ dẫn đầu, hình thành tầng lõi của thị trường.
* **Phân hóa theo cấp bậc:** Nhóm Fresher/Junior tập trung vào ngôn ngữ và framework; nhưng khi tiến lên cấp Senior/Lead/Manager, trọng tâm dịch chuyển rõ rệt sang kiến trúc, vận hành hệ thống và Cloud/DevOps.

### 3. Tác động của AI (Sự dịch chuyển của thị trường)
* **Hấp thụ vào lõi phần mềm:** AI không tạo ra một thị trường hoàn toàn tách biệt mà đang được "hấp thụ" trực tiếp vào lõi kỹ thuật hiện có. Vị trí AI/ML Engineer phổ biến, nhưng nhu cầu kỹ năng AI cũng đã lan sang các vai trò Backend, Fullstack
* **Doanh nghiệp dẫn dắt:** Nhu cầu tuyển dụng liên quan đến AI tập trung áp đảo tại các công ty "IT Product", vượt xa khối Outsourcing hay Consulting

### 4. Khai phá Luật kết hợp (Apriori Algorithm)
Sử dụng thuật toán Apriori (với `min_support_pct=0.02`, `lift_threshold=3`), mô hình đã khai phá thành công 82 cặp kỹ năng "bạn đồng hành", chỉ ra 3 quy luật thực tiễn:
* **Quy luật Cộng sinh:** Yêu cầu ngôn ngữ luôn kéo theo framework mạnh nhất của nó (VD: PHP đi kèm Laravel đạt chỉ số Lift 17.96).
* **Quy luật Kỹ năng thay thế:** Các công nghệ là đối thủ cạnh tranh lại thường xuyên xuất hiện chung (VD: TensorFlow và PyTorch có chỉ số Lift 24.83).
* **Quy luật Toàn diện:** Công nghệ không tồn tại độc lập. Ví dụ, hệ sinh thái DevOps yêu cầu liên kết chuỗi từ Terraform đến Ansible, Jenkins và Kubernetes.

### 5. Mô hình dự báo và thực nghiệm 
**Lưu ý về dữ liệu:** Do dữ liệu được thu thập trong ngắn hạn (28/01/2026 - 12/04/2026), kết quả dự báo hiện tại mang tính chất thực nghiệm. Mục tiêu chính là xây dựng hệ thống có khả năng thích ứng với dữ liệu lớn hơn trong tương lai.

**Chiến lược thực nghiệm**:
Nhóm thực hiện so sánh hai hướng tiếp cận để xử lý vấn đề dữ liệu thưa:
* **Hướng 1 (Chia để trị):** Tách biệt nhóm Top Skills (phổ biến) và Rare Skills (khan hiếm nhưng xuất hiện đều đặn theo từng tuần) để huấn luyện trên các họ mô hình chuyên biệt.
* **Hướng 2 (Tổng quát):** Huấn luyện trên toàn bộ tập dữ liệu.


**Kết quả hướng 1**
  ![](https://github.com/user-attachments/assets/3e0e2ba2-507f-4f65-94a6-0786f2e0a501)
**Kết quả hướng 2**
  ![](https://github.com/user-attachments/assets/cc375aac-5d6d-4535-b0b8-d3b70f723d23)
**So sánh kết quả hai hướng**
<img width="989" height="290" alt="image" src="https://github.com/user-attachments/assets/22cf3804-0781-4e07-9a3d-d0ed91c2d624" />


## 6. Thành viên
| Họ và tên              | MSSV       |
|------------------------|------------|
| Võ Ngọc Anh Thy        | 23521565   |
| Nguyễn Quý Phong       | 23521169   |
| Nguyễn Khánh Vân       | 23521772   |

