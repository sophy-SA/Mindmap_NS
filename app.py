import streamlit as st
import google.generativeai as genai
import base64
import requests
import os
from datetime import datetime
#from dotenv import load_dotenv

###Mermaid APIによるブロック図の生成とbase64エンコード(半角記号が含まれたコードも変換可能) 
#streamlit移植版
#事前に発想を広げてからmermeidコードを出力する構成

#
#ニーズ層とシーズ層の層数など構成を定義した
#キーワードの被りが無いようにチェックを導入、回答出力が安定するように修正
#3_1から2までの知見を盛り込んだまとめ版
#
# 既出の単語を使わないようにより強く分かりやすく指示
# GPTの指示を採用したVer

#  多少改善できたが完全ではない
#  ニーズ、シーズ、要求特性で違う言葉になるように工夫が必要。それでもニーズグループ内で同じものが出る危険はあるが、、
#  または各層のキーワードがオリジナルになるように命名規則を設ける。一回プロンプトの中ではもうこれしかなさそう


# extract_mermaid_code関数の定義
def extract_mermaid_code(response_text):
    try:
        # response_textを行ごとに分割
        lines = response_text.split('\n')
        mermaid_code = []
        response_text = []

        # 各行をチェック
        in_mermaid_block = False
        for line in lines:
            if line.strip() == '```mermaid':
                in_mermaid_block = True
                continue
            elif line.strip() == '```':
                in_mermaid_block = False
                continue

            if in_mermaid_block:
                mermaid_code.append(line)
            else:
                response_text.append(line)

        # 結果を整形
        mermaid_code = '\n'.join(mermaid_code)
        response_text = '\n'.join(response_text)

        return response_text, mermaid_code
    except Exception as e:
        st.error(f"エラーが発生しました: {str(e)}")

# Gemini APIの設定
genai.configure(api_key='AIzaSyA35e8FnZfrxjTP7_RBZQvAm7sjGwb6TWI')
#model = genai.GenerativeModel('gemini-1.5-pro')
model = genai.GenerativeModel('gemini-2.0-flash-exp')
#model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp')

# 環境変数の読み込み版
#load_dotenv()
#genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
#model = genai.GenerativeModel('gemini-pro')

# Streamlitのページ設定
st.set_page_config(page_title="マインドマップジェネレーター", layout="wide")
st.title("ニーズとシーズの深堀りマップ")

# セッション状態の初期化
if 'img_data' not in st.session_state:
    st.session_state.img_data = None
if 'img_url' not in st.session_state:
    st.session_state.img_url = None
if 'mermaid_code' not in st.session_state:
    st.session_state.mermaid_code = None
if 'response_text' not in st.session_state:
    st.session_state.response_text = None


# 入力フォームの作成
prompt1 = st.text_input("ターゲットにする製品/用途/購買層を入力：　例) 製品名、○○を△△する、○○用品など")
prompt2 = st.text_input("保有する技術/製品/サービスを入力：　例）○○製造技術、△△マネジメントサービスなど")
prompt3 = st.text_area("指示内容、注意点、参考情報：", value="特になし")

# 推論開始ボタンが押されたときの処理
if st.button("推論開始(マップを生成)"):
    if prompt1 and prompt2:
        try:
            # プロンプトの作成
            prompt = f"""
            ##指示
            あなたは優秀なプロダクト開発支援のプロコンサルタントです。
            ターゲットのニーズに向けて保有技術の進化や発展の方向を考察するマインドマップを作成します。
            作成したマインドマップをMermaidで描画するためのコードを表示してください。
            
            ##マインドマップの形式
            左の端にユーザーの設定したニーズがあり、ニーズから用途や利用シーンを発想していく。
　　　　　　発想した要素からさらに発想をつなげて独創的で多様なたくさんの要素を発想する。
　　　　　　発想は右に向かって広がり、キーワードが増える。

            反対側(右端)にユーザーの設定したシーズ(保有している技術、製品、サービス)がある。
　　　　　　シーズから左に向かって、応用や転換、または組み合わせで作れる技術を発想して増やしていく。

            中央には要求される特性がある。
            発想で広がったニーズから求められる特性と応用で広がったシーズ技術、製品、サービスが提供できる特性が
            中央の要求特性にある多数のキーワードを介してつながる構成。
            部分的に接続しないキーワードがあってもよい。接続できなくても重要と思われるキーワードは残す。

            ##ニーズ/ターゲットにする製品、ユーザー層、用途：{prompt1}
            ##シーズ/保有している技術、製品、サービス：：{prompt2}

            ##キーワード名のルール
            ・各グループで出た単語は、他のグループでは使用しない。
            ・単語が重ならないよう、生成後にチェックし、重複があれば修正する。
            ・どうしても同じ概念が含まれる場合、異なる表現や言い換えを行う。
            ・【ニーズの発想】例：○○しない、△△できる、□□用途 などの言葉を使う。
            ・【シーズの応用】例：△△技術、□□サービス、○○の向上、▼▼の活用 などの言葉を使う。
            ・【要求特性】例：高耐久、軽量、○○性、□□化 などの言葉を使う。
            ・キーワードの名前には( 、 ) 、 [ 、]、【、】、/、・、~などの記号や特殊な文字は使わない。必要な時は「_」に置き換える。

            #留意点、指針、参考知識：：{prompt3}

            #手順1、ニーズの発想
            設定されたニーズから利用シーンや用途、求められる特性を発想して様々なキーワードを提案していく(ニーズの第1層)。
　　　　　　「ニーズの第1層」のキーワードからさらに利用シーンや求められる特性を発想する(ニーズの第2層)。
　　　　　　「ニーズの第2層」で出力する単語は、「ニーズの第1層」で出た単語と絶対に重複しないように作成。
　　　　　　「ニーズの第2層」のキーワードから「ニーズの要求特性」の候補を発想して出力する。
　　　　　　「ニーズの要求特性」で出力する単語は、「ニーズの第1層」、「ニーズの第2層」で出た単語と絶対に重複しないように作成。
            発想は柔軟で独創的なものを重視する。

            #手順2、シーズの応用
            設定されたシーズを応用して開発できる技術、または提供できるサービスを提案する(シーズの第1層)。
　　　　　　「シーズの第1層」で出力する単語は、「ニーズの第1層」、「ニーズの第2層」、「要求特性」で出た単語と絶対に重複しないように作成。
　　　　　　「シーズの第1層」からさらに応用、または組み合わせて開発できる技術、製品、サービスを提案する(シーズの第2層)。
　　　　　　「シーズの第2層」で出力する単語は、「ニーズの第1層」、「ニーズの第2層」、「要求特性」、「シーズの第1層」で出た単語と絶対に重複しないように作成。
　　　　　　「シーズの第2層」が提供できる「シーズの要求特性」の候補を発想して出力する。
　　　　　　「シーズの要求特性」で出力する単語は、「ニーズの第1層」、「ニーズの第2層」、「シーズの第1層」、「シーズの第2層」で出た単語と絶対に重複しないように作成。
　　　　　　「シーズの要求特性」で出力する単語は、「ニーズの要求特性」の単語となるべく同じ言葉にする。

            シーズの応用は単純な転換ではなく、柔軟で独創的なものを重視する。
            「シーズの第1層」を基に「シーズの第2層」はより多くの技術や製品を産み出す。

            #手順3、ニーズとシーズに共通する「要求特性」の抽出
            ニーズの発想とシーズの応用の出力結果から、どのような「要求特性」が両者に共通するか考察する。
            共通する「要求特性」をマインドマップに記載する項目として抽出する。
　　　　　　競争力を高めるために、独自性の見られるものや差別化が行える項目を重要視してとりあげる。
　　　　　　重要な項目は共通していなくても抽出する。
　　　　　　共通しておらず接続できる項目がないか少ない場合は、不足部分を埋めるために
            ニーズ側の要求特性と繋げられるシーズ応用や、シーズ側の要求特性と繋げられるニーズ発想を追加していく。
　　　　　　類似したキーワードは統合して簡潔で見やすい構成にする。
　　　　　　「要求特性」で出力する単語は、「ニーズの第1層」、「ニーズの第2層」、「シーズの第1層」、「シーズの第2層」で出た単語と絶対に重複しないように作成。

　　　　　　ここまでの回答結果を基に、マインドマップで描画する各層のキーワードを決定し出力する。

            #手順4、項目名のチェック
            「ニーズの第1層」、「ニーズの第2層」、「要求特性」、「シーズの第2層」、「シーズの第1層」のキーワードを合わせ、同じ単語があるか全て確認する。
            同じ単語は全て重ならないように違う言葉に修正して出力する。
            単語の重複がないように必ず全てチェックして修正する。

            #手順5、マインドマップ構成の決定とMermaidのオブジェクト図の作成
            ここまで出力した内容を基に「マインドマップの形式」に沿ってマインドマップの構成を決定し、
            その構成を描画するMermaidのオブジェクト図を作成するコードを出力する。

            Mermaidのコード部分は「```mermaid」と「```」で囲むことで明示します。
            オブジェクト図は左から右に並べる構成にするので、最初に必ず「flowchart LR」を記述する。
            設定したニーズを左端として、「ニーズ」、「ニーズの第1層」、「ニーズの第2層」、「要求特性」の順にそれぞれのキーワードを接続する。
            「要求特性」から「シーズの第2層」「シーズの第1層」の順にそれぞれ接続されて「設定したシーズ」に接続し収束する
            ＊重要：Mermaidの接続関係は「<==」を使えません。シーズグループの接続関係は必ず「<==>」を使ってください


            ##mermaidコード部分の出力例(ニーズ：「日常で気軽に持ち運べる」、シーズ：「ニッケル水素電池」の場合)##
            ```mermaid
            flowchart LR
            %% テーマ設定
            classDef default fill:#f0f0f0,stroke:#555,stroke-width:4px,font-weight: bold,font-size: 20px;

            %% ニーズ側
            subgraph "ニーズの展開"
            %% 設定したニーズ==>ニーズの第1層
                日常生活で気軽に持ち運べる ==> 外出先で使う
                日常生活で気軽に持ち運べる ==> いつでも使える
                日常生活で気軽に持ち運べる ==> トラブル対応
            %% ニーズの第1層==>ニーズの第2層
                外出先で使う ==> モバイル機器用電源
                外出先で使う ==> ポータブル家電用電源
                いつでも使える ==> 超省電力
                いつでも使える ==> 繰り返し長く使える
                トラブル対応 ==> 非常用電源


            end
            %% ニーズの第2層==>要求特性
                モバイル機器用電源 ==> 軽量性
                モバイル機器用電源 ==> 高出力
                ポータブル家電用電源 ==> 長寿命
                ポータブル家電用電源 ==> 安全性
                ポータブル家電用電源 ==> 多様な出力電圧
                超省電力 ==> 急速充電
                超省電力 ==> 信頼性
                繰り返し長く使える ==> 信頼性
                繰り返し長く使える ==> 耐衝撃性
                非常用電源 ==> 耐衝撃性
                非常用電源 ==> 携帯性

            %% 求められる特性
            subgraph "要求特性"
                軽量性
                高出力
                長寿命
                安全性
                多様な出力電圧
                急速充電
                信頼性
                耐衝撃性
                携帯性
            end

            %% 要求特性==>シーズの第2層
            軽量性 ==> 高エネルギー密度
            軽量性 ==> 小型パッケージ技術
            高出力 ==> 高電流放電特性
            長寿命 ==> サイクル寿命向上
            安全性 ==> 過充電防止機能
            安全性 ==> 短絡防止機能
            多様な出力電圧 ==> DC-DCコンバータ技術
            急速充電 ==> 高速充電技術
            信頼性 ==> 安定した出力
            信頼性 ==> 自己診断機能
            耐衝撃性 ==> 堅牢な構造設計
            携帯性 ==> 軽量コンパクト設計

            %% シーズ側
            subgraph "保有技術"
            %% シーズの第2層<==>シーズの第1層
                高エネルギー密度 <==> 高密度化技術
                小型パッケージ技術 <==> 高密度化技術
                高電流放電特性 <==> 電極材料改良
                サイクル寿命向上 <==> 電解液改良
                過充電防止機能 <==> 回路設計技術
                短絡防止機能 <==> 回路設計技術
                DC-DCコンバータ技術 <==> 回路設計技術
                高速充電技術 <==> 充電制御技術
                安定した出力 <==> 電池管理システム
                自己診断機能 <==> 電池管理システム
                堅牢な構造設計 <==> 筐体設計技術
                軽量コンパクト設計 <==> 筐体設計技術

            %% シーズの第1層==>設定したシーズ技術
                高密度化技術 <==> ニッケル水素電池
                電極材料改良 <==> ニッケル水素電池
                電解液改良 <==> ニッケル水素電池
                回路設計技術 <==> ニッケル水素電池
                充電制御技術 <==> ニッケル水素電池
                電池管理システム <==> ニッケル水素電池
                筐体設計技術 <==> ニッケル水素電池
            end

            classDef needs fill:#e0f7fa,stroke:transparent,stroke-width:2px,font-weight: bold,font-size: 30px;
            class ニーズの展開 needs

            classDef property fill:transparent,stroke:transparent,stroke-width:2px,font-weight: bold,font-size: 30px;
            class 要求特性 property

            classDef seeds fill:#ffcccc,stroke:transparent,stroke-width:2px,font-weight: bold,font-size: 30px;
            class 保有技術 seeds
            ```

            """

            # Geminiでマインドマップのコードを生成
            response = model.generate_content(prompt)

            ## responseの結果を表示 エラー発生時のデバッグ用
            #st.write("### Geminiからの応答:")
            #st.write(response.text)

            # AIの応答を解説とMermaidコードに分割
            response_text, mermaid_code = extract_mermaid_code(response.text)


            # Mermaid形式のコードを抽出して整形
            #mermaid_code = response.text.strip()
            #if not mermaid_code.startswith('flowchart'):
            #    mermaid_code = 'flowchart LR\n' + mermaid_code
            
            # Mermaid APIのエンドポイント
            mermaid_api_url = "https://mermaid.ink/img/"
            
            # mermaidコードをbase64エンコード
            mermaid_code_bytes = mermaid_code.encode('utf-8')
            base64_code = base64.urlsafe_b64encode(mermaid_code_bytes).decode('utf-8')
            
            # 画像URLの生成
            img_url = f"{mermaid_api_url}{base64_code}"
            
            # 画像の取得と表示
            response = requests.get(img_url)
            if response.status_code == 200:
                # セッション状態に画像データとURLを保存
                st.session_state.img_data = response.content
                st.session_state.img_url = img_url
                st.session_state.mermaid_code = mermaid_code
                st.session_state.response_text = response_text

            else:
                st.session_state.img_data = []
                st.session_state.img_url = []
                st.session_state.mermaid_code = mermaid_code
                st.session_state.response_text = response_text
                st.error(f"画像の生成に失敗しました。コードとAIの回答を確認してください。ステータス: {response.status_code}")
        
        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")
    else:
        st.warning("入力データに不足があります")

               
# 現在の日時を使用してユニークなファイル名を生成
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# 画像の取得と表示
if st.session_state.img_data:
    # 生成されたマインドマップの表示
    st.image(st.session_state.img_url, caption="生成されたマップ", use_container_width=True)
 
    # 画像ダウンロードボタン
    st.download_button(
        label="マップをダウンロード",
        data=st.session_state.img_data,
        file_name=f"needs_map_{timestamp}.png",
        mime="image/png"
    )
                
if st.session_state.mermaid_code:
    # Mermaidコードの表示（オプション）
    with st.expander("描画コードを表示(Mermaid)"):
        st.code(st.session_state.mermaid_code, language="mermaid")

    # Mermaidコードダウンロードボタン
    st.download_button(
        label="描画コード ダウンロード",
        data=st.session_state.mermaid_code,
        file_name=f"needs_map_{timestamp}.txt",
        mime="text/plain"
    )

if st.session_state.response_text:
    # AIの解説部分の表示
    st.write("### AIの解説を表示:")
    st.write(st.session_state.response_text)

    # AIの解説ダウンロードボタン
    st.download_button(
        label="AIの解説 ダウンロード",
        data=st.session_state.response_text,
        file_name=f"AI_explanation_{timestamp}.txt",
        mime="text/plain"
    )



