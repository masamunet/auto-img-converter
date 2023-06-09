import requests
import json
import os
import hashlib
import time
import yaml
import argparse
import notify
# 実行時間計測用のクラス
from Timer import Timer
import time
from time_estimator import TimeEstimator


uri = "http://localhost:7860"


def load_yaml(yaml_file):
    """YAMLファイルを読み込み、辞書型に変換する関数"""
    with open(yaml_file, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data


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


def any2img(uri, endpoint, params):
    payload = params.copy()
    url = uri + endpoint
    image_base64, res_info = get_any2img(url, payload)
    infotexts = res_info["infotexts"]
    r_seed = res_info["seed"]
    return infotexts, image_base64, r_seed


def loopback(setting_params):
    infotexts = None
    image_base64 = None
    r_seed = None
    prompt = setting_params["f_prompt"]
    negative_prompt = setting_params["f_negative_prompt"]
    max_count = len(setting_params["loopbacks"])
    for i in range(max_count):
        with Timer() as timer:
            loopback_params = setting_params["loopbacks"][i]
            if "is_enabled" in loopback_params and not loopback_params["is_enabled"]:
                continue
            endpoint = loopback_params["api_endpoint"]
            params = loopback_params["params"]
            params["prompt"] = prompt
            params["negative_prompt"] = negative_prompt
            print("\tloopback: {}/{}".format(i + 1, max_count))
            print("\tendpoint: {}".format(endpoint))
            params["prompt"] = setting_params["f_prompt"]
            # print("params: {}".format(params))
            params["negative_prompt"] = setting_params["f_negative_prompt"]
            if r_seed is not None:
                if params["seed"] < 0:
                    params["seed"] = r_seed
            if "init_images" in loopback_params["params"]:
                params["init_images"] = [image_base64]
            # "alwayson_scripts"がある場合
            if "alwayson_scripts" in loopback_params["params"]:
                # "ControlNet"がある場合
                if "ControlNet" in loopback_params["params"]["alwayson_scripts"]:
                    # "input_image"がある場合
                    if "input_image" in loopback_params["params"]["alwayson_scripts"]["ControlNet"]["args"][0]:
                        # "input_image"を置き換える
                        loopback_params["params"]["alwayson_scripts"]["ControlNet"]["args"][0]["input_image"] = image_base64
                        # 新しい辞書をparams["alwayson_scripts"]["ControlNet"]に代入する
                        params["alwayson_scripts"]["ControlNet"] = loopback_params["params"]["alwayson_scripts"]["ControlNet"]

            infotexts, image_base64, r_seed = any2img(
                uri, endpoint, params)
            info_lines = infotexts[0].split("\n")
            prompt = info_lines[0]
            negative_prompt = info_lines[1].replace("Negative prompt: ", "")
        execution_time = timer.get_execution_time()
        print(f"\tLOOPBACK実行時間: {execution_time}")


def run(args):
    estimator = TimeEstimator(args.count)  # インスタンス生成、最大回数を引数に渡す
    estimator.start_process()  # 処理開始を記録

    # countの回数+1だけstart()を実行する
    for i in range(args.count):
        start_time = time.time()  # イテレーション開始時刻を記録
        with Timer() as timer:
            print("count: {}/{}".format(i + 1, args.count))
            setting_params = load_yaml(args.yaml_file)
            loopback(setting_params)
        execution_time = timer.get_execution_time()
        print(f"COUNT実行時間: {execution_time}")
        end_time = time.time()  # イテレーション終了時刻を記録
        iteration_time = end_time - start_time  # イテレーションにかかった時間を計算
        remaining_time, end_time = estimator.log_iteration(
            iteration_time)  # 残りの処理時間と終了予定時刻を取得
        print(f'残り時間: {remaining_time}, 終了時刻: {end_time}')  # 結果を表示
    print("Done!")
    try:
        notify.notify("処理が完了しました!")
    except:
        pass
    return


#  直接実行された場合、start(count, params)を実行
if __name__ == "__main__":
    # 引数の設定
    parser = argparse.ArgumentParser(
        description="Script to load parameters from YAML file.")
    parser.add_argument("-f", "--yaml_file", type=str,
                        default="params.yml", help="YAML file containing parameters")
    parser.add_argument("-c", "--count", type=int,
                        default=1, help="loopback count")
    args = parser.parse_args()
    run(args)
