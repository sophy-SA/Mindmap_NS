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
#ニーズ層とシーズ層の層数など構成を定義
#発想の手順を洗練させた改良バージョン
# 既出の単語を使わないように命名規則(グループ毎の接頭辞を追加)
# + 重複のチェックや制限を無くしてその分発想の追加などが働くようにした

#AIの応答を複数回に分けたVer
#発想の量は大幅に増えた
#マーメイドコードの分離ルーチンを削除、出力例を追加、要求特性の接続を柔軟に
#

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
st.title("ニーズとシーズの深堀りマップ_弐")

# セッション状態の初期化
if 'img_data' not in st.session_state:
    st.session_state.img_data = None
if 'img_url' not in st.session_state:
    st.session_state.img_url = None
if 'mermaid_code' not in st.session_state:
    st.session_state.mermaid_code = None
if 'response_text1' not in st.session_state:
    st.session_state.response_text1 = None
if 'response_text2' not in st.session_state:
    st.session_state.response_text2 = None


# 入力フォームの作成
prompt1 = st.text_input("ターゲットにする製品/用途/購買層を入力：　例) □□向け、○○を△△する、○○用品など")
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
            ターゲットが求めている本質的な価値を見出すため、ニーズから利用シーンや用途、特徴を発想してください。
            発想は柔軟で独創的なものを重視し、なるべく多くのキーワードを発想する。
            
            ##ニーズ/ターゲットにする製品、ユーザー層、用途：{prompt1}
            
            #手順1、第1層のニーズの発想
            ターゲットニーズ「{prompt1}」から利用シーンや用途、特徴を発想して様々なキーワードを提案して出力する。
            ここで提案されたキーワードを「ニーズの第1層」と呼ぶ。
            
            #手順2、第2層のニーズの発想
            「ニーズの第1層」のキーワードからさらに新たな利用シーンや用途を発想して出力する。
            ここで提案されたキーワードを「ニーズの第2層」と呼ぶ。
            
            #手順3、ニーズの要求特性
            「ニーズの第2層」のキーワードから「ニーズの要求特性」の候補をたくさん発想して出力する。

            ##キーワード名のルール
            ・ニーズの発想グループは利用シーンや用途、特徴を表す単語を使う。(例：○○しない、△△できる、□□用途 など)。
            ・「ニーズの第1層」の単語は前に"i"、「ニーズの第2層」の単語は前に"l"、をつける
            ・「ニーズの要求特性」のグループは特性や性質を表す単語を使う。(例：高耐久、軽量、○○性、□□化 など)。
            ・キーワードの名前には( 、 ) 、 [ 、]、【、】、/、・、~などの記号や特殊な文字は使わない。これらを使う時は「_」に置き換える。
            ・空白やスペースは表示エラーになるので絶対に使わない。「 」を使うときは「_」に置き換える。

            #留意点、指針、参考知識：：{prompt3}
            
            #出力例#
            
            **設定されたニーズ：〇〇**
            
            **ニーズの第1層**
            
            *   i手軽に始める
            *   i専門知識不要
            *   i結果がすぐ見える
            *   i自分のペースで
            *   i最新技術に触れる
            
            **ニーズの第2層**
            
            *   i手軽に始める ==> l無料トライアル
            *   i手軽に始める ==> l初期設定不要
            *   i専門知識不要 ==> l直感的な操作
            *   i専門知識不要 ==> l専門用語を使わない
            *   i結果がすぐ見える ==> lデモ体験
            *   i結果がすぐ見える ==> l成功事例紹介
            *   i自分のペースで ==> l個別指導
            *   i自分のペースで ==> l質問しやすい環境
            *   i最新技術に触れる ==> l業界トレンド解説
            *   i最新技術に触れる ==> l応用事例紹介
            
            **ニーズの要求特性**
            
            *   無料トライアル ==> 低コスト
            *   無料トライアル ==> 短時間
            *   初期設定不要 ==> 簡単操作
            *   初期設定不要 ==> 高速起動
            *   直感的な操作 ==> 使いやすさ
            *   直感的な操作 ==> 視覚的な分かりやすさ
            *   専門用語を使わない ==> 理解しやすさ
            *   専門用語を使わない ==> 親しみやすさ
            
            """

            # AIの回答結果を格納
            response_1st = model.generate_content(prompt).text


            prompt_2nd = f"""
            ##指示
            あなたは優秀なプロダクト開発支援のプロコンサルタントです。
            シーズ技術が顧客に提供できる本質的な価値や強味と有望なターゲットを見出すため、
            シーズを応用、または組み合わせて開発できる製品、技術や提供できるサービスを発想してください。
            シーズ応用の発想は単純な転換ではなく、柔軟で独創的なものをなるべく多く発想します。
            
            ##シーズ/保有している技術、製品、サービス：：{prompt2}
            
            #手順1、第1層のシーズの応用
            シーズ技術「{prompt2}」から開発または提供できる様々な技術、製品やサービスを提案して出力する。
            ここで提案されたキーワードを「シーズの第1層」と呼ぶ。
            
            #手順2、第2層のシーズの応用
            「シーズの第1層」のキーワードからさらに多くの技術や製品、サービスを産み出す。
            ここで提案されたキーワードを「シーズの第2層」と呼ぶ。
            
            #手順3、シーズの要求特性
            「シーズの第2層」が提供できる「シーズの要求特性」の候補をたくさん発想して出力する。

            ##キーワード名のルール
            ・シーズの応用グループは技術やサービス、性能、機能を表す単語を使う。(例：△△技術、□□サービス、○○の向上、▼▼の活用 など)。
            ・「シーズの第1層」の単語は前に"o"、「シーズの第2層」の単語は前に"r"、をつける
            ・「シーズの要求特性」のグループは特性や性質を表す単語を使う。(例：高耐久、軽量、○○性、□□化 など)。
            ・キーワードの名前には( 、 ) 、 [ 、]、【、】、/、・、~などの記号や特殊な文字は使わない。これらを使う時は「_」に置き換える。
            ・空白やスペースは表示エラーになるので絶対に使わない。「 」を使うときは「_」に置き換える。

            #留意点、指針、参考知識：：{prompt3}
            
            
            #出力例#
            
            **設定されたシーズ：△△**
            
            **シーズの第1層**
            
            *   o個別最適化された学習プラン
            *   o対話型コーチング
            *   o実践的な課題
            *   o最新モデルへの対応
            *   oコミュニティサポート
            
            **シーズの第2層**
            
            *   o個別最適化された学習プラン ==> r進捗管理システム
            *   o個別最適化された学習プラン ==> rスキル診断
            *   o対話型コーチング ==> r自然言語処理
            *   o対話型コーチング ==> rリアルタイムフィードバック
            *   o実践的な課題 ==> rAPI連携
            *   o実践的な課題 ==> r実データ活用
            *   o最新モデルへの対応 ==> r継続的なアップデート
            *   o最新モデルへの対応 ==> rバージョン管理
            *   oコミュニティサポート ==> rQ&Aフォーラム
            *   oコミュニティサポート ==> r成果発表の場
            
            **シーズの要求特性**
            
            *   進捗管理システム ==> 可視化
            *   スキル診断 ==> 個別最適化
            *   自然言語処理 ==> 理解しやすさ
            *   リアルタイムフィードバック ==> 即時性
            *   API連携 ==> 拡張性
            *   実データ活用 ==> 実用性
            *   継続的なアップデート ==> 最新情報
            *   バージョン管理 ==> 安全性
            *   Q&Aフォーラム ==> 疑問解決
            *   成果発表の場 ==> モチベーション向上
            *   成果発表の場 ==> コミュニティ
            *   スキル診断 ==> 丁寧なサポート
            
            """
            
            # AIの回答結果を格納
            response_2nd = model.generate_content(prompt_2nd).text


            # プロンプトの作成(3rd)
            prompt_3rd = f"""
            ##指示
            あなたは優秀なプロダクト開発支援のプロコンサルタントです。
            ニーズにマッチし、且つ自社のコア技術を活かせる開発方針やテーマを見出すマインドマップを作成するため、
            ニーズが求める特性とシーズが提供できる特性のマッチングを考察します。
            開発において競争力を向上させ、他社に模倣されないために重要なキーワードも抽出します。
            
            ##ニーズ/ターゲットにする製品、ユーザー層、用途：{prompt1}
            ##シーズ/保有している技術、製品、サービス：：{prompt2}
            
            ##ニーズから発想された利用シーンや用途、特徴：
            {response_1st}
            
            ##シーズ応用で提供できる製品、技術や提供できるサービス：
            {response_2nd}
            
            #手順1、ニーズとシーズに共通する「要求特性」の抽出
            ニーズの発想とシーズの応用の項目から、どのような「要求特性」が両者に共通しているか考察し、
            共通する「要求特性」をキーワードとして抽出する。
            競争力を高めるため、独自性のあるものや差別化が行える項目を重要視してとりあげる。
            差別化に重要と思われる項目は共通していなくても抽出して出力する。

            #手順2、「要求特性」からの発想の追加
            共通しておらず接続できない「ニーズの要求特性」について、可能なら、これと繋げられるシーズ応用の発想を追加する。
            既存のキーワードにつなげられるものがあれば接続する。
            新たな「シーズの第2層」を追加して既存の「シーズの第1層」とつなげても良い。
            または「シーズの第2層」⇒「シーズの第1層」の順に逆に発想して出力する。
            
            共通しておらず接続できない「シーズの要求特性」について、可能なら、これと繋げられるニーズの発想を追加する。
            既存のキーワードにつなげられるものがあれば接続する。
            新たな「ニーズの第2層」を追加して既存の「ニーズの第1層」とつなげても良い。
            または「ニーズの第2層」⇒「ニーズの第1層」の順に逆に発想して出力する。

            ここまでの回答結果を基に、マインドマップで描画する各層のキーワードを決定し出力する。
            
            ##キーワード名のルール
            ・各キーワードは、どのグループに属した単語であるか分かりやすい語句を選択する
            ・ニーズの発想グループは利用シーンや用途、特徴を表す単語を使う。(例：○○しない、△△できる、□□用途 など)。
            ・「ニーズの第1層」の単語は前に"i"、「ニーズの第2層」の単語は前に"l"、をつける
            ・シーズの応用グループは技術やサービス、性能、機能を表す単語を使う。(例：△△技術、□□サービス、○○の向上、▼▼の活用 など)。
            ・「シーズの第1層」の単語は前に"o"、「シーズの第2層」の単語は前に"r"、をつける
            ・要求特性のグループは特性や性質を表す単語を使う。(例：高耐久、軽量、○○性、□□化 など)。
            ・キーワードの名前には( 、 ) 、 [ 、]、【、】、/、・、~などの記号や特殊な文字は使わない。これらを使う時は「_」に置き換える。
            ・空白やスペースは表示エラーになるので絶対に使わない。「 」を使うときは「_」に置き換える。

            #留意点、指針、参考知識：：{prompt3}
            
            
            """
            
            # AIの回答結果を格納
            response_3rd = model.generate_content(prompt_3rd).text
            
            
            # プロンプトの作成(4th)
            prompt_4th = f"""
            ##指示
            あなたは優秀なプロダクト開発支援のプロコンサルタントです。
            ターゲットのニーズに向けた保有技術の進化や発展の方向を考察し、プロダクト開発のアドバイスを行います。
            
            ##ニーズ/ターゲットにする製品、ユーザー層、用途：{prompt1}
            ##シーズ/保有している技術、製品、サービス：：{prompt2}
            
            ##ニーズの発想とシーズの応用、ニーズとシーズに共通する「要求特性」：
            {response_3rd}

            #手順1、顧客価値の創出に関する解説と指針だし
            入力されたニーズ、シーズ、と要求特性から顧客価値の創出について分析し、下記の内容について提案を行って出力する。

            ・シーズ技術が顧客に提供できる本質的な価値や強味と有望なターゲット
            ・市場ニーズからみたターゲット層が求めている価値と有効な技術やサービス
            ・ニーズにマッチし、且つ自社のコア技術を活かせる開発方針やテーマ
            ・開発において競争力を向上させ、他社に模倣されないための留意点

            #留意点、指針、参考知識：：{prompt3}
            
            """
            
            # # AIの回答結果を格納
            response_4th = model.generate_content(prompt_4th).text
            
            # プロンプトの作成(fina;)
            prompt_fin = f"""
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
            
            ##ニーズから発想された利用シーンや用途、特徴：
            {response_1st}
            
            ##シーズ応用で提供できる製品、技術や提供できるサービス：
            {response_2nd}
            
            ##ニーズの発想とシーズの応用、ニーズとシーズに共通する「要求特性」：
            {response_3rd}

            ##キーワード名のルール
            ・「ニーズの第1層」の単語は前に"i"、「ニーズの第2層」の単語は前に"l"、がついている
            ・「シーズの第1層」の単語は前に"o"、「シーズの第2層」の単語は前に"r"、がついている

            #留意点、指針、参考知識：：{prompt3}

            #手順1、マインドマップ構成の決定とMermaidのオブジェクト図の作成
            マインドマップで記載するキーワードのリストを基に「マインドマップの形式」に沿ってマインドマップの構成を決定する。
            決定したマインドマップを描画するMermaidのオブジェクト図を作成するコードを出力する。コード以外は出力しない。

            Mermaidのコード部分は「```mermaid」と「```」で囲むことで明示します。
            オブジェクト図は左から右に並べる構成にするので、最初に必ず「flowchart LR」を記述する。
            設定したニーズを左端として、「ニーズ」、「ニーズの第1層」、「ニーズの第2層」、「要求特性」の順にそれぞれのキーワードを接続する。
            「要求特性」から「シーズの第2層」「シーズの第1層」の順にそれぞれ接続されて「設定したシーズ」に接続し収束する。
            ＊重要：Mermaidの接続関係は「<==」を使えない。シーズグループの接続関係は必ず「<==>」を使うこと。


            ##mermaidコード部分の出力例(ニーズ：「日常で気軽に持ち運べる」、シーズ：「ニッケル水素電池」の場合)##
            ```mermaid
            flowchart LR
            %% テーマ設定
            classDef default fill:#f0f0f0,stroke:#555,stroke-width:4px,font-weight: bold,font-size: 20px;

            %% ニーズ側
            subgraph "ニーズの展開"
            %% 設定したニーズ==>ニーズの第1層
                日常生活で気軽に持ち運べる ==> i外出先で使う
                日常生活で気軽に持ち運べる ==> iいつでも使える
                日常生活で気軽に持ち運べる ==> iトラブル対応
            %% ニーズの第1層==>lニーズの第2層
                i外出先で使う ==> lモバイル機器用電源
                i外出先で使う ==> lポータブル家電用電源
                iいつでも使える ==> l超省電力
                iいつでも使える ==> l繰り返し長く使える
                iトラブル対応 ==> l非常用電源


            end
            %% ニーズの第2層==>要求特性
                lモバイル機器用電源 ==> 軽量性
                lモバイル機器用電源 ==> 高出力
                lポータブル家電用電源 ==> 長寿命
                lポータブル家電用電源 ==> 安全性
                lポータブル家電用電源 ==> 多様な出力電圧
                l超省電力 ==> 急速充電
                l超省電力 ==> 信頼性
                l繰り返し長く使える ==> 信頼性
                l繰り返し長く使える ==> 耐衝撃性
                l非常用電源 ==> 耐衝撃性
                l非常用電源 ==> 携帯性

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
            軽量性 ==> r高エネルギー密度
            軽量性 ==> r小型パッケージ技術
            高出力 ==> r高電流放電特性
            長寿命 ==> rサイクル寿命向上
            安全性 ==> r過充電防止機能
            安全性 ==> r短絡防止機能
            多様な出力電圧 ==> rDCコンバータ技術
            急速充電 ==> r高速充電技術
            信頼性 ==> r安定した出力
            信頼性 ==> r自己診断機能
            耐衝撃性 ==> r堅牢な構造設計
            携帯性 ==> r軽量コンパクト設計

            %% シーズ側
            subgraph "保有技術"
            %% シーズの第2層<==>シーズの第1層
                r高エネルギー密度 <==> o高密度化技術
                r小型パッケージ技術 <==> o高密度化技術
                r高電流放電特性 <==> o電極材料改良
                rサイクル寿命向上 <==> o電解液改良
                r過充電防止機能 <==> o回路設計技術
                r短絡防止機能 <==> o回路設計技術
                rDCコンバータ技術 <==> o回路設計技術
                r高速充電技術 <==> o充電制御技術
                r安定した出力 <==> o電池管理システム
                r自己診断機能 <==> o電池管理システム
                r堅牢な構造設計 <==> o筐体設計技術
                r軽量コンパクト設計 <==> o筐体設計技術

            %% シーズの第1層==>設定したシーズ技術
                o高密度化技術 <==> ニッケル水素電池
                o電極材料改良 <==> ニッケル水素電池
                o電解液改良 <==> ニッケル水素電池
                o回路設計技術 <==> ニッケル水素電池
                o充電制御技術 <==> ニッケル水素電池
                o電池管理システム <==> ニッケル水素電池
                o筐体設計技術 <==> ニッケル水素電池
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
            response_fin = model.generate_content(prompt_fin).text
            
            
            response_text1 = "\n".join([response_1st, response_2nd, response_3rd])
            response_text2 = response_4th
            mermaid_code = response_fin
            
            #デバッグ確認用
            #st.write("1st")
            #st.write(response_1st)
            #st.write("2nd")
            #st.write(response_2nd)
            #st.write("3rd")
            #st.write(response_3rd)
            #st.write("4th")
            #st.write(response_4th)
            
            ## responseの結果を表示 エラー発生時のデバッグ用
            #st.write("### Geminiからの応答:")
            #st.write(response.text)

            # AIの応答を解説とMermaidコードに分割
            #response_text1, response_text2, mermaid_code = extract_mermaid_code(response.text)


            # Mermaid形式のコードを抽出して整形
            #mermaid_code = response.text.strip()
            mermaid_code = mermaid_code.strip()
            
            mermaid_code = mermaid_code.split("```mermaid")[1].split("```")[0].strip()
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
                st.session_state.response_text1 = response_text1
                st.session_state.response_text2 = response_text2

            else:
                st.session_state.img_data = []
                st.session_state.img_url = []
                st.session_state.mermaid_code = mermaid_code
                st.session_state.response_text1 = response_text1
                st.session_state.response_text2 = response_text2
                st.error(f"画像の生成に失敗しました。コードとAIの回答を確認してください。ステータス: {response.status_code}")
        
        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")
    else:
        st.warning("未入力の項目があります")

               
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

# AIの解説部分の表示とダウンロード
if 'response_text2' in st.session_state and st.session_state.response_text2:
    st.write(st.session_state.response_text2)

    st.download_button(
        label="分析結果のダウンロード",
        data=st.session_state.response_text2,
        file_name=f"ai_explanation_part2_{timestamp}.txt",
        mime="text/plain"
    )


if 'response_text1' in st.session_state and st.session_state.response_text1:
    with st.expander("ニーズ/シーズの種だし部分を表示"):
        st.text(st.session_state.response_text1)

    st.download_button(
        label="種だし部分のダウンロード",
        data=st.session_state.response_text1,
        file_name=f"ai_explanation_part1_{timestamp}.txt",
        mime="text/plain"
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


