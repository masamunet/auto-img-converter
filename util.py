import base64
from PIL import Image
import os
import base64


def get_files_in_directory(directory_path):
    """
    指定されたディレクトリの中のファイルのフルパスをリストにして返す。

    Args:
        directory_path (str): ディレクトリのパスの文字列。

    Returns:
        list: ディレクトリ内のファイルのフルパスのリスト。

    Raises:
        OSError: 指定されたディレクトリが存在しない場合に発生。
    """
    if not os.path.exists(directory_path):
        raise OSError(f"ディレクトリが存在しません: {directory_path}")

    file_list = []
    for filename in os.listdir(directory_path):
        # 隠しファイルは無視する
        if filename.startswith("."):
            continue
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            file_list.append(os.path.abspath(file_path))

    return file_list


def image_to_data_uri(file_path):
    """
    指定された画像ファイルをData URIに変換する。

    Args:
        file_path (str): 画像ファイルのパス。

    Returns:
        str: 変換されたData URI。

    Raises:
        FileNotFoundError: 指定されたパスに対応するファイルが存在しない場合。

    Example:
        >>> image_to_data_uri("image.png")
        'data:image/png;base64,iVBORw0KGg...'

    """
    # 画像ファイルをバイト列として読み込み
    try:
        with open(file_path, "rb") as image_file:
            image_bytes = image_file.read()
    except FileNotFoundError:
        raise FileNotFoundError("指定されたパスに対応するファイルが存在しません。")

    # 画像の形式を取得
    try:
        image_format = Image.open(file_path).format.lower()
    except:
        raise ValueError("画像ファイルの形式を取得できませんでした。")

    # バイト列をbase64エンコード
    base64_encoded_bytes = base64.b64encode(image_bytes)

    # Data URIを作成
    data_uri = "data:image/{0};base64,{1}".format(
        image_format, base64_encoded_bytes.decode("utf-8"))

    return data_uri


def save_base64_image_to_file(base64_string, output_dir, filename):
    """
    BASE64文字列をPNG画像に変換し、指定されたファイルパスに保存する。

    Args:
        base64_string (str): 変換元のBASE64文字列
        file_path (str): 保存先のファイルパス

    Returns:
        bool: 保存が成功した場合はTrue、失敗した場合はFalse
    """
    # Decode the base64 string into bytes
    image_bytes = base64.b64decode(base64_string)
    # create directory if it does not exist
    os.makedirs(output_dir, exist_ok=True)
    # decode base64 string and save to file
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "wb") as f:
        f.write(base64.b64decode(base64_string))
    return filepath
