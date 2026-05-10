from daf.command_line.scan.scan_request import ScanRequest


def test_scan_request_exposes_daf_scan_inputs():
    request = ScanRequest(
        scan_data={"mu": [0.0, 1.0]},
        motors=["mu"],
        motors_data={"mu": {"pv": "SIM:m1"}},
        counters={},
        main_counter=None,
        scan_type="absolute",
        steps=11,
        acquisition_time=0.1,
        output="/tmp/scan.nxs",
        kafka_topic="topic",
        scan_db="temp",
        kafka_server=None,
    )

    inputs = request.to_daf_scan_inputs()

    assert inputs["inputed_motors"] == ["mu"]
    assert inputs["scan_type"] == "absolute"
    assert inputs["steps"] == 11
