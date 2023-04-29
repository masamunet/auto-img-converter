import requests
import json
import os
import hashlib
import time
import yaml
import argparse

setting_params = {}

uri = "http://127.0.0.1:7860"


def get_hash(data):
    """与えられたデータのSHA256ハッシュを計算し、16進数文字列として返す関数"""
    data_str = str(data)
    sha256_hash = hashlib.sha256(data_str.encode('utf-8')).hexdigest()
    return sha256_hash[:8]


def get_current_milliseconds():
    """現在のミリ秒を取得する関数"""
    return int(round(time.time() * 1000))


def get_full_path(relative_path):
    """相対パスからフルパスを取得する関数"""
    return os.path.abspath(relative_path)


def access_api(url, payload):
    # リクエストヘッダーにContent-Typeを指定する
    headers = {
        "Content-Type": "application/json",
        "accept": "application/json"
    }

    # POSTリクエストを送信する
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    return response


# access_apiのラッパー。webui api にアクセスし、結果を返す
def get_any2img(url, payload):
    response = access_api(url, payload)
    # レスポンスのステータスコードを確認する
    if response.status_code == 200:
        # レスポンスが正常な場合、レスポンスボディを出力する
        res_json = response.text
        res_dict = json.loads(res_json)
        res_info = json.loads(res_dict['info'])
        image_base64 = res_dict['images'][0]
        return image_base64, res_info
    else:
        # レスポンスがエラーの場合、エラーメッセージを出力する
        print("Error: {}".format(response.text))
        return None, None


def txt2img(params, txt2img_params):
    """txt2imgを実行し、結果を返す関数"""
    payload = params.copy()
    payload["alwayson_scripts"] = txt2img_params["alwayson_scripts"]
    url = uri + "/sdapi/v1/txt2img"
    image_base64, res_info = get_any2img(url, payload)
    infotexts = res_info["infotexts"]
    r_seed = res_info["seed"]
    return payload, infotexts, image_base64, r_seed


def img2img(payload, img2img_params, image64, seed, prompt, negative_prompt):
    """
    """
    payload["init_images"] = [image64]
    payload["prompt"] = prompt
    payload["negative_prompt"] = negative_prompt.replace(
        "Negative prompt: ", "")
    payload["seed"] = seed
    payload["denoising_strength"] = img2img_params["denoising_strength"]
    payload["script_name"] = ""
    payload["script_name"] = img2img_params["script_name"]
    payload["script_args"] = img2img_params["script_args"]
    url = uri + "/sdapi/v1/img2img"
    image_base64, res_info = get_any2img(url, payload)
    infotexts = res_info["infotexts"]
    r_seed = res_info["seed"]
    return payload, infotexts, r_seed


def start():
    payload, infotexts, image_base64, seed = txt2img(
        setting_params["params"], setting_params["txt2img_params"])
    info_lines = infotexts[0].split("\n")
    if setting_params["is_upscale"]:
        payload, infotexts, seed = img2img(payload, setting_params["img2img_params"], image_base64, seed,
                                           info_lines[0], info_lines[1])
        info_lines = infotexts[0].split("\n")
    return


def run():
    # countの回数+1だけstart()を実行する
    for i in range(setting_params["count"]):
        print("count: {}".format(i))
        start()
    print("Done!")
    return


#  直接実行された場合、start(count, params)を実行
if __name__ == "__main__":
    # 引数の設定
    parser = argparse.ArgumentParser(
        description="Script to load parameters from YAML file.")
    parser.add_argument("-f", "--yaml_file", type=str,
                        default="params.yml", help="YAML file containing parameters")
    args = parser.parse_args()
    with open(args.yaml_file, 'r') as stream:
        try:
            setting_params = yaml.safe_load(stream)
            setting_params["params"]["prompt"] = setting_params["prompt"]
            setting_params["params"]["negative_prompt"] = setting_params["negative_prompt"]
        except yaml.YAMLError as exc:
            print(exc)
    run()
