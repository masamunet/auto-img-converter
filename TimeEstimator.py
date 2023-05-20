import time
import datetime


class TimeEstimator:
    """
    時間のかかる処理の進行状況と終了時刻の推定を行うクラス。

    Attributes:
        max_iterations (int): 処理の最大回数。
        start_time (float): 処理の開始時刻。
        current_iteration (int): 現在の処理回数。
    """

    def __init__(self, max_iterations):
        """
        TimeEstimatorのコンストラクタ。

        Args:
            max_iterations (int): 処理の最大回数。
        """
        self.max_iterations = max_iterations
        self.start_time = None
        self.current_iteration = 0

    def start_process(self):
        """
        処理の開始を記録するメソッド。処理開始前に呼び出す必要がある。
        """
        self.start_time = time.time()  # 処理開始時刻を記録

    def log_iteration(self, iteration_time):
        """
        各イテレーションの終了を記録し、全体の処理時間と終了時刻を推定するメソッド。

        Args:
            iteration_time (float): 1回のイテレーションにかかった時間（秒）。

        Returns:
            tuple of str: 残りの処理時間と終了予定時刻を表す文字列のタプル。
        """
        self.current_iteration += 1  # 処理回数を1つ増やす

        # 全体の処理時間を推定
        estimated_total_time = iteration_time * self.max_iterations

        # 残りの処理時間を計算
        remaining_time = estimated_total_time - \
            (self.current_iteration * iteration_time)

        # 処理終了予定時刻を計算
        end_time = self.start_time + \
            (self.current_iteration * iteration_time) + remaining_time

        # 残りの処理時間と終了予定時刻を文字列に変換
        remaining_time_str = str(
            datetime.timedelta(seconds=int(remaining_time)))
        end_time_str = datetime.datetime.fromtimestamp(
            end_time).strftime('%H:%M:%S')

        return remaining_time_str, end_time_str
