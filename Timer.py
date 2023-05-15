import time


class Timer:
    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.execution_time = self.end_time - self.start_time

    def get_execution_time(self):
        hours = int(self.execution_time // 3600)
        minutes = int((self.execution_time % 3600) // 60)
        seconds = int(self.execution_time % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


if __name__ == "__main__":
    # 使用例
    with Timer() as timer:
        # 実行したいコードをここに書く
        time.sleep(2)
    # 実行時間を取得
    execution_time = timer.get_execution_time()
    print(f"実行時間: {execution_time}")
