## Flash Response Application

単語カード型の英語学習アプリケーションです。
Quick Response（瞬間英作文）と呼ばれる通訳者のための練習方法を、単語カード（Flash Card）形式で練習して暗記することができます。\
\
※現在稼働停止中。画面は開発途中のものです。UI/UX、アップロードのエラー処理の追加、多言語化（外国人向け日本語カード）などを行う予定。

<img src="https://user-images.githubusercontent.com/33816000/113381325-a320ca00-93b9-11eb-9463-ca748e2f5fe5.png" width="500">

### Usage　使い方
選定された日本語文（問題）を英訳していき、表現を覚え、会話で応用できるようにします。

### Features　特徴
- 本に近いレイアウト
- 問題を１問ずつカード単位でどれだけできたかの自己評価、練習回数を保存
- 記憶の度合い（忘却度）を評価、練習回数、最後の練習日時より計算
- 記憶の度合い、練習回数に応じた「記憶スコア」により練習項目を選定

### Description 詳細

- 構成（Django/Nginx/gunicorn/PostgreSQL/AWS EC2,S3/Docker/RabbitMQ/Celery）
- 開発環境（ubuntu/emacs/docker-compose/circleCI）
- 機能
    - 問題練習　５問ずつ練習、評価保存、練習途中で評価のリセット
    - ダッシュボード　記憶スコア、本日の練習数などの確認
    - ユーザー認証　ユーザー登録、ログイン/アウト、パスワード変更/リセット
    - CRUD　問題カードを追加/リスト閲覧/編集/削除
    - メール通知　sendGridによるパスワードリセット
    - ページング/検索　問題カードリストにて、20個ずつページ閲覧、キーワードで問題を検索
    - CSVファイルアップロード　指定フォーマットのCSVファイルで自作の問題を追加
	- 音声機能　英語機械音声ファイルの作成（API）、非同期処理での追加
- ドキュメント（画面遷移図、guiflowで作成　https://github.com/hirokidaichi/guiflow/releases/tag/v_0.1.1）
- その他　常時SSL、音声データはS3に保存
