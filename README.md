# ScreenQRReader
<p align="center"><img alt="icon" src="https://github.com/KNSN92/ScreenQRReader/blob/main/readme_icon.png?raw=true" width="25%" /></p>
<br>
画面上のQRコードを読み取ることが出来るmac用アプリです。
<br>

### ビルド手順
##### 準備
 - python3.13で動作を確認しています。より古いバージョンでも動くかもしれませんが、python3.9では動作しない事を確認済みです。
 - 別途推奨されたバージョンのpythonの環境を用意して下さい。仮想環境をお勧めします。
 - `pip install -r requirements.txt` で必要ライブラリをインストール
##### ビルド
 - 取り敢えず動かす場合は`python main.py`で動かせます。
 - デバッグ用アプリをビルドする場合は`python setup.py py2app --alias`を実行して下さい。
 - 完全なアプリをビルドする場合は`python setup.py py2app`を実行して下さい。