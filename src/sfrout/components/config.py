import os
import csv
import logging

from pathlib import Path
from typing import Any, Protocol

logger_main = logging.getLogger(__name__)


class ConfigProtocol(Protocol):
    """Protocol class for config object.

    :param reports_list_path: CLI argument for input report list path.
    :type reports_list_path: str
    :param report: CLI argument for single report params.
    :type report: str
    :param path: CLI argument for save location path override.
    :type path: str
    :param threads: CLI argument for number of threads to use.
    :type threads: int
    """

    domain: str
    reports_csv_path: str
    reports_list: list[dict[str, Any]]
    summary_filepath: str
    log_filepath:str
    report: str
    path: str
    threads: int
    stdout_loglevel: str 
    file_loglevel: str 
    verbose: bool

class Config:
    """Concrete class representing Config object. Contains entire configuration required for a program.
    
    :param reports_list_path: CLI argument for input report list path.
    :type reports_list_path: str
    :param report: CLI argument for single report params.
    :type report: str
    :param path: CLI argument for save location path override.
    :type path: str
    :param threads: CLI argument for number of threads to use.
    :type threads: int
    """

    def __init__(self,
                 *,
                 domain: str,
                 reports_csv_path: str,
                 reports_list: list[dict[str, Any]] = [],
                 summary_filepath: str | None = None,
                 log_path: str | None = None,
                 report: str = "",
                 path: str = "",
                 threads: int = 0,
                 stdout_loglevel: str = "WARNNING", 
                 file_loglevel: str = "INFO",
                 verbose=False):

        self.domain: str = domain
        self.reports_csv_path: str = reports_csv_path
        self.reports_list: list[dict[str, Any]] = reports_list
        self.summary_filepath: os.PathLike | None = Path(summary_filepath) if summary_filepath else None
        self.log_path: os.PathLike | None = Path(log_path) if log_path else None
        self.report: list[str] = report.split(
            ',') if report else []
        self.path: str = path
        self.threads: int = threads
        self.keys: list[str] = ['name', 'id', 'path', 'params']
        self.report_params_list: list[dict[str,
                                           str | Path]] = self._parse_input_report()
        self.threads: int = self._define_number_of_threads()
        
        self.stdout_loglevel: str = stdout_loglevel
        self.file_loglevel: str = file_loglevel
        self.verbose: bool = verbose

    
    def _define_number_of_threads(self):
        """Defines number of threads. By default number of threads is set to half of available threads.
        If threads value is not available number of threds will be set to 2. 
        If threads number has been defined in CLI configuration threads will be equal to this number. 
        If CLI report is filled (single report mode) then number of threads will be automatically set to 1  
        """

        return (int((os.cpu_count() or 4) / 2) if not self.threads else self.threads) if not self.report else 1

    def _input_report_path_cast(self, object_kwargs: list[dict[str, Any]]) -> list[dict[str, str | os.PathLike]]:
        """Casts value of `path` key into Path object. 

        :param object_kwargs: Colection of object parameters
        :type object_kwargs: list[dict[str, Any]]
        :return: Collection of object parameters with `path` casted to Path object 
        :rtype: list[dict[str, str | PathLike]]
        """

        logger_main.debug(
            "Parsing input reports - casting 'path' to Path object")

        [dict.update({'path': Path(dict['path'])}) for dict in object_kwargs]

        return object_kwargs

    def _input_report_single_mode_override(self) -> list[dict[str, str]]:
        """Reads parameters taken from CLI. Returns parsed parameters into object kwargs. 

        :return: collection of single object kwargs (parameters) based on CLI argument
        :rtype: list[dict[str, str]]
        """

        logger_main.debug("Parsing input reports - single mode report")

        if len(self.report) != 4:
            logger_main.debug(
                "Parsing input reports - single mode report | optional_params not present")
            self.report.append('')

        return [dict(zip(self.keys, self.report))]

    def _input_report_csv_standard_file_mode(self) -> list[dict[str, str]]:
        """Reads parameteres taken from input CSV. Returns parsed parameters into objects kwargs.

        :return: collection of objects kwargs (parameters) based on input CSV
        :rtype: list[dict[str, str]]
        """

        logger_main.debug("Parsing input reports - standard csv mode report")
        with open(self.reports_csv_path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            logger_main.debug(
                "Parsing input reports - standard csv mode report - skipping header")
            next(csv_reader)

            return [dict(zip(self.keys, values)) for values in csv_reader]

    def _input_report_path_override(self, object_kwargs: list[dict[str, str]]) -> list[dict[str, str]]:
        """Replaces value of `path` kwarg parameter of the object with `path` value from CLI argument.

        :param object_kwargs: Colection of object parameters
        :type object_kwargs: list[dict[str, str]]
        :return: Collection of object parameters with `path` replaced with value of `path` CLI argument 
        :rtype: list[dict[str, str]]
        """

        logger_main.debug("Parsing input reports - report path override")
        [dict.update({'path': self.path}) for dict in object_kwargs]
    
        return object_kwargs

    def _parse_input_report(self) -> list[dict[str, Any]]:
        """Orchestrating function for parsing parameters for input reports.

        :return: Collection of ready to use object kwargs.
        :rtype: list[dict[str, Any]]
        """

        logger_main.debug("Parsing input reports")

        _temp_report_params = ""

        if self.report:
            _temp_report_params = self._input_report_single_mode_override()
        else:
            _temp_report_params = self._input_report_csv_standard_file_mode()

        if self.reports_list:
            _temp_report_params = self.reports_list

        if self.path:
            _temp_report_params = self._input_report_path_override(
                _temp_report_params)

        logger_main.debug("Input reports successfully generated")

        return self._input_report_path_cast(_temp_report_params)
    
if __name__ == '__main__':
    pass
