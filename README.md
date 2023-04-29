# auto-img-converter

## これは何？
AUTOMATIC1111/stable-diffusion-webuiの、txt2imgを実行したあとに、そのままimg2imgに処理を渡してSDアップスケールを自動的に行うツールです。
実際にはwebuiのapiを叩いているので、txt2imgのあとに行う処理はSDアップスケールに限らず、webuiでできることは何でもできますが、いったんツールとしての説明は、txt2imgのあとにimg2imgのSDアップスケールを行うツールとしての説明だけにとどめておきます。

## 動作必要環境

+ [AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui)が適切にインストールされていて起動できる
+ なおかつAUTOMATIC1111/stable-diffusion-webuiのAPIモードが起動できている。APIモードの起動については[API · AUTOMATIC1111/stable\-diffusion\-webui Wiki](https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/API)をご覧下さい
+ AUTOMATIC1111/stable-diffusion-webuiのプラグイン、[sd\-dynamic\-prompts](https://github.com/adieyal/sd-dynamic-prompts)が適切にインストールされている
+ AUTOMATIC1111/stable-diffusion-webuiのプラグイン、[ultimate\-upscale](https://github.com/Coyote-A/ultimate-upscale-for-automatic1111)が適切にインストールされている

## 使い方

　このツールはPythonで実行します。AUTOMATIC1111/stable-diffusion-webuiがAPIモードで適切に起動できている時点で、このツールを実行するためのPythonの環境は整っていると言えますので、Pythonの環境構築の説明については省きます。

　まずはprompy.ymlをエディターで開いてください。実行に必要なパラメーターを設定します。countとis_upscaleはツール独自のパラメーターなので、prompt.ymlに書かれてあるコメントを参考に設定してください。
それ以外のパラメーターについては、webuiを使っていればだいたい何の数値かわかると思いますので、必要なだけ調整してください。

　prompt.ymlにあらかじめ書かれていない、必要だと思う数値については[txt2imgの場合はこちら](http://127.0.0.1:7860/docs#/default/text2imgapi_sdapi_v1_txt2img_post)、[img2imgの場合はこちら](http://127.0.0.1:7860/docs#/default/img2imgapi_sdapi_v1_img2img_post)を参考にしてください。この2つのリンク先は、いずれもローカルで立ち上げているwebuiのAPIのドキュメントが開くはずです（設定を変えていなければ。変えていればその設定にしたがって適宜URLを置き換えて開いてください）。

　sd-dynamic-promptの設定については、sd-dynamic-promptのバージョンの記述が必要なため、 ＜stable-diffusion-webuiのインストールパス＞/extensions/sd-dynamic-prompts/sd_dynamic_prompts/__init__.py に書かれてある、バージョン情報を参考に記述してください。

## 実行

```bash
python3 run.py
```

で実行します。
prompt.yml以外の設定ファイルを使いたいときは、

```bash
python run.py --yaml_file ＜設定ファイルの指定＞
```

と指定してください。
prompt_*.ymlといったファイル名にしておけば、デフォルトでgit除外ファイルとして指定されているので、自分のバリエーションに合わせた設定ファイル管理ができて便利です。