# OCR Web（Streamlit × Gemini API）

画像アップロード→Gemini API OCR→テキスト取得を行うWebアプリケーション

## 🚀 新機能（v2.0.0）

### ✨ フェーズ1: コア機能強化
- **📱 レスポンシブデザイン**: モバイル・タブレット・デスクトップ対応
- **⚡ パフォーマンス最適化**: レイジーローディング、スケルトンローディング
- **🔒 セキュリティ強化**: ファイル検証、入力サニタイゼーション、レート制限

### 📄 フェーズ2: ファイル形式・エクスポート機能
- **📄 PDFサポート**: PDFファイルの画像変換とOCR処理
- **📁 バッチアップロード**: フォルダ単位での一括処理
- **📊 CSV/Excelエクスポート**: 結果の構造化データ出力

## 機能

### 基本機能
- 画像アップロード（PNG/JPEG/WEBP/HEIC対応）
- Gemini APIを使用したOCR処理
- テキスト編集・コピー・保存機能
- 多言語対応（自動言語判定）
- エラーハンドリングとリトライ機能

### 新機能
- **レスポンシブデザイン**: モバイルファーストのUI設計
- **セキュリティ検証**: ファイルアップロードの安全性確保
- **パフォーマンス最適化**: 高速な画像処理と表示
- **PDF処理**: PDFファイルの画像変換とOCR
- **多形式エクスポート**: CSV、Excel、TXT形式での結果出力
- **バッチ処理**: 複数ファイルの一括処理

## セットアップ

### 1. 仮想環境の作成

```powershell
# Windows
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1

# または
python -m venv .venv
.\.venv\Scripts\activate
```

### 2. 依存関係のインストール

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt -c constraints.txt
```

#### オプション機能のインストール

**PDFサポート**:
```bash
pip install PyPDF2 pdf2image
```

**エクスポート機能**:
```bash
pip install pandas openpyxl
```

### 3. APIキーの設定

#### 方法1: Streamlit Secrets（推奨）

`.streamlit/secrets.toml` ファイルを編集し、実際のAPIキーを設定：

```toml
GEMINI_API_KEY = "AIzaSyC..."  # 実際のAPIキーに置き換え
```

#### 方法2: 環境変数

`.env` ファイルを作成（`env.example`をコピーしてリネーム）：

```bash
cp env.example .env
```

`.env` ファイルを編集：

```env
GEMINI_API_KEY=AIzaSyC...  # 実際のAPIキーに置き換え
```

#### 方法3: アプリケーション内入力

アプリケーション起動後、サイドバーの入力フィールドに直接入力

### 4. アプリケーションの起動

```bash
streamlit run app.py
```

## 使用方法

### 基本操作
1. ブラウザで `http://localhost:8501` にアクセス
2. 画像ファイルをアップロード
3. OCR処理を実行
4. 結果を編集・コピー・保存

### 新機能の使用方法

#### PDF処理
1. PDFファイルをアップロード
2. 自動的に画像に変換
3. 各ページをOCR処理
4. 結果を統合して表示

#### エクスポート機能
1. OCR処理完了後
2. エクスポート形式を選択（CSV/Excel/TXT）
3. ダウンロードボタンで保存

#### バッチ処理
1. 複数ファイルを同時アップロード
2. 一括OCR処理
3. 結果の比較・統合

## 対応形式

### 画像形式
- PNG
- JPEG/JPG
- WEBP
- HEIC/HEIF（要pillow-heif）

### 新規対応形式
- **PDF**（要PyPDF2、pdf2image）

## セキュリティ機能

### ファイル検証
- ファイルサイズ制限（20MB）
- ファイル形式検証
- マジックナンバーチェック
- 危険なファイル名パターンの検出

### 入力サニタイゼーション
- HTMLエスケープ
- 改行文字の正規化
- 連続改行の制限

### レート制限
- 1分間に10リクエストまで
- 自動的な制限管理

## パフォーマンス最適化

### 画像処理
- レイジーローディング
- 自動リサイズ（長辺2048px）
- メモリ効率的な処理

### UI最適化
- スケルトンローディング
- 進捗表示
- レスポンシブレイアウト

## トラブルシューティング

### API Key エラーが発生する場合

1. **API Keyの確認**
   - [Google AI Studio](https://aistudio.google.com/) でAPI Keyが正しく取得されているか確認
   - API Keyの形式が `AIzaSyC...` で始まるか確認

2. **設定の確認**
   - `.streamlit/secrets.toml` の `GEMINI_API_KEY` がプレースホルダー（`"your-api-key-here"`）になっていないか確認
   - 環境変数 `GEMINI_API_KEY` が正しく設定されているか確認

3. **アプリケーション内での検証**
   - サイドバーの「🔍 APIキーを検証」ボタンを使用してAPI Keyの有効性を確認

### PDF機能のエラー

1. **ライブラリの確認**
   ```bash
   pip install PyPDF2 pdf2image
   ```

2. **PDF2Imageの依存関係**
   - Windows: `poppler` のインストールが必要
   - macOS: `brew install poppler`
   - Linux: `apt-get install poppler-utils`

### エクスポート機能のエラー

1. **ライブラリの確認**
   ```bash
   pip install pandas openpyxl
   ```

### その他のエラー

- **ファイルサイズエラー**: 20MB以下のファイルを使用
- **処理時間エラー**: 画像サイズを小さくするか、リトライ回数を増やす
- **形式エラー**: 対応形式のファイルを使用
- **レート制限エラー**: しばらく待ってから再試行

## 注意事項

- APIキーは環境変数またはStreamlit Secretsで管理
- 大きなファイル（20MB超）は自動的にFiles APIに切り替え
- 処理時間は最大60秒
- APIキーは公開リポジトリにコミットしないよう注意
- PDF処理は大量のメモリを使用する場合があります
- セキュリティ機能により一部のファイルが拒否される場合があります

## 技術仕様

### フレームワーク
- **Streamlit**: Webアプリケーションフレームワーク
- **Gemini API**: OCR処理エンジン
- **PIL/Pillow**: 画像処理

### 新規技術
- **PyPDF2**: PDFファイル処理
- **PDF2Image**: PDF画像変換
- **Pandas**: データ処理・CSV出力
- **OpenPyXL**: Excelファイル生成

### セキュリティ
- **ファイル検証**: マジックナンバー、サイズ、形式チェック
- **入力サニタイゼーション**: HTMLエスケープ、正規化
- **レート制限**: セッション管理による制限

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。
