## ScrapCast 要件定義書

### ✅ サービス概要
ScrapCastは、ユーザーがTwitter（X）上で保存したいツイートをリツイートし、@ScrapCastGoGo をメンションすることで、ツイートのリンクを自動的に指定されたGitHubリポジトリのMarkdownファイルに保存するWebサービスです。

---

### 👤 想定ユーザー
- Twitterアカウントを持つ一般ユーザー
- GitHubアカウントを持ち、自分のリポジトリで記録を残したい人

---

### 📌 利用フロー
1. ユーザーが保存したいツイートを見つける
2. リツイートして @ScrapCastGoGo をメンション
3. ScrapCastが元ツイートのURLを取得
4. 指定されたGitHubリポジトリのMarkdownファイルに追記
5. 完了通知（リプライ or Web UI上）

---

### ⚙️ 機能要件
#### 1. Twitter連携
- Twitter APIでメンション付きRTを検知（Mentions Timelineを使用）
- 元ツイートのURLと本文取得

#### 2. ユーザー認証（GitHub OAuth）
- GitHub OAuthを使用してユーザー認証を行い、アクセストークンを取得
- スコープは最小限で構成（例：`repo`, `read:user`）
- 認証フローは以下の通り：
  1. 認証URLへリダイレクト
  2. GitHub認証画面でユーザーが許可
  3. コールバックエンドポイントでアクセストークンを取得
  4. アクセストークンを暗号化してDBに保存

#### 3. Markdown書き込み
- 初期ファイル名：`x_notes.md`
- Markdown形式：
  ```markdown
  - [ツイート内容（冒頭のみ）](https://twitter.com/ユーザー名/status/ツイートID) - yyyy-mm-dd
  ```

#### 4. 書き込みファイル管理
- ファイル名はWeb UIで変更可能
- ユーザーは複数ファイルを登録できる（`ai_notes.md`, `dev_tips.md`など）
- 各ファイルにDescription（用途説明）を設定可能
- AIがツイート内容とDescriptionを比較して最適なファイルを選択（埋め込み or BERTベース）

#### 5. Mentions Polling
- Twitter API v2 `GET /2/users/:id/mentions` を用いて、定期的にメンションを取得
- Polling間隔は60秒程度
- 前回取得ID（`last_seen_id`）を保存し、差分取得を行う
- メンション元がリツイートである場合、元ツイートのIDを取得し、保存対象として処理
- 実装はPython等で常駐プロセスとして構成可能

#### 6. GitHub連携
- OAuthトークンを使い、GitHubのREST APIで対象リポジトリのMarkdownファイルに追記
- API使用例：
  ```http
  PUT /repos/:owner/:repo/contents/:path
  ```
- ファイルが存在しない場合は新規作成
- ファイル更新時は最新SHAを取得して上書き

#### 7. リポジトリ設定画面
- 保存先リポジトリ名、ファイル名、Descriptionを設定・編集可能

#### 8. エラーハンドリング
- 処理失敗時、TwitterリプライまたはWeb UIにて通知
- Polling・GitHub連携・分類処理それぞれにログを残す

---

### 🔒 非機能要件
- GitHubトークンは暗号化保存
- 通信は全てHTTPS
- 高負荷時はバッチ処理で対応
- 再起動時も重複処理が起きないよう `last_seen_id` を永続化
- 将来的なZennやNotion連携に備えた拡張設計

---

### 🧪 技術スタック（例）
| 分類         | 技術・サービス        |
|--------------|------------------------|
| フロントエンド | Next.js / React        |
| バックエンド   | Node.js / Express      |
| DB           | Firestore / DynamoDB    |
| 認証         | GitHub OAuth           |
| 外部API      | Twitter API / GitHub API |
| デプロイ     | Vercel / Render / Fly.io |

---

### 🌱 拡張の可能性
- ツイート分類による知識の自動整理
- 複数媒体（Notion, Zennなど）への保存先拡張
- カスタムルールによる分類精度向上

---

### 📥 Mentions Polling 機能要件（詳細）
#### 機能名
Twitter Mentions Polling

#### 目的
ScrapCastの公式アカウント（@ScrapCastGoGo）がTwitter上でメンションされた新着ツイートを定期的に検出し、それがリツイートであれば元ツイートの情報を取得して、後続の保存処理（例：GitHub書き込み）へ連携する。

#### トリガー
- 一定間隔で実行されるバッチまたは常駐プロセス（推奨：60秒間隔）

#### 入力
- Bearer Token（Twitter API v2）
- ScrapCastアカウントの user_id
- 前回取得した最新ツイートID（last_seen_id）

#### 処理内容
1. Twitter API で mentions を取得
2. referenced_tweets フィールドを見て、retweeted タイプがあれば処理対象
3. 元ツイートの情報を取得し、GitHub保存に渡す
4. 最後に処理したメンションIDを更新・保存

#### 出力
- 元ツイートの情報（ID / テキスト / 投稿者 など）

#### 非機能要件
- 安定したPolling間隔での実行
- エラー処理と再試行
- 再起動時も前回IDから継続可能
- ツイートは古い順に処理

---

### 🧩 GitHub連携の前提設定
#### リポジトリ設定
- 対象ファイルが存在するパブリック or プライベートリポジトリ
- ユーザーが管理者 or コラボレーターであること

#### アクセストークン取得（OAuth）
- スコープ：`repo`, `read:user`
- トークンは暗号化保存

#### ファイル更新API
- `PUT /repos/:owner/:repo/contents/:path`
- Base64でファイル内容を送信
- 更新にはSHAが必要
- GitHub AppやFine-grained tokenでも将来的に対応可能

---

今後のステップ：画面設計 / データモデル設計 / GitHub更新処理の実装 など

