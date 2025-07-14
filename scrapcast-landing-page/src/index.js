const HeroSection = () => {
    return (
        <header className="hero bg-dark text-white text-center py-5">
            <div className="container">
                <h1 className="display-4">気になるツイートを@ScrapCastGoGoでリツイートするだけ</h1>
                {/* TODO: メンション例の動画/GIF をここに挿入 */}
                <a href="#" className="btn btn-primary btn-lg mt-4">Twitterアカウントで今すぐ始める</a>
            </div>
        </header>
    );
};

const ProblemsSection = () => {
    return (
        <section className="py-5">
            <div className="container">
                <h2 className="text-center mb-4">😵 こんな経験ありませんか？</h2>
                <div className="row">
                    <div className="col-md-4">
                        <div className="card text-center p-3 mb-3">
                            <div className="card-body">
                                <p className="card-text">「あの記事、どこで見たっけ？」</p>
                            </div>
                        </div>
                    </div>
                    <div className="col-md-4">
                        <div className="card text-center p-3 mb-3">
                            <div className="card-body">
                                <p className="card-text">「メモしたけど、どこに保存したか忘れた」</p>
                            </div>
                        </div>
                    </div>
                    <div className="col-md-4">
                        <div className="card text-center p-3 mb-3">
                            <div className="card-body">
                                <p className="card-text">「ブックマークが溢れて見つからない」</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
};

const SolutionSection = () => {
    return (
        <section className="py-5 bg-light">
            <div className="container">
                <h2 className="text-center mb-4">✨ ScrapCastなら3秒で解決</h2>
                <div className="row text-center">
                    <div className="col-md-4">
                        <div className="mb-3">
                            <h3>1️⃣ 引用ツイート</h3>
                            <p>気になるツイートを@ScrapCastGoGoで引用</p>
                        </div>
                    </div>
                    <div className="col-md-4">
                        <div className="mb-3">
                            <h3>2️⃣ 自動要約</h3>
                            <p>AIが自動で要約・整理</p>
                        </div>
                    </div>
                    <div className="col-md-4">
                        <div className="mb-3">
                            <h3>3️⃣ GitHubに保存</h3>
                            <p>GitHubに蓄積して検索可能</p>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
};

const SetupFlowSection = () => {
    return (
        <section className="py-5">
            <div className="container">
                <h2 className="text-center mb-4">🚀 たった2ステップで完了</h2>
                <div className="row text-center">
                    <div className="col-md-6">
                        <div className="mb-3">
                            <h3>1️⃣ Twitterでログイン</h3>
                            <p>（30秒）</p>
                        </div>
                    </div>
                    <div className="col-md-6">
                        <div className="mb-3">
                            <h3>2️⃣ GitHubリポジトリ設定</h3>
                            <p>（2分）</p>
                        </div>
                    </div>
                </div>
                <p className="text-center mt-4">あとは@ScrapCastGoGoで引用するだけ！</p>
            </div>
        </section>
    );
};

const FeaturesSection = () => {
    return (
        <section className="py-5 bg-light">
            <div className="container">
                <h2 className="text-center mb-4">機能詳細</h2>
                <div className="row text-center">
                    <div className="col-md-3">
                        <div className="mb-3">
                            <h4>🤖 AI要約機能</h4>
                            <p>Gemini/GPT-4o miniによる高品質な要約</p>
                        </div>
                    </div>
                    <div className="col-md-3">
                        <div className="mb-3">
                            <h4>📝 Markdown自動整理</h4>
                            <p>指定のフォーマットでGitHubに自動保存</p>
                        </div>
                    </div>
                    <div className="col-md-3">
                        <div className="mb-3">
                            <h4>🔍 GitHub検索対応</h4>
                            <p>蓄積した情報をGitHubで簡単に検索</p>
                        </div>
                    </div>
                    <div className="col-md-3">
                        <div className="mb-3">
                            <h4>📱 Twitter連携</h4>
                            <p>引用ツイートだけで簡単操作</p>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
};

const PricingSection = () => {
    return (
        <section className="py-5">
            <div className="container">
                <h2 className="text-center mb-4">料金プラン</h2>
                <div className="row">
                    <div className="col-md-4">
                        <div className="card mb-4 shadow-sm">
                            <div className="card-header">
                                <h4 className="my-0 fw-normal">無料プラン</h4>
                            </div>
                            <div className="card-body">
                                <h1 className="card-title pricing-card-title">¥0<small className="text-muted fw-light">/月</small></h1>
                                <ul className="list-unstyled mt-3 mb-4">
                                    <li>月20件まで</li>
                                    <li>お試し・個人利用に</li>
                                </ul>
                                <button type="button" className="w-100 btn btn-lg btn-outline-primary">無料で始める</button>
                            </div>
                        </div>
                    </div>
                    <div className="col-md-4">
                        <div className="card mb-4 shadow-sm">
                            <div className="card-header">
                                <h4 className="my-0 fw-normal">🌟 スタンダード</h4>
                            </div>
                            <div className="card-body">
                                <h1 className="card-title pricing-card-title">¥300<small className="text-muted fw-light">/月</small></h1>
                                <ul className="list-unstyled mt-3 mb-4">
                                    <li>月100件まで</li>
                                    <li>AI要約（Gemini 1.5 Flash）</li>
                                    <li>GitHubリポジトリ1つまで</li>
                                    <li>自動リプライ機能</li>
                                </ul>
                                <button type="button" className="w-100 btn btn-lg btn-primary">登録する</button>
                            </div>
                        </div>
                    </div>
                    <div className="col-md-4">
                        <div className="card mb-4 shadow-sm">
                            <div className="card-header">
                                <h4 className="my-0 fw-normal">💎 プロ</h4>
                            </div>
                            <div className="card-body">
                                <h1 className="card-title pricing-card-title">¥500<small className="text-muted fw-light">/月</small></h1>
                                <ul className="list-unstyled mt-3 mb-4">
                                    <li>無制限</li>
                                    <li>AI要約（GPT-4o mini）</li>
                                    <li>リポジトリ複数連携</li>
                                    <li>優先処理</li>
                                </ul>
                                <button type="button" className="w-100 btn btn-lg btn-primary">登録する</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
};

const CTASection = () => {
    return (
        <section className="py-5 text-center bg-light">
            <div className="container">
                <h2 className="mb-4">さあ、今すぐ始めましょう</h2>
                <a href="#" className="btn btn-primary btn-lg mx-2">🐦 Twitterで今すぐ始める</a>
                <a href="#" className="btn btn-secondary btn-lg mx-2">📺 使い方デモを見る</a>
                <a href="#" className="btn btn-info btn-lg mx-2">❓ よくある質問</a>
            </div>
        </section>
    );
};

const Footer = () => {
    return (
        <footer className="py-4 bg-dark text-white text-center">
            <div className="container">
                <p>&copy; 2025 ScrapCast. All Rights Reserved.</p>
            </div>
        </footer>
    );
};

const App = () => {
    return (
        <div>
            <HeroSection />
            <ProblemsSection />
            <SolutionSection />
            <SetupFlowSection />
            <FeaturesSection />
            <PricingSection />
            <CTASection />
            <Footer />
        </div>
    );
};

ReactDOM.render(<App />, document.getElementById('root'));
