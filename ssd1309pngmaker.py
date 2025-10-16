import os
import argparse
from pathlib import Path
from PIL import Image
from tqdm import tqdm

# ==== デフォルト設定 ====
DEFAULT_RESAMPLE = "LANCZOS"
DEFAULT_MODE = "letterbox"  # or "stretch"
DEFAULT_DITHER = "FLOYDSTEINBERG"  # or "NONE"
DEFAULT_THRESHOLD = 128
DEFAULT_BGCOLOR = "black"  # or "white"
TARGET_SIZE = (128, 64)
BASE_OUTPUT_DIR = Path("output")

RESAMPLE_MAP = {
    "NEAREST": Image.NEAREST,
    "BILINEAR": Image.BILINEAR,
    "BICUBIC": Image.BICUBIC,
    "LANCZOS": Image.LANCZOS,
}

DITHER_MAP = {
    "NONE": Image.NONE,
    "FLOYDSTEINBERG": Image.FLOYDSTEINBERG,
}

COLOR_MAP = {
    "black": 0,
    "white": 255,
}


def get_unique_output_dir(base_dir: Path) -> Path:
    """output, output-02, output-03...のように枝番をつけてディレクトリを生成"""
    if not base_dir.exists():
        base_dir.mkdir()
        return base_dir

    idx = 2
    while True:
        new_dir = Path(f"{base_dir}-{idx:02d}")
        if not new_dir.exists():
            new_dir.mkdir()
            return new_dir
        idx += 1


def letterbox(img: Image.Image, target_size, resample, bgcolor=0):
    """長辺合わせ＋余白塗り"""
    target_w, target_h = target_size
    ratio = min(target_w / img.width, target_h / img.height)
    new_w = int(img.width * ratio)
    new_h = int(img.height * ratio)
    img = img.resize((new_w, new_h), resample)

    new_img = Image.new("L", target_size, bgcolor)
    paste_x = (target_w - new_w) // 2
    paste_y = (target_h - new_h) // 2
    new_img.paste(img, (paste_x, paste_y))
    return new_img


def convert_image(input_path: Path, output_dir: Path, args, stats):
    try:
        with Image.open(input_path) as img:
            if img.format == "GIF":
                img.seek(0)

            w, h = img.size
            if w < TARGET_SIZE[0] or h < TARGET_SIZE[1]:
                stats["skip"] += 1
                return

            img = img.convert("L")

            # リサイズ
            if args.mode == "stretch":
                img = img.resize(TARGET_SIZE, RESAMPLE_MAP[args.resample])
            else:
                img = letterbox(img, TARGET_SIZE, RESAMPLE_MAP[args.resample],
                                bgcolor=COLOR_MAP[args.bgcolor])

            # 2値化
            if args.dither == "NONE":
                img = img.point(lambda x: 255 if x > args.threshold else 0, mode="1")
            else:
                img = img.convert("1", dither=DITHER_MAP[args.dither])

            out_path = output_dir / f"{input_path.stem}_128x64_bw.png"
            img.save(out_path, format="PNG")
            stats["success"] += 1

    except Exception as e:
        stats["fail"] += 1
        print(f"⚠️ {input_path.name} の処理に失敗: {e}")


def main():
    parser = argparse.ArgumentParser(description="128x64 1bit image converter")
    parser.add_argument("--input", required=True, help="入力ディレクトリ")
    parser.add_argument("--mode", choices=["letterbox", "stretch"], default=DEFAULT_MODE)
    parser.add_argument("--resample", choices=RESAMPLE_MAP.keys(), default=DEFAULT_RESAMPLE)
    parser.add_argument("--dither", choices=DITHER_MAP.keys(), default=DEFAULT_DITHER)
    parser.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD)
    parser.add_argument("--bgcolor", choices=COLOR_MAP.keys(), default=DEFAULT_BGCOLOR)
    args = parser.parse_args()

    input_dir = Path(args.input)
    if not input_dir.exists():
        print(f"❌ 入力ディレクトリが見つかりません: {input_dir}")
        return

    # 出力先のユニークなディレクトリを生成
    output_dir = get_unique_output_dir(BASE_OUTPUT_DIR)
    print(f"📁 出力先: {output_dir.resolve()}")

    # ファイルリスト収集
    file_list = []
    for ext in ("*.png", "*.jpg", "*.gif"):
        file_list.extend(input_dir.glob(ext))

    if not file_list:
        print("⚠️ 対象ファイルが見つかりません。")
        return

    stats = {"success": 0, "fail": 0, "skip": 0}

    # tqdm で進捗バー表示
    for f in tqdm(file_list, desc="処理中", unit="file"):
        convert_image(f, output_dir, args, stats)

    total = len(file_list)
    print("\n✅ 処理完了")
    print(f"   総ファイル数: {total}")
    print(f"   成功:       {stats['success']}")
    print(f"   スキップ:   {stats['skip']}")
    print(f"   失敗:       {stats['fail']}")


if __name__ == "__main__":
    main()
