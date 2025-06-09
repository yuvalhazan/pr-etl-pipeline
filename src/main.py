import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

import config
from extract import run_extract
from transform import run_transform


@dataclass
class Task:
    name: str
    func: Callable
    output_path: Path
    input_path: Path
    description: str = ""

    def __post_init__(self):
        if isinstance(self.output_path, str):
            self.output_path = Path(self.output_path)

    def prepare(self):
        self.output_path.parent.mkdir(parents=True, exist_ok=True)


class Pipeline:
    def __init__(self, tasks, run_timestamp: datetime = None, log_level=logging.INFO):
        self.run_timestamp = run_timestamp or datetime.now()
        self.logger = self._setup_logging(log_level)
        self.tasks = tasks

    def _setup_logging(self, level=logging.INFO):
        date_stamp = self.run_timestamp.strftime("%Y-%m-%d")
        time_stamp = self.run_timestamp.strftime("%H_%M_%S")
        log_file_path = Path(config.ROOT_LOG_DIR) / date_stamp / f"pipeline_{time_stamp}.log"
        log_file_path.parent.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(log_file_path, mode='w'),
            ],
            force=True,
        )
        logger = logging.getLogger(__name__)
        logger.info("=== LOGGING INITIALIZED ===")
        logger.info(f"Log file: {log_file_path}")
        return logger

    def run(self) -> bool:
        self.logger.info("===== Starting the data pipeline =====")
        self.logger.info(f"Number of tasks queued: {len(self.tasks)}")
        failed = []

        for idx, task in enumerate(self.tasks, 1):
            self.logger.info(f"--> Task {idx}/{len(self.tasks)}: {task.name}")
            if not self._execute(task):
                failed.append(task.name)
                break

        if failed:
            self.logger.error(f"Pipeline failed. Failed tasks: {failed}")
            return False

        self.logger.info("Pipeline completed successfully")
        return True

    def _execute(self, task: Task) -> bool:
        try:
            self.logger.info(f"--> Running: {task.name}")
            if task.description:
                self.logger.info(f"--> Info: {task.description}")

            task.prepare()
            task.func(task.output_path, task.input_path)

            self.logger.info(f"<-- Done: {task.name}")
            return True

        except Exception as e:
            self.logger.exception(f"Error during '{task.name}': {e}")
            return False


def create_tasks_github_pipeline(run_time) -> list[Task]:
    date_stamp = run_time.strftime("%Y-%m-%d")
    time_stamp = run_time.strftime("%H_%M_%S")

    return [
        Task(
            name="extract",
            func=run_extract,
            output_path=Path(config.ROOT_DATA_DIR/date_stamp/f"{time_stamp}_{config.EXTRACTED_FILE_NAME}"),
            input_path=Path(),
            description="Extract merged PR data from GitHub",
        ),
        Task(
            name="transform",
            func=run_transform,
            output_path=Path(config.ROOT_DATA_DIR/date_stamp/f"{time_stamp}_{config.PROCESSED_FILE_NAME}"),
            input_path=Path(config.ROOT_DATA_DIR/date_stamp/f"{time_stamp}_{config.EXTRACTED_FILE_NAME}"),
            description="Transform data into CSV",
        ),
    ]


if __name__ == "__main__":
    run_timestamp = datetime.now()

    pipeline = Pipeline(run_timestamp=run_timestamp, tasks=[])
    pipeline.tasks = create_tasks_github_pipeline(run_timestamp)

    success = pipeline.run()
    if not success:
        exit(1)
