"""Evaluate one or more Roboflow hosted models against a local Test split export.

Roboflow's training UI only reports metrics on the Validation split. This script
calls the same hosted inference API the app uses (see backend/app/recognition.py)
against a Test split you export yourself, and builds a confusion matrix + per-class
precision/recall from the results, so results are Test-set based and match what the
app actually calls in production.

How to get the Test split export from Roboflow:
    1. Open the project on Roboflow -> "Versions" in the left sidebar.
    2. Open the version you trained the model from.
    3. Click "Download Dataset" (or "Export Dataset").
    4. Format: choose "YOLOv8".
    5. Save the zip anywhere (it does not need to be unzipped -- this script reads
       straight from the .zip). The export contains data.yaml and train/valid/test
       subfolders, each with images/ and labels/.

Different model versions were usually trained on different dataset versions, so
each model should be checked against its OWN Test split export, not a shared one.
Use --dataset KEY=PATH (repeatable) for that, where KEY is either a backend/.env
variable name (its value is used as the model ID) or a literal model ID:

    backend\\.venv\\Scripts\\python.exe scripts/evaluate_roboflow_models.py ^
        --dataset ROBOFLOW_MODEL_ID=backend/model/two_model.zip ^
        --dataset ROBOFLOW_MODEL_ID_2=backend/model/last_model.zip

If every model can be checked against the same Test split, pass that folder or zip
as a single positional argument instead:

    backend\\.venv\\Scripts\\python.exe scripts/evaluate_roboflow_models.py <exported_dataset.zip>

    # Evaluate specific model IDs instead of everything in backend/.env:
    backend\\.venv\\Scripts\\python.exe scripts/evaluate_roboflow_models.py <exported_dataset.zip> --model-id sang-rqj4u/ozm-4-yolov8n-t1

By default this reads every ROBOFLOW_MODEL_ID* variable and ROBOFLOW_API_KEY from
backend/.env, so with both ROBOFLOW_MODEL_ID and ROBOFLOW_MODEL_ID_2 set there it
evaluates both models in one run and writes one report with a section per model.

This makes one hosted-inference API call per Test image per model (Test set is
small, ~78 images, so this is normally a couple of minutes per model). It assumes
one object per image, matching this project's dataset; if a label file has more
than one box it uses the first and prints a warning.
"""
import argparse
import base64
import json
import sys
import zipfile
from collections import Counter
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
IMAGE_SUFFIXES = {'.jpg', '.jpeg', '.png'}


def load_env(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not path.exists():
        return env
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, _, value = line.partition('=')
        env[key.strip()] = value.strip()
    return env


def resolve_dataset_root(path: Path) -> Path:
    """Extract a Roboflow export .zip once (cached next to it) and return the extracted folder; pass directories through."""
    if path.is_dir():
        return path
    if not path.is_file() or path.suffix.lower() != '.zip':
        raise SystemExit(f'{path}는 폴더도 .zip 파일도 아닙니다.')
    extracted = path.parent / f'{path.stem}_extracted'
    if not (extracted / 'data.yaml').exists():
        print(f'{path.name} 압축 해제 중... -> {extracted}')
        with zipfile.ZipFile(path) as archive:
            archive.extractall(extracted)
    return extracted


def find_test_dir(path: Path) -> tuple[Path | None, Path]:
    """Accept either the export root (with a test/ subfolder) or the test/ folder itself."""
    path = resolve_dataset_root(path)
    if (path / 'images').is_dir() and (path / 'labels').is_dir():
        return (path.parent / 'data.yaml' if (path.parent / 'data.yaml').exists() else None), path
    if (path / 'test').is_dir():
        return path / 'data.yaml', path / 'test'
    raise SystemExit(f'{path} 아래에서 test/images, test/labels 폴더를 찾지 못했습니다. Roboflow에서 YOLOv8 포맷으로 export한 폴더를 지정해 주세요.')


def load_class_names(data_yaml: Path | None, explicit: str | None) -> list[str]:
    if explicit:
        return [name.strip() for name in explicit.split(',') if name.strip()]
    if not data_yaml or not data_yaml.exists():
        raise SystemExit('data.yaml을 찾지 못했습니다. --classes "apple,bread,..." 로 직접 지정해 주세요.')
    names: list[str] = []
    in_names = False
    for line in data_yaml.read_text(encoding='utf-8').splitlines():
        stripped = line.strip()
        if stripped.startswith('names:'):
            rest = stripped.split(':', 1)[1].strip()
            if rest.startswith('['):
                return [n.strip().strip("'\"") for n in rest.strip('[]').split(',') if n.strip()]
            in_names = True
            continue
        if in_names:
            if stripped.startswith('-'):
                names.append(stripped[1:].strip().strip("'\""))
            elif stripped:
                break
    if not names:
        raise SystemExit(f'{data_yaml}에서 클래스 이름을 읽지 못했습니다. --classes로 직접 지정해 주세요.')
    return names


def ground_truth_label(label_path: Path, class_names: list[str]) -> str | None:
    if not label_path.exists():
        return None
    lines = [line for line in label_path.read_text(encoding='utf-8').splitlines() if line.strip()]
    if not lines:
        return None
    if len(lines) > 1:
        print(f'경고: {label_path.name}에 박스가 {len(lines)}개 있어 첫 번째만 정답으로 사용합니다.', file=sys.stderr)
    class_id = int(lines[0].split()[0])
    return class_names[class_id]


def infer_top_label(client: httpx.Client, model_id: str, api_key: str, jpeg: bytes) -> str | None:
    response = client.post(
        f'https://detect.roboflow.com/{model_id}',
        params={'api_key': api_key, 'confidence': 0},
        content=base64.b64encode(jpeg),
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        timeout=30,
    )
    response.raise_for_status()
    predictions = response.json().get('predictions', [])
    if not predictions:
        return None
    return max(predictions, key=lambda p: p['confidence'])['class']


# The hosted API sometimes returns a human-readable display name instead of the
# short class slug used in data.yaml/exported labels (e.g. this project's l_onion
# class comes back as "large green onion" from one model version). Map known
# alternate spellings back to the canonical class name so they score correctly;
# extend at the CLI with --alias 'canonical=alt1,alt2'.
DEFAULT_ALIASES: dict[str, list[str]] = {
    'l_onion': ['large_green_onion', 'large green onion'],
}


def build_alias_lookup(class_names: list[str], extra: list[str] | None) -> dict[str, str]:
    lookup: dict[str, str] = {}
    for canonical, alternates in DEFAULT_ALIASES.items():
        if canonical in class_names:
            for alternate in alternates:
                lookup[alternate.strip().lower()] = canonical
    for entry in extra or []:
        canonical, _, alternates = entry.partition('=')
        for alternate in alternates.split(','):
            if alternate.strip():
                lookup[alternate.strip().lower()] = canonical.strip()
    return lookup


def resolve_predicted_label(predicted: str | None, class_names: list[str], alias_lookup: dict[str, str]) -> str | None:
    if predicted is None or predicted in class_names:
        return predicted
    return alias_lookup.get(predicted.strip().lower(), predicted)


def evaluate(model_id: str, api_key: str, test_dir: Path, class_names: list[str], alias_lookup: dict[str, str]) -> list[tuple[str, str | None]]:
    images_dir, labels_dir = test_dir / 'images', test_dir / 'labels'
    image_paths = sorted(p for p in images_dir.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES)
    pairs: list[tuple[str, str | None]] = []
    with httpx.Client() as client:
        for i, image_path in enumerate(image_paths, 1):
            truth = ground_truth_label(labels_dir / f'{image_path.stem}.txt', class_names)
            if truth is None:
                continue
            raw_predicted = infer_top_label(client, model_id, api_key, image_path.read_bytes())
            predicted = resolve_predicted_label(raw_predicted, class_names, alias_lookup)
            pairs.append((truth, predicted))
            note = f' (모델 원문: {raw_predicted})' if predicted != raw_predicted else ''
            print(f'[{model_id}] {i}/{len(image_paths)} {image_path.name}: 정답={truth} 예측={predicted}{note}')
    return pairs


NO_DETECTION = '(미검출)'


def build_confusion_matrix(pairs: list[tuple[str, str | None]], class_names: list[str]):
    matrix = {truth: Counter() for truth in class_names}
    # Anything the model predicted that isn't a known class name and wasn't resolved
    # by an alias gets its own column instead of silently collapsing into 0s, so an
    # unexpected label string is visible in the report rather than hidden.
    unexpected: list[str] = []
    for truth, predicted in pairs:
        key = predicted or NO_DETECTION
        matrix[truth][key] += 1
        if key not in class_names and key != NO_DETECTION and key not in unexpected:
            unexpected.append(key)
    labels = [*class_names, *sorted(unexpected), NO_DETECTION]
    return matrix, labels


def per_class_metrics(matrix, class_names: list[str], labels: list[str]):
    rows = []
    for label in class_names:
        support = sum(matrix[label].values())
        true_positive = matrix[label][label]
        predicted_as_label = sum(matrix[truth][label] for truth in class_names)
        precision = true_positive / predicted_as_label if predicted_as_label else None
        recall = true_positive / support if support else None
        rows.append((label, support, precision, recall))
    return rows


def format_percent(value: float | None) -> str:
    return f'{value:.0%}' if value is not None else 'N/A'


def format_report(model_id: str, matrix, class_names: list[str], labels: list[str], rows) -> str:
    lines = [f'## {model_id}', '', '### 혼동행렬 (행: 정답, 열: 예측)', '']
    lines.append('| 정답 \\ 예측 | ' + ' | '.join(labels) + ' |')
    lines.append('|' + '---|' * (len(labels) + 1))
    for truth in class_names:
        lines.append('| ' + truth + ' | ' + ' | '.join(str(matrix[truth][pred]) for pred in labels) + ' |')
    lines += ['', '### 클래스별 Precision / Recall', '', '| 클래스 | Test 장수 | Precision | Recall |', '|---|---|---|---|']
    for label, support, precision, recall in rows:
        lines.append(f'| {label} | {support} | {format_percent(precision)} | {format_percent(recall)} |')
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('test_dataset_dir', type=Path, nargs='?', help='모든 모델에 같이 쓸 데이터셋 폴더 또는 .zip. --dataset을 쓰면 생략')
    parser.add_argument('--dataset', action='append', dest='datasets', metavar='KEY=PATH',
                         help='모델별 데이터셋 지정. KEY는 backend/.env 변수명(예: ROBOFLOW_MODEL_ID_2) 또는 모델 ID 문자열. 여러 번 지정 가능')
    parser.add_argument('--model-id', action='append', dest='model_ids', help='test_dataset_dir와 함께 쓰는 모델 ID 목록. 생략 시 backend/.env의 ROBOFLOW_MODEL_ID*를 모두 사용')
    parser.add_argument('--api-key', help='생략 시 backend/.env의 ROBOFLOW_API_KEY 사용')
    parser.add_argument('--classes', help='쉼표로 구분한 클래스 이름. 생략 시 각 데이터셋의 data.yaml에서 읽음')
    parser.add_argument('--alias', action='append', dest='aliases', metavar='CANONICAL=ALT1,ALT2',
                         help='모델이 다른 이름으로 반환하는 클래스를 정답 라벨로 매핑. 예: l_onion=large_green_onion,"large green onion". l_onion 관련 별칭은 기본으로 이미 포함됨')
    parser.add_argument('--out', type=Path, default=ROOT / 'docs' / 'test-results' / 'roboflow-test-eval.md')
    parser.add_argument('--json-out', type=Path, default=ROOT / 'docs' / 'test-results' / 'roboflow-test-eval.json',
                         help='시각화 노트북(roboflow-test-eval.ipynb)이 읽는 구조화된 결과 파일')
    args = parser.parse_args()

    env = load_env(ROOT / 'backend' / '.env')
    api_key = args.api_key or env.get('ROBOFLOW_API_KEY')
    if not api_key:
        raise SystemExit('ROBOFLOW_API_KEY가 없습니다. --api-key로 지정하거나 backend/.env에 설정하세요.')

    # (model_id, dataset_path) pairs to evaluate.
    jobs: list[tuple[str, Path]] = []
    if args.datasets:
        for entry in args.datasets:
            if '=' not in entry:
                raise SystemExit(f'--dataset {entry} 형식이 잘못됐습니다. KEY=PATH 형태로 지정해 주세요.')
            key, _, raw_path = entry.partition('=')
            model_id = env.get(key, key)
            jobs.append((model_id, Path(raw_path)))
    if args.test_dataset_dir:
        model_ids = args.model_ids or [value for key, value in env.items() if key.startswith('ROBOFLOW_MODEL_ID') and value]
        if not model_ids:
            raise SystemExit('평가할 모델 ID가 없습니다. --model-id로 지정하거나 backend/.env에 ROBOFLOW_MODEL_ID를 설정하세요.')
        jobs += [(model_id, args.test_dataset_dir) for model_id in model_ids]
    if not jobs:
        raise SystemExit('평가할 데이터셋이 없습니다. --dataset KEY=PATH를 쓰거나, 데이터셋 폴더/zip을 위치 인자로 지정해 주세요.')

    sections = []
    json_models = []
    for model_id, dataset_path in jobs:
        data_yaml, test_dir = find_test_dir(dataset_path)
        class_names = load_class_names(data_yaml, args.classes)
        alias_lookup = build_alias_lookup(class_names, args.aliases)
        pairs = evaluate(model_id, api_key, test_dir, class_names, alias_lookup)
        matrix, labels = build_confusion_matrix(pairs, class_names)
        rows = per_class_metrics(matrix, class_names, labels)
        sections.append(format_report(model_id, matrix, class_names, labels, rows))
        json_models.append({
            'model_id': model_id,
            'class_names': class_names,
            'labels': labels,
            'matrix': {truth: {pred: matrix[truth][pred] for pred in labels} for truth in class_names},
            'metrics': [
                {'label': label, 'support': support, 'precision': precision, 'recall': recall}
                for label, support, precision, recall in rows
            ],
        })

    report = '# Roboflow Test set 평가 결과\n\n' + '\n\n'.join(sections) + '\n'
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding='utf-8')
    print(f'\n결과 저장: {args.out}')

    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps({'models': json_models}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'구조화된 결과 저장(노트북용): {args.json_out}')


if __name__ == '__main__':
    main()
