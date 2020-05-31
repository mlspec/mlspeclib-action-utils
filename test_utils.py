import sys
import unittest
from pathlib import Path

if Path("src").exists():
    sys.path.append(str(Path("src")))
sys.path.append(str(Path.cwd()))
sys.path.append(str(Path.cwd().parent))

from utils import KnownException, report_found_params, raise_schema_mismatch  # noqa


class UtilsTest(unittest.TestCase):
    def test_report_found_params(self):
        param_name = "EXPECTED_PARAM"
        with self.assertRaises(KnownException) as context:
            report_found_params([param_name], {})

        self.assertTrue(param_name in str(context.exception))

        report_found_params([param_name], {param_name: 'NORESULT'})

        self.assertTrue(True)

    def test_raise_schema_mismatch(self):
        expected_type = 'EXPECTEDTYPE'
        expected_version = '0.0.1'

        with self.assertRaises(KnownException) as context:
            raise_schema_mismatch(expected_type, expected_version, None, None)

        self.assertTrue(expected_type in str(context.exception))
        self.assertTrue(expected_version in str(context.exception))

        with self.assertRaises(KnownException) as context:
            raise_schema_mismatch(expected_type, expected_version, expected_type, None)

        self.assertTrue(f"Expected Type: {expected_type}" in str(context.exception))

        with self.assertRaises(KnownException) as context:
            raise_schema_mismatch(expected_type, expected_version, None, expected_version)

        self.assertTrue(f"Expected Version: {expected_version}" in str(context.exception))

    # # TODO: Think about moving logger to a library of some kind so that it can be reused with this signature across derivaed containers
    # class setupLogger:
    #     _rootLogger = None
    #     _buffer = None

    #     def __init__(self):
    #         # logging.config.fileConfig('logging.conf')

    #         # return (logger, None)
    #         self._rootLogger = logging.getLogger()
    #         self._rootLogger.setLevel(logging.DEBUG)
    #         formatter = logging.Formatter("::%(levelname)s - %(message)s")

    #         if not self._rootLogger.hasHandlers():
    #             self._buffer = StringIO()
    #             bufferHandler = logging.StreamHandler(self._buffer)
    #             bufferHandler.setLevel(logging.DEBUG)
    #             bufferHandler.setFormatter(formatter)
    #             bufferHandler.set_name("buffer.logger")
    #             self._rootLogger.addHandler(bufferHandler)

    #             stdout_handler = logging.StreamHandler(sys.stdout)
    #             stdout_handler.setLevel(logging.DEBUG)
    #             stdout_handler.setFormatter(formatter)
    #             stdout_handler.set_name("stdout.logger")
    #             self._rootLogger.addHandler(stdout_handler)

    #             set_output_handler = logging.StreamHandler(sys.stdout)
    #             set_output_handler.setLevel(logging.NOTSET)
    #             set_output_handler.setFormatter(logging.Formatter("%(message)s"))
    #             set_output_handler.addFilter(self.filter_for_outputs)
    #             set_output_handler.set_name("setoutput.logger")
    #             self._rootLogger.addHandler(set_output_handler)
    #         else:
    #             for i, handler in enumerate(self._rootLogger.handlers):
    #                 if handler.name == "buffer.logger":
    #                     self._buffer = self._rootLogger.handlers[i].stream
    #                     break

    #             if self._buffer is None:
    #                 raise SystemError(
    #                     "Somehow, we've lost the 'buffer' logger, meaning nothing will be printed. Exiting now."
    #                 )

    #     def get_loggers(self):
    #         return (self._rootLogger, self._buffer)

    #     def get_root_logger(self):
    #         return self._rootLogger

    #     def get_buffer(self):
    #         return self._buffer

    #     def print_and_log(self, variable_name, variable_value):
    #         # echo "::set-output name=time::$time"
    #         output_message = f"::set-output name={variable_name}::{variable_value}"
    #         print(output_message)
    #         self._rootLogger.critical(output_message)

    #         return output_message

    #     @staticmethod
    #     def filter_for_outputs(record: LogRecord):
    #         if str(record.msg).startswith("::set-output"):
    #             return True
    #         return False
