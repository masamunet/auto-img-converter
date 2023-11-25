import requests
import json
import os
import hashlib
import time
import yaml
import argparse
import notify
import random
# 実行時間計測用のクラス
from Timer import Timer
import time
from time_estimator import TimeEstimator


uri = "http://localhost:7860"


def get_random_element(variable):
    """
    配列の場合はランダムな要素を、それ以外の場合はそのまま返します。

    Parameters:
        variable (any): 処理したい変数。

    Returns:
        any: 配列の場合はランダムな要素、それ以外の場合はそのままの値。
    """
    if isinstance(variable, list):
        if len(variable) > 0:
            return random.choice(variable)
        else:
            return None
    else:
        return variable


def swap_width_height(data_list):
    """
    辞書のリストから、'width'と'height'の値を入れ替えます。

    Parameters:
        data_list (list): 入れ替えを行いたい辞書のリスト。

    Returns:
        list: 'width'と'height'の値を入れ替えた辞書のリスト。
    """
    swapped_data = []
    for item in data_list:
        if 'width' in item and 'height' in item:
            swapped_item = item.copy()
            swapped_item['width'] = item['height']
            swapped_item['height'] = item['width']
            swapped_data.append(swapped_item)
        else:
            swapped_data.append(item.copy())
    return swapped_data


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
    """
    webui api にアクセスし、結果を返す
    """
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
    prompt = res_info["prompt"]
    negative_prompt = res_info["negative_prompt"]
    r_seed = res_info["seed"]
    return image_base64, r_seed, prompt, negative_prompt


def loopback(setting_params):
    infotexts = None
    image_base64 = None
    r_seed = None
    # プロンプトとネガティブプロンプトが配列だった場合はランダムな要素を取得する
    prompt = get_random_element(setting_params["f_prompt"])
    negative_prompt = get_random_element(
        setting_params["f_negative_prompt"])
    # もしサイズをランダムな縦横比にする設定だった場合は、ランダムな縦横比を取得する
    if setting_params.get('is_random_swap_width_height'):
        print('random swap size mode.')
        size = setting_params.get('size')
        if size is not None:
            # この部分で関数を実行するかどうかを決定します
            if random.random() < 0.5:
                print("swap size.")
                new_size = swap_width_height(size)
            else:
                print('nomal size.')
                new_size = size  # 関数を実行しない場合は、元のサイズをそのまま使用
            print("size:{}".format(new_size))
            setting_params['size'] = new_size
    # ループバックの回数だけループする
    max_count = len(setting_params["loopbacks"])
    for i in range(max_count):
        with Timer() as timer:
            # ループバックのパラメータを取得する
            loopback_params = setting_params["loopbacks"][i]
            # "is_enabled"がある場合
            if "is_enabled" in loopback_params and not loopback_params["is_enabled"]:
                # ループバックをスキップする
                continue
            endpoint = loopback_params["api_endpoint"]
            params = loopback_params["params"]
            params["prompt"] = prompt
            params["negative_prompt"] = negative_prompt
            if 'width' in params and 'width' in setting_params['size'][i]:
                params['width'] = setting_params['size'][i]['width']
                print("\twidth:{}".format(params['width']))
            if 'height' in params and 'height' in setting_params['size'][i]:
                params['height'] = setting_params['size'][i]['height']
                print('\theight:{}'.format(params['height']))
            print("\tloopback: {}/{}".format(i + 1, max_count))
            print("\tendpoint: {}".format(endpoint))
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

            image_base64, r_seed, res_prompt, res_negative_prompt = any2img(
                uri, endpoint, params)
            prompt = res_prompt
            negative_prompt = res_negative_prompt
        execution_time = timer.get_execution_time()
        print(f"\tLOOPBACK実行時間: {execution_time}")


def run(args):
    estimator = TimeEstimator(args.count)  # インスタンス生成、最大回数を引数に渡す
    estimator.start_process()  # 処理開始を記録

    # countの回数+1だけstart()を実行する
    for i in range(args.count):
        start_time = time.time()  # イテレーション開始時刻を記録
        with Timer() as timer:
            yaml_file = args.yaml_file
            print(yaml_file)
            print("count: {}/{}".format(i + 1, args.count))
            setting_params = load_yaml(yaml_file)
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
