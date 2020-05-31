import logging
from logging import LogRecord
from io import StringIO
import sys
from pathlib import Path
from mlspeclib import MLObject

if Path("src").exists():
    sys.path.append(str(Path("src")))
sys.path.append(str(Path.cwd()))
sys.path.append(str(Path.cwd().parent))


class KnownException(Exception):
    pass


def report_found_params(expected_params: list, offered_params: dict) -> None:
    rootLogger = setupLogger().get_root_logger()
    for param in expected_params:
        if param not in offered_params or offered_params[param] is None:
            raise KnownException(f"No parameter set for {param}.")
        else:
            rootLogger.debug(f"Found value for {param}.")


def raise_schema_mismatch(
    expected_type: str, expected_version: str, actual_type: str, actual_version: str
):
    raise KnownException(
        f"""Actual data does not match the expected schema and version:
    Expected Type: {expected_type}
    Actual Type: {actual_type}

    Expected Version: {expected_version}
    Actual Version: {actual_version}")"""
    )


# TODO: Think about moving logger to a library of some kind so that it can be reused with this signature across derivaed containers
class setupLogger:
    _rootLogger = None
    _buffer = None

    def __init__(self, debug=False):
        logLevel = logging.WARN
        if debug:
            logLevel = logging.DEBUG

        self._rootLogger = logging.getLogger()
        self._rootLogger.setLevel(logLevel)
        formatter = logging.Formatter("::%(levelname)s - %(message)s")

        if not self._rootLogger.hasHandlers():
            self._buffer = StringIO()
            bufferHandler = logging.StreamHandler(self._buffer)
            bufferHandler.setLevel(logLevel)
            bufferHandler.setFormatter(formatter)
            bufferHandler.set_name("buffer.logger")
            self._rootLogger.addHandler(bufferHandler)

            stdout_handler = logging.StreamHandler(sys.stdout)
            stdout_handler.setLevel(logLevel)
            stdout_handler.setFormatter(formatter)
            stdout_handler.set_name("stdout.logger")
            self._rootLogger.addHandler(stdout_handler)

            set_output_handler = logging.StreamHandler(sys.stdout)
            set_output_handler.setLevel(logging.NOTSET)
            set_output_handler.setFormatter(logging.Formatter("%(message)s"))
            set_output_handler.addFilter(self.filter_for_outputs)
            set_output_handler.set_name("setoutput.logger")
            self._rootLogger.addHandler(set_output_handler)
        else:
            for i, handler in enumerate(self._rootLogger.handlers):
                if handler.name == "buffer.logger":
                    self._buffer = self._rootLogger.handlers[i].stream
                    break

            if self._buffer is None:
                raise SystemError(
                    "Somehow, we've lost the 'buffer' logger, meaning nothing will be printed. Exiting now."
                )

    def get_loggers(self):
        return (self._rootLogger, self._buffer)

    def get_root_logger(self):
        return self._rootLogger

    def get_buffer(self):
        return self._buffer

    def print_and_log(self, variable_name, variable_value):
        # echo "::set-output name=time::$time"
        output_message = f"::set-output name={variable_name}::{variable_value}"
        print(output_message)
        self._rootLogger.critical(output_message)

        return output_message

    @staticmethod
    def filter_for_outputs(record: LogRecord):
        if str(record.msg).startswith("::set-output"):
            return True
        return False


def verify_result_contract(
    result_object: MLObject,
    expected_schema_type,
    expected_schema_version,
    step_name: str,
):
    """ Creates an MLObject based on an input string, and validates it against the workflow object
    and step_name provided.
    Will fail if the .validate() fails on the object or the schema mismatches what is seen in the
    workflow.
    """
    rootLogger = setupLogger().get_root_logger()

    (contract_object, errors) = MLObject.create_object_from_string(
        result_object.dict_without_internal_variables()
    )

    if errors is not None and len(errors) > 0:
        error_string = (
            f"Error verifying result object for '{step_name}.output': {errors}"
        )
        rootLogger.debug(error_string)
        raise ValueError(error_string)

    if (contract_object.schema_type != expected_schema_type) or (
        contract_object.schema_version != expected_schema_version
    ):
        error_string = f"""Actual data does not match the expected schema and version:
    Expected Type: {expected_schema_type}
    Actual Type: {contract_object.schema_type}
    Expected Version: {expected_schema_version}
    Actual Version: {contract_object.schema_version}")"""
        rootLogger.debug(error_string)
        raise ValueError(error_string)

    rootLogger.debug(
        f"Successfully loaded and validated contract object: {contract_object.schema_type} on step {step_name}.output"
    )

    return True
