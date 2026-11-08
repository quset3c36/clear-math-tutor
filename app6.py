import os
import re
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# Streamlitのページ設定
st.set_page_config(
    page_title="クリアー数学I+A 徹底解説AI",
    page_icon="📐",
    layout="wide"
)

# Gemini APIクライアントの初期化
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    else:
        st.error("GEMINI_API_KEY が設定されていません。.envファイルを確認してください。")
        st.stop()

client = genai.Client(api_key=api_key)

# ==========================================
# 📚 問題データベース（辞書）
# ==========================================
PROBLEM_DATABASE = {
    "20": {
        "title": "例題20：確率（くじ引き）",
        "text": "当たりが4本，はずれが8本あるくじから，4本を同時に引くとき，4本ともはずれ る確率を求めよ。"
    },
    "21": {
        "title": "例題21：確率から個数の決定（玉を取り出す）",
        "text": "赤玉と白玉が合わせて10個入った袋から，2個の玉を同時に取り出すとき，2個とも赤玉である確率が \\frac{2}{15} であるという。赤玉の個数を求めよ。"
    },
    "22": {
        "title": "例題22：和事象，余事象の確率（玉を取り出す）",
        "text": "赤玉4個，白玉6個の入った袋から，4個の玉を同時に取り出すとき，次の場合の確率を求めよ。\n(1) 4個とも同じ色の玉が出る。\n(2) 赤玉と白玉がともに取り出される。"
    },
    "23": {
        "title": "例題23：出る目の最大値と確率（さいころ）",
        "text": "3個のさいころを同時に投げるとき，次の場合の確率を求めよ。\n(1) 出る目の最大値が3以下である。\n(2) 出る目の最大値が4である。"
    },
    "24": {
        "title": "例題24：独立な試行の確率（くじ引き）",
        "text": "箱Aには当たり2本，はずれ8本の計10本のくじ，箱Bには当たり1本，はずれ5本の計6本のくじが入っている。箱A, Bから1本ずつくじを引くとき，当たりくじを1本だけ引く確率を求めよ。"
    },
    "25": {
        "title": "例題25：反復試行の確率（硬貨投げ）",
        "text": "1枚の硬貨を6回投げるとき，次の場合の確率を求めよ。\n(1) 表がちょうど3回出る。\n(2) 表が5回以上出る。"
    },
    "26": {
        "title": "例題26：点の移動と反復試行（さいころ）",
        "text": "数直線上を動く点Pが原点の位置にある。1個のさいころを投げて，1または6の目が出たときはPを負の方向に1だけ進め，それ以外の目が出たときはPを正の方向に1だけ進める。さいころを4回投げ終わったとき，Pの座標が2となる確率を求めよ。"
    },
    "27": {
        "title": "例題27：条件付き確率（くじ引き）",
        "text": "当たりくじ4本を含む9本のくじを，A，Bの2人がこの順に1本ずつ引くとき，次の確率を求めよ。ただし，引いたくじはもとに戻さない。\n(1) Aが当たったとき，Bも当たる確率\n(2) Aがはずれ，Bが当たる確率"
    },
    "28": {
        "title": "例題28：条件付き確率（くじ引き）",
        "text": "当たりくじ3本を含む9本のくじを，A，B，Cの3人がこの順に1本ずつ引くとき，Cが当たる確率を求めよ。ただし，引いたくじはもとに戻さない。"
    },
    "29": {
        "title": "例題29：原因の確率",
        "text": "白玉4個，赤玉2個が入った袋がある。もとに戻さないで1個ずつ続けて2回玉を取り出す。2回目の玉が赤であるとき，1回目の玉が赤である確率を求めよ。"
    },
    "30": {
        "title": "例題30：期待値",
        "text": "赤玉3個，白玉2個が入った袋から3個の玉を同時に取り出すとき，赤玉が出る個数をXとする。Xの期待値を求めよ。"
    },
    "31": {
        "title": "例題31：期待値と有利・不利",
        "text": "5枚の10円硬貨を同時に投げて，表の出た硬貨を受け取るゲームがある。このゲームの参加料が1回30円のとき，このゲームに参加することは得であるか，損であるか。"
    },
    "34": {
        "title": "例題34：反復試行の確率（排反な3つの事象）",
        "text": "赤玉1個と白玉2個と青玉3個が入った袋から1個の玉を取り出し，色を見てからもとに戻すことを5回行う。このとき，赤玉が2回，白玉が1回，青玉が2回出る確率を求めよ。"
    },
    "45": {
        "title": "例題45：内接円の半径と辺の長さ",
        "text": "△ABCにおいて、AB=7, BC=8, CA=5 とする。この三角形の内接円と辺BC, CA, AB との接点をそれぞれ P, Q, R とするとき、CQ の長さを求めよ。"
    },
    "46": {
        "title": "例題46：方べきの定理の利用",
        "text": "円Oを中心にする半径2の円の内部に点Pがあり、PA·PB=1 のとき、点Pを通る弦ABについて、線分OPの長さを求めよ。"
    },
    "64": {
        "title": "例題64：和と最大公約数の条件から2数を求める",
        "text": "和が 210, 最大公約数が 14 である 2 つの自然数 a, b の組をすべて求めよ。ただし, a < b とする。"
    },
    "65": {
        "title": "例題65：整数の割り算と余り",
        "text": "a, b は整数とする。a を 6 で割ると 4 余り, b を 6 で割ると 5 余る。次の数を 6 で割ったときの余りを求めよ。\n(1) a + b\n(2) ab"
    },
    "66": {
        "title": "例題66：倍数でないことの証明（余りによる整数の分類を利用）",
        "text": "n は整数とする。n^2 - 2 は 3 の倍数でないことを証明せよ。"
    },
    "67": {
        "title": "例題67：連続する3つの整数の積の証明",
        "text": "n は整数とする。2n^3 - 3n^2 + n は 6 の倍数であることを証明せよ。"
    },
    "68": {
        "title": "例題68：a^k を m で割った余り",
        "text": "5^{100} を 6 で割った余りを求めよ。"
    },
    "69": {
        "title": "例題69：a^k を m で割った余り",
        "text": "n は整数とする。n を 5 で割った余りが 3 であるとき, n^{30} を 5 で割った余りを求めよ。"
    },
    "71": {
        "title": "例題71：最大公約数（互除法を利用）",
        "text": "731 と 301 の最大公約数を, 互除法を用いて求めよ。"
    },
    "72": {
        "title": "例題72：1次不定方程式の解法",
        "text": "(1) 等式 86x - 49y = 3 を満たす整数 x, y の組を 1 つ求めよ。\n(2) 方程式 86x - 49y = 3 の整数解をすべて求めよ。"
    },
    "73": {
        "title": "例題73：余りと 1 次不定方程式",
        "text": "5 で割ると 2 余り, 14 で割ると 5 余るような自然数のうち, 3 桁で最大のものを求めよ。"
    },
    "74": {
        "title": "例題74：等式を満たす整数 x, y の組",
        "text": "次の等式を満たす整数 x, y の組をすべて求めよ。\nxy - 2x + 3y - 1 = 0"
    },
    "75": {
        "title": "例題75：x, y の2次不定方程式（分数形）",
        "text": "\\frac{1}{x} + \\frac{1}{y} = \\frac{1}{3} を満たす自然数 x, y の組をすべて求めよ。"
    },
    "76": {
        "title": "例題76：n進法",
        "text": "10進法の数 123 を 5進法で表せ。"
    },
    "77": {
        "title": "例題77：n進法の小数",
        "text": "10進法の小数 0.8125 を 4進法で表せ。"
    },
    "78": {
        "title": "例題78：n進法と数字の並び",
        "text": "自然数 N を 2進法で表すと 5桁の数 11a01_{(2)} となり，7進法で表すと 2桁の数 3b_{(7)} となるという。a, b を求めて，N を 10進法で表せ。"
    },
    "81": {
        "title": "例題81：不定方程式の整数解（3元分数形）",
        "text": "次の等式を満たす自然数 x, y, z の組をすべて求めよ。\n\\frac{1}{x} + \\frac{1}{y} + \\frac{1}{3z} = \\frac{4}{3} \\quad (x \\leqq y \\leqq z)"
    },
    "82": {
        "title": "例題82：倍数であることを証明（背理法を利用）",
        "text": "整数 a, b, c が a^2 + b^2 = c^2 を満たすとき，a, b のうち少なくとも1つは偶数であることを証明せよ。"
    }
}

# ==========================================
# 🆕 新機能：まずはテスト！セクション
# ==========================================
st.markdown("### 📝 まずはテスト！")
st.write("解説を見る前に、問題番号を入力して自分の力だけで問題を解いてみよう。")

test_col1, test_col2 = st.columns([2, 3])
with test_col1:
    test_number = st.text_input("テストする例題番号を入力（例: 25, 45, 65）：", placeholder="25", key="test_input")

if st.button("🔍 テスト問題を表示する", type="secondary"):
    clean_test_key = test_number.strip()
    if not clean_test_key:
        st.warning("例題番号を入力してください。")
    elif clean_test_key not in PROBLEM_DATABASE:
        st.error(f"⚠️ 例題「{clean_test_key}」はデータベースに登録されていません。")
    else:
        test_data = PROBLEM_DATABASE[clean_test_key]
        # テスト問題を綺麗にカード形式で表示
        st.markdown(f"""
        <div style="background-color: #e3f2fd; border: 2px solid #90caf9; border-radius: 10px; padding: 20px; margin-top: 10px; margin-bottom: 20px;">
            <h4 style="margin-top: 0; color: #0d47a1;">🎯 挑戦中の問題：{test_data['title']}</h4>
            <p style="font-size: 18px; font-weight: bold; color: #333;">{test_data['text']}</p>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ==========================================
# メインタイトル＆通常の徹底解説機能
# ==========================================
st.title("📐 クリアー数学I+A「辞書＆美図解」徹底解説AI")
st.write("アプリ内のデータベースから正確な問題文を瞬間呼び出し、**論理の飛躍ゼロの解説**と**美しいSVG図解**を左右に並べて表示します。")

st.divider()

# サイドバー設定
st.sidebar.header("⚙️ 設定・登録確認")
st.sidebar.write(f"登録済み例題数: {len(PROBLEM_DATABASE)}問")

target_grade = st.sidebar.select_slider(
    "解説の丁寧さ",
    options=["初学者向け（行間を完全に埋める）", "標準レベル"],
    value="初学者向け（行間を完全に埋める）"
)

# 入力フォーム
st.subheader("📝 徹底解説の番号を入力")
col_input1, col_input2 = st.columns([2, 3])
with col_input1:
    example_number = st.text_input(
        "解説を見たい例題番号を入力してください：",
        placeholder="45",
        key="main_input"
    )

# 生成ボタン
if st.button("🚀 データベースから検索して解説を生成する", type="primary"):
    clean_key = example_number.strip()
    
    if not clean_key:
        st.warning("例題番号を入力してください。")
    elif clean_key not in PROBLEM_DATABASE:
        st.error(f"⚠️ 例題「{clean_key}」はまだデータベースに登録されていません。")
    else:
        target_problem = PROBLEM_DATABASE[clean_key]
        problem_text = target_problem["text"]
        problem_title = target_problem["title"]

        with st.spinner(f"「{problem_title}」の正確な問題文をもとに、SVG図解とステップ解説を作成中..."):
            system_instruction = f"""
あなたは数学の超一流プロ家庭教師であり、SVGグラフィックのデザイナーです。『クリアー数学I+A』の視覚的図解を作成します。

【絶対厳守のルール】
1. **問題文の正確な表示**: 提示された以下の問題文をそのまま「### 【問題: {problem_title}】」として最初に記載してください。
2. **SVG図解の品質と構造（超重要）**:
   - 必ず `<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">...</svg>` の形式で出力してください（```xml などのコードブロックは使わず、タグを直接出力）。
   - **テキストをSVG枠の外や下に平文で垂れ流すことは絶対に禁止**です。すべての文字ラベルや数値は、必ずSVG内の `<text x="..." y="..." font-size="14" fill="#333">...</text>` タグを使って図の中に配置してください。
   - 確率や樹形図の問題であれば、円（`<circle>`）や四角（`<rect>`）、線（`<line>`）を使って確率分布、ツリー構造や袋の中身を視覚的に描き、分岐の確率を `<text>` で添えてください。
3. **図解に対応する箇条書きの解説**:
   - SVG図解の下、または右側の解説エリアに、図に対応する「図のポイント・箇条書き」をスッキリ整理して記載してください。
4. **論理の飛躍の完全排除**: すべての計算や公式の選択理由を「### 【ステップ別詳細解説】」として行間100%で解説してください。

- 対象レベル: {target_grade}
"""    
            # 図が確実に生成される最新のプロンプト
#             system_instruction = f"""
# あなたは数学の超一流プロ家庭教師です。『クリアー数学I+A』の解説を作成します。

# 【絶対厳守のルール】
# 1. **問題文の正確な表示**: 提示された以下の問題文をそのまま「### 【問題: {problem_title}】」として最初に記載してください。
# 2. **SVGによる美しい図解の生成（超重要）**: 
#    - 図形問題だけでなく、数論や確率（くじ、硬貨、余りなど）の問題であっても、必ず状況を視覚化した図を `<svg ...>...</svg>` で生成してください（```xmlなどのコードブロックは使わずタグを直接出力）。
#    - 線の太さ（stroke-width: 2px以上）、色（青、赤、オレンジなど）、背景（薄い色）を使い、テキストラベルや数値を配置して視覚的に非常に分かりやすいベクター画像を作成してください。
# 3. **論理の飛躍の完全排除**: すべての変形や公式の選択理由を「### 【ステップ別詳細解説】」として行間100%で解説してください。

# - 対象レベル: {target_grade}
# """

            try:
                response = client.models.generate_content(
                    model='gemini-3.8-flash',
                    contents=f"以下の問題について、SVG図解付きで徹底解説してください:\n{problem_text}",
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.2,
                    )
                )

                full_text = response.text

                # 1. AIの返答から <svg> ... </svg> を抽出
                svg_match = re.search(r'(<svg[\s\S]*?</svg>)', full_text)
                svg_code = svg_match.group(1) if svg_match else ""

                # 2. 文章部分からSVGタグを取り除く
                explanation_text = re.sub(r'<svg[\s\S]*?</svg>', '', full_text)

                st.markdown(f"### 💡 {problem_title} 徹底解説")

                # 画面を左右に分割（左：図解 / 右：問題と解説）
                col_left, col_right = st.columns([1, 1])

                with col_left:
                    st.markdown("#### 📐 視覚的図解")
                    if svg_code:
                        st.markdown(f"""
                        <div style="background-color: #f8f9fa; border: 2px solid #e9ecef; border-radius: 10px; padding: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                            {svg_code}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.warning("図解の生成に失敗しました。")

                with col_right:
                    st.markdown("#### 📝 問題とステップ解説")
                    # 💡 解説文だけをスクロールできるように高さを指定
                    with st.container(height=500):
                        st.markdown(explanation_text, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

st.divider()
st.caption("※アプリ内のデータベースに登録された正確な問題文を使用するため、数値のズレや著作権ブロックを完全に回避できます。")