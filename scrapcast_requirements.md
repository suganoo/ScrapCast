### 📝 Markdown保存フォーマットの仕様

以下の形式でGitHubリポジトリのMarkdownファイルに追記される：

```markdown
### ChatGPTによる自動コードレビュー実験
ChatGPTを活用してGitHubのPRレビューを自動化。精度と作業効率が向上した。
https://twitter.com/ユーザー名/status/ツイートID
- https://github.com/example/repo
- https://zenn.dev/sample/article
```

#### フォーマット要素：
- `### タイトル行`: 元ツイートの内容からAIが生成する簡潔なタイトル（最大15〜20文字程度）
- 次の行：元ツイートの要約（1〜2文）
- 次の行：元ツイートのURL（引用元ツイートリンク）
- 次の行：ツイート内に含まれていたその他の外部リンク（最大数件までリスト形式）

#### ルール：
- 行間は空けない
- `要約:` や `リンク:` などのラベルは使わない
- Markdown内の構文を破壊しないようURL等は生のまま記載
- 複数の参考URLがあればハイフン（`- `）付きでリストにする

この形式により、情報の視認性とGitHubでの履歴管理・内容整理が容易になる。

---

### 💬 ツイートへの返信仕様

ScrapCastが保存処理を完了したら、メンション付きツイートに対してリプライを送信する。

#### リプライ内容：
- 「保存完了」のメッセージ
- GitHubで更新されたMarkdownファイルのリンクを含める

#### メッセージ例：
```
✅ 保存しました！
こちらに追加しました👇
https://github.com/ユーザー名/リポジトリ名/blob/main/x_notes.md
```

### 🔐 Secrets管理について

ScrapCastでは、外部API（GitHub、Twitter）との安全な連携のために、シークレット情報（認証キーやトークンなど）を環境変数として安全に管理する必要がある。

#### 管理対象の例：
| シークレット名         | 用途                                |
|--------------------------|-------------------------------------|
| `GITHUB_CLIENT_ID`       | GitHub OAuth認証用のクライアントID |
| `GITHUB_CLIENT_SECRET`   | GitHub OAuth認証用のシークレット    |
| `TWITTER_BEARER_TOKEN`   | Twitter APIアクセス用トークン       |
| `JWT_SECRET`             | Webアプリのセッション署名用秘密鍵   |

#### Render.com での管理方法：
- 管理画面 > 対象のサービス > Environment タブを開く
- 必要なキーと値を入力（暗号化されて保存）
- アプリケーション内では `os.environ["KEY"]` のように読み出し
- サーバー再起動時にも自動で反映される

#### セキュリティ上の注意：
- これらは絶対にソースコードに直接書かないこと
- GitHubリポジトリにも含めないこと（.envファイルなどは除外）
- トークン漏洩の防止とアクセス制御のため、必要最小限の範囲で使用する

---

#### 補足：
- ユーザーによってリポジトリやファイル名が異なるため、動的にリンクを生成する
- リプライは元メンションツイートに対して直接送信
- 失敗時はエラーメッセージや再試行ログを残す

---

### 🔄 イベント駆動アーキテクチャ（Firestore活用）

ScrapCastは、Firestoreを中心としたイベント駆動アーキテクチャを採用し、効率的でスケーラブルな処理を実現する。

#### データフロー：
1. **GitHub Actions（定期実行）**
   - Twitter APIから引用ツイートを取得
   - 取得したツイートURLをFirestoreに保存
   - 重複チェック・差分更新のみ実行

2. **Firestore（データストア + イベントトリガー）**
   - ツイートURLの永続化
   - Cloud Functions のトリガーとして機能
   - `onCreate` イベントで後続処理を自動実行

3. **Cloud Functions（イベント処理）**
   - Firestore変更検知で自動起動
   - Twitter APIでツイート詳細を再取得
   - AI要約生成（Gemini 1.5 Flash → GPT-4o mini）・Markdown保存・リプライ送信を順次実行

#### Firestoreスキーマ案：

**ツイートデータ**
```
scrapcast_tweets/{tweetId}
├── id: string           // ツイートID
├── url: string          // 引用ツイートURL
├── author_username: string // 引用ツイートした人のアカウント
├── quoted_tweet_url: string // 引用元ツイートURL
├── created_at: timestamp
├── processed: boolean   // 処理済みフラグ
└── processing_status: { // 処理ステータス
    ├── summarized: boolean
    ├── saved_to_github: boolean
    └── replied: boolean
    }
```

**ユーザー設定データ**
```
scrapcast_users/{username}
├── username: string           // Twitterアカウント名
├── github_owner: string       // GitHubオーナー名
├── github_repo: string        // GitHubリポジトリ名
├── github_file_path: string   // 保存先ファイルパス（例: "notes.md"）
├── created_at: timestamp
├── active: boolean            // アクティブ状態
└── settings: {               // ユーザー固有設定
    ├── auto_reply: boolean
    └── summary_length: string  // "short" | "medium" | "long"
    }
```

**データ関連付け**
- `scrapcast_tweets` の `author_username` で `scrapcast_users` を参照
- ユーザーごとの異なるGitHubリポジトリに対応

#### AI要約エンジン：
**段階的AI選択**
- **開発・テスト期**: Gemini 1.5 Flash（無料枠活用、150万tokens/分）
- **本運用期**: OpenAI GPT-4o mini（高品質・低コスト、$0.15-0.6/1M tokens）

**コスト試算（月100ツイート処理）**
- 開発期: ほぼ無料（Gemini無料枠内）
- 運用期: 約$0.5-1（GPT-4o mini）

#### メリット：
- **イベント駆動**: 新規ツイート検知時の自動処理
- **軽量データ**: URLのみ保存でストレージ効率化
- **処理分離**: 取得・加工・保存の責務分離
- **スケーラビリティ**: 処理量増加に対応可能
- **監視・デバッグ**: 処理状況の可視化
- **コスト最適化**: 段階的AI選択で開発コスト削減

---

### 🏗 インフラ構成（低コスト・MVP向け）

ScrapCastは、コストを抑えながら安定して動作するインフラ構成を採用する。

#### 構成要素：
| 機能        | サービス        | プラン/料金        | 備考 |
|-------------|------------------|---------------------|------|
| Web UI/API  | Render.com または Fly.io | 無料枠あり（月数百円以下） | Node.js / Python 対応 |
| DB（設定管理用） | Cloud Firestore（Firebase） | 無料枠で十分 | スキーマレス・シンプル |
| Polling処理 | GitHub Actions（cron） | 無料（パブリックRepo前提） | 定期実行可能、シンプル構成 |
| OAuth連携 | Render/Fly内で対応 | - | 認証・リダイレクト処理対応 |
| Secrets管理 | Render/Fly/Actionsに内蔵 | - | APIトークンを安全に保持 |

#### ポイント：
- GitHub Actionsのcronを使えば、常駐プロセスなしでPollingを実現
- Firestoreは5万読み取り/月・1GBストレージまで無料で十分
- RenderやFly.ioは無料で常時稼働可能（低負荷アプリ前提）

#### 補足：
- 一定のユーザー数を超えたら有料プラン or クラウド移行も検討
- GitHub Actionsの使用時間（2,000分/月）に注意

---

### 🌐 ランディングページ（LP）構成案

ScrapCastの魅力を効果的に伝えるLPの構成要素。

#### 1. ヒーロー（メインビジュアル）
```
📱 気になるツイートを見つけたら、@ScrapCastGoGoで引用するだけ
→ 自動でAI要約してGitHubに保存！

[メンション例の動画/GIF]
[🐦 Twitterで今すぐ始める]
```

#### 2. 課題提起
```
😵 こんな経験ありませんか？
❌ 「あの記事、どこで見たっけ？」
❌ 「メモしたけど、どこに保存したか忘れた」
❌ 「ブックマークが溢れて見つからない」
```

#### 3. 解決策
```
✨ ScrapCastなら3秒で解決
1️⃣ 気になるツイートを@ScrapCastGoGoで引用
2️⃣ AIが自動で要約・整理
3️⃣ GitHubに蓄積して検索可能
```

#### 4. 設定フロー
```
🚀 たった2ステップで完了
1️⃣ Twitterでログイン（30秒）
2️⃣ 保存先GitHubリポジトリを設定（2分）
→ あとは@ScrapCastGoGoで引用するだけ！
```

#### 5. 機能詳細
- 🤖 AI要約機能（Gemini/GPT-4o mini）
- 📝 Markdown自動整理
- 🔍 GitHub検索対応
- 📱 Twitter連携

#### 6. 料金プラン
**無料プラン**: 月20件まで（お試し・個人利用）

**🌟 スタンダードプラン（月300円）**:
- 月100件までの引用ツイート処理
- AI要約（Gemini 1.5 Flash）
- GitHubリポジトリ1つまで連携
- 基本のMarkdown保存
- 自動リプライ機能

**💎 プロプラン（月500円）**:
- 無制限の引用ツイート処理
- AI要約（GPT-4o mini）← 高品質
- GitHubリポジトリ複数連携
- カスタム要約テンプレート
- 優先処理（処理速度向上）
- 詳細ダッシュボード（統計・分析）
- Slack/Discord通知連携

#### 7. CTA（行動喚起）
- **メインCTA**: [🐦 Twitterで今すぐ始める]
- **サブCTA**: [📺 使い方デモを見る] [❓ よくある質問]

