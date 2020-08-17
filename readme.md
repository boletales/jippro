# つかいかた
- 同梱のモデルから難易度表を生成する
  - コマンド：「test2_diffsheet.py "bmsファイルを置いてるフォルダ"」
  - ./samplesに難易度表が生成される

- 生成した難易度表を表示する
    - 事前にnode.jsを入手し、このフォルダで「npm install express」すること
    1. コマンド：「test2_diffsheet.py "bmsファイルを置いてるフォルダ"」
    2. コマンド：「node ./dai2modoki/server.js」
    3. ブラウザで「localhost」にアクセスすると難易度表が表示される
  
- ローカルの譜面で学習を行う
    1. コマンド：「bms2notes.py "bmsファイルを置いてるフォルダ" [all] [sample]」
    2. コマンド：「learn.py "サンプルファイルの数値"」

# githubリンク
https://github.com/boletales/jippro

# colabリンク
https://colab.research.google.com/drive/1w9JRuw0utg4IrmHAiAbi1CcsKecJDv_J#scrollTo=GfGWYCX-s9FG