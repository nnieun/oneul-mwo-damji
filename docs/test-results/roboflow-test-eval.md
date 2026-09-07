# Roboflow Test set 평가 결과

## sang-rqj4u/ozm-4-yolov8n-t1

### 혼동행렬 (행: 정답, 열: 예측)

| 정답 \ 예측 | apple | bread | carrot | egg | galic | l_onion | onion | raw_pork | shrimp | sliced_ham | (미검출) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| apple | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| bread | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| carrot | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| egg | 0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| galic | 0 | 0 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| l_onion | 0 | 0 | 0 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 0 |
| onion | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 |
| raw_pork | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 19 | 0 | 0 | 0 |
| shrimp | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 |
| sliced_ham | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | 0 |

### 클래스별 Precision / Recall

| 클래스 | Test 장수 | Precision | Recall |
|---|---|---|---|
| apple | 7 | 100% | 100% |
| bread | 7 | 100% | 100% |
| carrot | 3 | 100% | 100% |
| egg | 9 | 100% | 100% |
| galic | 6 | 100% | 100% |
| l_onion | 6 | 100% | 100% |
| onion | 10 | 100% | 100% |
| raw_pork | 19 | 100% | 100% |
| shrimp | 3 | 100% | 100% |
| sliced_ham | 8 | 100% | 100% |

## sang-rqj4u/ozm-7-yolov8n-t1

### 혼동행렬 (행: 정답, 열: 예측)

| 정답 \ 예측 | apple | bread | carrot | egg | galic | l_onion | onion | raw_pork | shrimp | sliced_ham | (미검출) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| apple | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| bread | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| carrot | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| egg | 0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| galic | 0 | 0 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| l_onion | 0 | 0 | 0 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 0 |
| onion | 0 | 0 | 0 | 0 | 2 | 0 | 6 | 1 | 0 | 1 | 0 |
| raw_pork | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 17 | 0 | 0 | 0 |
| shrimp | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 |
| sliced_ham | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 0 |

### 클래스별 Precision / Recall

| 클래스 | Test 장수 | Precision | Recall |
|---|---|---|---|
| apple | 7 | 100% | 100% |
| bread | 7 | 70% | 100% |
| carrot | 3 | 100% | 33% |
| egg | 9 | 90% | 100% |
| galic | 6 | 75% | 100% |
| l_onion | 6 | 100% | 100% |
| onion | 10 | 100% | 60% |
| raw_pork | 19 | 94% | 89% |
| shrimp | 3 | 100% | 100% |
| sliced_ham | 8 | 78% | 88% |
