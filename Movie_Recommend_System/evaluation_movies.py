# evaluate_performance.py
import sys
import os
from pathlib import Path

# Thêm đường dẫn project vào PYTHONPATH
current_dir = Path(__file__).parent.absolute()
sys.path.append(str(current_dir / "backend")) 
import json
import time
import pandas as pd
from datetime import datetime
from backend.app.services.top5movie_service import recommend_movies

def load_test_cases(file_path):
    """Đọc test cases từ file JSON"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Lỗi khi đọc file test cases: {str(e)}")
        return []

def calculate_metrics(recommended, expected):
    """Tính toán precision và recall"""
    relevant = len(set([m["title"] for m in recommended]) & set(expected))
    precision = relevant / len(recommended) if recommended else 0
    recall = relevant / len(expected) if expected else 0
    return precision, recall

def run_evaluation(test_cases):
    """Chạy đánh giá trên tất cả test cases"""
    results = []
    
    for idx, case in enumerate(test_cases):
        start_time = time.time()
        
        try:
            # Gọi logic recommendation
            recommendations = recommend_movies(case["input"])
            
            # Tính toán thời gian và metrics
            response_time = time.time() - start_time
            precision, recall = calculate_metrics(recommendations, case.get("expected_movies", []))
            
            results.append({
                "test_case": case["input"],
                "precision": round(precision, 2),
                "recall": round(recall, 2),
                "response_time": round(response_time, 2),
                "recommended": [m["title"] for m in recommendations],
                "expected": case.get("expected_movies", [])
            })
            
        except Exception as e:
            print(f"Lỗi với test case '{case['input']}': {str(e)}")
            results.append({
                "test_case": case["input"],
                "error": str(e)
            })
            
        # Progress reporting
        if (idx + 1) % 5 == 0:
            print(f"Đã xử lý {idx+1}/{len(test_cases)} test cases")
    
    return results

def generate_report(results):
    """Tạo báo cáo chi tiết"""
    # Tạo DataFrame
    df = pd.DataFrame(results)
    
    # Tính toán metrics tổng hợp
    summary = {
        "total_cases": len(results),
        "success_rate": len([r for r in results if "error" not in r]) / len(results),
        "avg_precision": df["precision"].mean(),
        "avg_recall": df["recall"].mean(),
        "avg_response_time": df["response_time"].mean()
    }
    
    # Xuất file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"evaluation_report_{timestamp}.csv"
    df.to_csv(report_filename, index=False)
    
    # In kết quả
    print("\n=== KẾT QUẢ ĐÁNH GIÁ ===")
    print(f"Tổng số test cases: {summary['total_cases']}")
    print(f"Tỷ lệ thành công: {summary['success_rate']:.1%}")
    print(f"Precision trung bình: {summary['avg_precision']:.2f}")
    print(f"Recall trung bình: {summary['avg_recall']:.2f}")
    print(f"Thời gian phản hồi TB: {summary['avg_response_time']:.2f}s")
    print(f"\nBáo cáo đã được lưu vào: {report_filename}")

if __name__ == "__main__":
    # Cấu hình
    TEST_CASE_PATH = "C:\\Users\\Admin\\Downloads\\test_cases (1).json"  # Cập nhật đường dẫn thực tế"
    
    print("🚀 Bắt đầu quá trình đánh giá hiệu năng...")
    
    # Thực hiện đánh giá
    test_cases = load_test_cases(TEST_CASE_PATH)
    
    if not test_cases:
        print("❌ Không thể đọc test cases. Vui lòng kiểm tra file và định dạng.")
        exit(1)
        
    results = run_evaluation(test_cases)
    generate_report(results)
    
    print("✅ Đánh giá hoàn tất!")