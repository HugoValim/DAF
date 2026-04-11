"""
Unit tests for daf.command_line.scan modules
"""
import unittest
from unittest.mock import patch, MagicMock
import sys


class TestDAFScanInputs(unittest.TestCase):
    """Test DAFScanInputs dataclass"""

    def test_scan_db_defaults_to_none(self):
        """Test that scan_db can be None"""
        from daf.command_line.scan.scan_daf import DAFScanInputs

        inputs = DAFScanInputs()
        self.assertIsNone(inputs.scan_db)

    def test_scan_db_can_be_set(self):
        """Test that scan_db can be set"""
        from daf.command_line.scan.scan_daf import DAFScanInputs

        inputs = DAFScanInputs(scan_db="temp")
        self.assertEqual(inputs.scan_db, "temp")


class TestDAFScanInstantiation(unittest.TestCase):
    """Test DAFScan instantiation with scan_db"""

    def test_dafscan_fixes_none_scan_db_to_temp(self):
        """Test that DAFScan fixes None scan_db to 'temp'"""
        with patch('daf.command_line.scan.scan_daf.databroker.Broker') as mock_broker:
            mock_broker_instance = MagicMock()
            mock_broker_instance.insert = MagicMock()
            mock_broker.named.return_value = mock_broker_instance

            with patch('daf.command_line.scan.scan_daf.KafkaProducer'):
                with patch('daf.command_line.scan.scan_daf.RunEngine'):
                    from daf.command_line.scan.scan_daf import DAFScan, DAFScanInputs

                    inputs = DAFScanInputs(
                        scan_data={},
                        inputed_motors=(),
                        motors_data_dict={},
                        counters=(),
                        main_counter=None,
                        scan_type="absolute",
                        steps=10,
                        acquisition_time=0.1,
                        delay_time=0.0,
                        output="test",
                        kafka_topic="test_topic",
                        scan_db=None,  # None scan_db
                    )

                    # Should not raise - fix handles None
                    scan = DAFScan(inputs)

                    # Verify scan_db was defaulted to 'temp'
                    self.assertEqual(scan.scan_db, "temp")

    def test_dafscan_uses_valid_scan_db(self):
        """Test that DAFScan uses valid scan_db as provided"""
        with patch('daf.command_line.scan.scan_daf.databroker.Broker') as mock_broker:
            mock_broker_instance = MagicMock()
            mock_broker_instance.insert = MagicMock()
            mock_broker.named.return_value = mock_broker_instance

            with patch('daf.command_line.scan.scan_daf.KafkaProducer'):
                with patch('daf.command_line.scan.scan_daf.RunEngine'):
                    from daf.command_line.scan.scan_daf import DAFScan, DAFScanInputs

                    inputs = DAFScanInputs(
                        scan_data={},
                        inputed_motors=(),
                        motors_data_dict={},
                        counters=(),
                        main_counter=None,
                        scan_type="absolute",
                        steps=10,
                        acquisition_time=0.1,
                        delay_time=0.0,
                        output="test",
                        kafka_topic="test_topic",
                        scan_db="my_custom_db",  # Valid scan_db
                    )

                    scan = DAFScan(inputs)
                    self.assertEqual(scan.scan_db, "my_custom_db")


if __name__ == "__main__":
    unittest.main()
