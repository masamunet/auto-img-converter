import unittest
import time
from time_estimator import TimeEstimator


class TestTimeEstimator(unittest.TestCase):
    def test_time_estimator(self):
        estimator = TimeEstimator(5)
        estimator.start_process()

        for _ in range(5):
            start_time = time.time()
            time.sleep(1)  # 時間のかかる処理の代わり
            end_time = time.time()
            iteration_time = end_time - start_time

            remaining_time, end_time = estimator.log_iteration(iteration_time)

        # テスト：最後のイテレーション後の残り時間はほぼ0秒であるべき
        self.assertTrue("0:00:00" in remaining_time)

        # テスト：終了予定時刻は開始から約5秒後であるべき
        estimated_end_time = time.strftime(
            '%H:%M:%S', time.gmtime(time.time() + 5))
        self.assertEqual(end_time, estimated_end_time)


if __name__ == "__main__":
    unittest.main()
