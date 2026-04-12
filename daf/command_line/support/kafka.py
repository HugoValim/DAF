#!/usr/bin/env python3

import argparse as ap

from daf.command_line.support.support_utils import SupportBase
from daf.utils.decorators import cli_decorator


class Kafka(SupportBase):
    DESC = """Configure Kafka settings for DAF scans"""
    EPI = """
    Eg:
       daf.kafka -b localhost:9092
       daf.kafka --server localhost:9092
       daf.kafka -l
        """

    def __init__(self):
        super().__init__()
        self.parsed_args = self.parse_command_line()
        self.parsed_args_dict = vars(self.parsed_args)

    def parse_command_line(self) -> ap.Namespace:
        super().parse_command_line()
        self.parser.add_argument(
            "-b",
            "--server",
            metavar="bootstrap servers",
            type=str,
            help="Kafka bootstrap servers (e.g., localhost:9092)",
        )
        self.parser.add_argument(
            "-l",
            "--list",
            action="store_true",
            help="list current Kafka configuration",
        )

        args = self.parser.parse_args()
        return args

    def run_cmd(self) -> None:
        if self.parsed_args_dict["list"]:
            self.list_kafka_config()
        elif self.parsed_args_dict["server"]:
            self.set_kafka_server()

    def list_kafka_config(self) -> None:
        """Display current Kafka configuration"""
        kafka_server = self.experiment_file_dict.get("kafka_server", "not configured")
        print(f"Kafka bootstrap servers: {kafka_server}")

    def set_kafka_server(self) -> None:
        """Set Kafka bootstrap servers in the experiment file"""
        kafka_server = self.parsed_args_dict["server"]
        self.experiment_file_dict["kafka_server"] = kafka_server
        self.write_to_experiment_file({}, is_kafka_config=True)
        print(f"Kafka bootstrap servers set to: {kafka_server}")

    def write_kafka_config_to_experiment_file(self, dict_to_write: dict) -> None:
        """Write Kafka config to the experiment file"""
        if (
            "kafka_server" in dict_to_write
            and dict_to_write["kafka_server"] is not None
        ):
            self.experiment_file_dict["kafka_server"] = dict_to_write["kafka_server"]

    def write_to_experiment_file(
        self,
        dict_to_write: dict,
        is_kafka_config: bool = False,
        write=True,
    ):
        """Write to the .Experiment file based on a inputted dict"""
        if is_kafka_config:
            self.write_kafka_config_to_experiment_file(dict_to_write)
        if write:
            self.io.write(self.experiment_file_dict)


@cli_decorator
def main() -> None:
    obj = Kafka()
    obj.run_cmd()


if __name__ == "__main__":
    main()
