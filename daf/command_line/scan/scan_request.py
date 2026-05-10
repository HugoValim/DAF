"""Named scan request passed from CLI parsing to scan execution."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ScanRequest:
    scan_data: dict[str, Any]
    motors: list[str]
    motors_data: dict[str, Any]
    counters: dict[str, Any]
    main_counter: str | None
    scan_type: str
    steps: int | None
    acquisition_time: float
    output: str
    kafka_topic: str
    scan_db: str
    delay_time: float | None = None
    kafka_server: str | None = None

    def to_daf_scan_inputs(self) -> dict[str, Any]:
        return {
            "scan_data": self.scan_data,
            "inputed_motors": self.motors,
            "motors_data_dict": self.motors_data,
            "counters": self.counters,
            "main_counter": self.main_counter,
            "scan_type": self.scan_type,
            "steps": self.steps,
            "acquisition_time": self.acquisition_time,
            "delay_time": self.delay_time,
            "output": self.output,
            "kafka_topic": self.kafka_topic,
            "scan_db": self.scan_db,
            "kafka_server": self.kafka_server,
        }
