- Prompt 1
```
Tạo [số lượng câu hỏi] câu hỏi trắc nghiệm cho nội dung bên dưới
Mỗi câu hỏi có bốn phương án trả lời và chỉ có một đáp án đúng
Ví dụ kết quả trả về:
Câu hỏi 1: [Câu hỏi]
A: [Đáp án A]
B: [Đáp án B]
C: [Đáp án C]
D: [Đáp án D]

Nội dung:
===
[Nội dung cần tạo câu hỏi trắc nghiệm]
===
```
- Prompt 2
```
Bạn là một nhà văn và nhà phê bình văn học.
Hày phân tích đánh giá, và cải thiện  đoạn văn sau, nhưng vẫn giữ nguyên phong cách ban đầu.

Nội dung đoạn văn:
===
[Nội dung]
===

```

- Prompt 3
```
Dựa vào DANH SÁCH REVIEW bên dưới, hãy phân loại thành review tốt và xấu, tổng hợp và đếm số review.
Kết quả trả về theo định dạng sau:
===
Danh sách các review tốt ([số lượng review tốt]/[tổng số review]):
- [Nội dung review tốt 1]
- [Nội dung review tốt 2]
- [Nội dung review tốt 3]
...
Danh sách review xấu ([số lượng review xấu]/[tổng số review]):
- [Nội dung review xấu 1]
- [Nội dung review xấu 2]
...
===

DANH SÁCH REVIEW:
===
[Danh sách các review]
===
```

- Prompt 4
```
Bạn là một principal software engineer, hãy giúp tôi review, tìm và fix bug đoạn code be dưới, đồng thời thêm comment cho để giải thích cho các đoạn code phức tạp

code của tôi:
===
[Nội dung đoạn code]
===
```
- Prompt 5
```
Dựa vào danh sách các điểm du lịch bên dưới, giới thiệu các điểm tham quan, hoạt động, món ăn nổi tiếng, thời gian tham quan

Ví dụ output như sau:
===
1. [Địa danh 1]
[Giới thiệu về địa điểm này]
[Danh sách các món ăn nổi tiếng của địa danh này]
[Thời gian thăm quan hợp lý trong năm]
[Gợi ý lịch trình thăm quan trong ngày]
===

Danh sách các địa danh:
===
[Danh sách]
===
```

- Prompt 6
```
Từ NỘI DUNG SÁCH HOẶC TÊN SÁCH bên dưới, hãy giúp tôi tóm tắt nội dung cuốn sách và liệt kê các nhân vật xuất hiện

Ví dụ output như sau:
===
[Giới thiệu ngắn gọn, tổng quang về sách]
[Nội dung tóm tắt, liệt cách sự kiện quan trọng]
[Danh sách các nhân vật chính, khái quát vai trò]
[Danh sách các nhân vật phụ]
===

NỘI DUNG SÁCH HOẶC TÊN SÁCH:
===
[Nội dung]
===
```