import os
import csv
import logging

from pathlib import Path
from typing import Any, Protocol

logger_main = logging.getLogger(__name__)


class ConfigProtocol(Protocol):
    """Protocol class for config object.

    :param domain: argument for SFDC domain
    :type domain: str
    :param reports_csv_path: argument for input report csv path.
    :type reports_csv_path: str
    :param reports_list: argument for list of reports as dictionary
    :type reports_list: list[dict[str, Any]]
    :param summary_filepath: argument for summary file path
    :type summary_filepath: str
    :param log_filepath: argument for log file path
    :type log_filepath: str
    :param report: argument for single report parameters
    :type report: str
    :param path: argument for save location path override
    :type path: str
    :param threads: argument for number of threads to use
    :type threads: int
    :param stdout_loglevel: argument for stdout log level
    :type stdout_loglevel: str
    :param file_loglevel: argument for stdout log level
    :type file_loglevel: str
    :param verbose: Flag, toggles progress bar/stdout
    :type verbose: bool
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
    
    :param domain: argument for SFDC domain
    :type domain: str
    :param reports_csv_path: argument for input report csv path.
    :type reports_csv_path: str
    :param reports_list: argument for list of reports as dictionary, defaults to []
    :type reports_list: list[dict[str, Any]], optional
    :param summary_filepath: argument for summary file path, defaults to None
    :type summary_filepath: str, optional
    :param log_filepath: argument for log file path, defaults to None
    :type log_filepath: str, optional
    :param report: argument for single report parameters, defaults to ""
    :type report: str, optional
    :param path: argument for save location path override, defaults to ""
    :type path: str, optional
    :param threads: argument for number of threads to use, defaults to 0
    :type threads: int, optional
    :param stdout_loglevel: argument for stdout log level, defaults to "WARNING"
    :type stdout_loglevel: str, optional
    :param file_loglevel: argument for stdout log level, defaults to "INFO"
    :type file_loglevel: str, optional
    :param verbose: Flag, toggles progress bar/stdout, defaults to False
    :type verbose: bool, optional
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
        self.keys: list[str] = ['name', 'id', 'path', 'export_params']
        self.report_params_list: list[dict[str,
                                           str | Path]] = self._parse_input_report()
        self.threads: int = self._define_number_of_threads()
        
        self.stdout_loglevel: str = stdout_loglevel
        self.file_loglevel: str = file_loglevel
        self.verbose: bool = verbose

    
    def _define_number_of_threads(self):
        """Defines number of threads. By default number of threads is set to half of available threads.
        If threads value is not available number of threds will be set to 2.  
        If ``report`` parameter is filled (single report mode) then number of threads will be automatically set to 1.
        """

        return (int((os.cpu_count() or 4) / 2) if not self.threads else self.threads) if not self.report else 1

    def _input_report_path_cast(self, object_kwargs: list[dict[str, Any]]) -> list[dict[str, str | os.PathLike]]:
        """Casts value of ``path`` into :class:`Path` object. 

        :param object_kwargs: colection of report parameters
        :type object_kwargs: list[dict[str, Any]]
        :return: collection of object parameters with `path` casted to :class:`Path` object 
        :rtype: list[dict[str, str | :class:`os.PathLike`]]
        """

        logger_main.debug(
            'Parsing input reports - casting "path" to Path object')

        [dict.update({'path': Path(dict['path'])}) for dict in object_kwargs]

        return object_kwargs

    def _input_report_single_mode_override(self) -> list[dict[str, str]]:
        """Creates report's parameters in single report mode. Returns parsed parameters as object kwargs. 

        :return: collection of report's parameters in single report mode
        :rtype: list[dict[str, str]]
        """

        logger_main.debug('Parsing input reports - single mode report')

        if len(self.report) != 4:
            logger_main.debug(
                'Parsing input reports - single mode report | optional_params not present')
            self.report.append('')

        return [dict(zip(self.keys, self.report))]

    def _input_report_csv_standard_file_mode(self) -> list[dict[str, str]]:
        """Reads parameteres taken from input `csv` . Returns parsed parameters as objects kwargs.

        :return: collection of report's parameters in standard mode
        :rtype: list[dict[str, str]]
        """

        logger_main.debug('Parsing input reports - standard csv mode report')
        with open(self.reports_csv_path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            logger_main.debug(
                'Parsing input reports - standard csv mode report - skipping header')
            next(csv_reader)

            return [dict(zip(self.keys, values)) for values in csv_reader]

    def _input_report_path_override(self, object_kwargs: list[dict[str, str]]) -> list[dict[str, str]]:
        """Replaces value of `path` key in `object_kwargs` dict with `path` parameter value. `path` override.

        :param object_kwargs: Colection of report parameters
        :type object_kwargs: list[dict[str, str]]
        :return: Collection of report's parameters with replaced `path` 
        :rtype: list[dict[str, str]]
        """

        logger_main.debug('Parsing input reports - report path override')
        [dict.update({'path': self.path}) for dict in object_kwargs]
    
        return object_kwargs

    def _parse_input_report(self) -> list[dict[str, Any]]:
        """Orchestrating function which parses parameters for :class:`ReportProtocol` .

        :return: Collection of ready to use report kwargs.
        :rtype: list[dict[str, Any]]
        """

        logger_main.debug('Parsing input reports')

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

        logger_main.debug('Input reports successfully generated')

        return self._input_report_path_cast(_temp_report_params)
    
if __name__ == '__main__':
    pass
