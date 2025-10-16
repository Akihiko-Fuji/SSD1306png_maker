# SSD1306/SSD1309 PNG Maker

128×64ドットのSSD1306/SSD1309向けに画像を最適化するPython製ツールです。複数形式での出力、リサイズモード、ディザリングや反転などのパラメータを自由に調整できます。

## 特長

- 128×64サイズへの自動リサイズ（縦横比維持のレターボックス／ストレッチ）
- FLOYD-STEINBERGディザ・しきい値指定による2値化
- 白／黒背景の余白塗り、白黒反転に対応
- 小さい画像の拡大処理を任意で許可
- PNG／RAWバイト列／Cヘッダーファイルの複数形式を同時に出力
- 入力ディレクトリを再帰的に探索し、一括変換

## 必要環境

- Python 3.9以降
- [Pillow](https://python-pillow.org/)
- [tqdm](https://tqdm.github.io/)

```
pip install -r requirements.txt
```

`requirements.txt`が無い場合は、以下のように個別インストールしてください。

```
pip install pillow tqdm
```

## 使い方

```
python ssd1309pngmaker.py --input <入力ディレクトリ> [オプション]
```

主なオプション:

| オプション | 説明 |
| --- | --- |
| `--output PATH` | 出力先ディレクトリ。省略時は`output`配下に枝番付きで作成 |
| `--recursive` | 入力ディレクトリを再帰的に探索 |
| `--mode {letterbox,stretch}` | 縦横比維持か全面ストレッチかを選択 |
| `--resample {NEAREST,BILINEAR,BICUBIC,LANCZOS}` | リサンプリング方法 |
| `--dither {NONE,FLOYDSTEINBERG}` | ディザリングの有無 |
| `--threshold <0-255>` | しきい値（`--dither NONE`時のみ有効） |
| `--bgcolor {black,white}` | レターボックス時の余白色 |
| `--allow-upscale` | 128×64より小さな画像も拡大して処理 |
| `--invert` | 変換後の白黒を反転 |
| `--output-format {png,raw,header}...` | 出力形式。複数指定で同時生成 |
| `--c-symbol-prefix PREFIX` | ヘッダー出力時のシンボル名プレフィックス |

### 出力形式

- **PNG**: `_128x64_bw.png`というファイル名で1bit PNGを出力します。
- **RAW**: `_128x64_bw.raw`として、各行が左から右へ詰められた1bit生データを出力します。
- **HEADER**: `_128x64_bw.h`として、幅・高さ定義と`unsigned char`配列を含むCヘッダーファイルを生成します。`--c-symbol-prefix`で配列名の先頭を調整できます。

### 実行例

```
python ssd1309pngmaker.py \
    --input samples \
    --output out \
    --recursive \
    --mode letterbox \
    --resample LANCZOS \
    --dither FLOYDSTEINBERG \
    --output-format png header raw
```

## ライセンス

このリポジトリは [MIT License](LICENSE) の下で提供されます。
