# OCR Web セットアップスクリプト (Windows)
# PowerShellで実行してください

Write-Host "🚀 OCR Web セットアップを開始します..." -ForegroundColor Green

# Python バージョンチェック
Write-Host "📋 Python バージョンを確認中..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python が見つかりません。Python 3.10以上をインストールしてください。" -ForegroundColor Red
    exit 1
}

# 仮想環境作成
Write-Host "🔧 仮想環境を作成中..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "⚠️ 既存の仮想環境が見つかりました。削除しますか？ (y/N)" -ForegroundColor Yellow
    $response = Read-Host
    if ($response -eq "y" -or $response -eq "Y") {
        Remove-Item -Recurse -Force ".venv"
        Write-Host "🗑️ 既存の仮想環境を削除しました" -ForegroundColor Yellow
    } else {
        Write-Host "❌ セットアップを中止しました" -ForegroundColor Red
        exit 1
    }
}

python -m venv .venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 仮想環境の作成に失敗しました" -ForegroundColor Red
    exit 1
}
Write-Host "✅ 仮想環境を作成しました" -ForegroundColor Green

# 仮想環境をアクティベート
Write-Host "🔌 仮想環境をアクティベート中..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 仮想環境のアクティベートに失敗しました" -ForegroundColor Red
    exit 1
}
Write-Host "✅ 仮想環境をアクティベートしました" -ForegroundColor Green

# pip アップグレード
Write-Host "⬆️ pip をアップグレード中..." -ForegroundColor Yellow
python -m pip install --upgrade pip
Write-Host "✅ pip をアップグレードしました" -ForegroundColor Green

# 依存関係インストール
Write-Host "📦 依存関係をインストール中..." -ForegroundColor Yellow
pip install -r requirements.txt -c constraints.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 依存関係のインストールに失敗しました" -ForegroundColor Red
    exit 1
}
Write-Host "✅ 依存関係をインストールしました" -ForegroundColor Green

# APIキー設定確認
Write-Host "🔑 APIキー設定を確認中..." -ForegroundColor Yellow
if (Test-Path ".streamlit\secrets.toml") {
    $secretsContent = Get-Content ".streamlit\secrets.toml" -Raw
    if ($secretsContent -match "your-api-key-here") {
        Write-Host "⚠️ APIキーが設定されていません" -ForegroundColor Yellow
        Write-Host "   .streamlit\secrets.toml ファイルを編集して、Gemini APIキーを設定してください" -ForegroundColor Cyan
    } else {
        Write-Host "✅ APIキーが設定されています" -ForegroundColor Green
    }
} else {
    Write-Host "⚠️ secrets.toml ファイルが見つかりません" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 セットアップが完了しました！" -ForegroundColor Green
Write-Host ""
Write-Host "📝 次のコマンドでアプリケーションを起動できます：" -ForegroundColor Cyan
Write-Host "   streamlit run app.py" -ForegroundColor White
Write-Host ""
Write-Host "🌐 ブラウザで http://localhost:8501 にアクセスしてください" -ForegroundColor Cyan
Write-Host ""
Write-Host "📚 詳細な使用方法は README.md を参照してください" -ForegroundColor Cyan
