import os
import csv
import logging

from dataclasses import dataclass, field
from typing import Any, Generator, Protocol, runtime_checkable
from datetime import datetime, timedelta
from pandas import DataFrame
from tabulate import tabulate

logger_main = logging.getLogger(__name__)


@runtime_checkable
class ReportProtocol(Protocol):
    """Protocol class for report object.

    :param name: report name, propagated to report file name
    :type name: str
    :param id: report id
    :type id: str
    :param path: report path, save location for the report in form of :class:`pathlib.Path` object
    :type path: :class:`os.PathLike`
    :param type: report type, drives connector selection
    :type type: str
    :param export_params: default GET parameters
    :type export_params: str
    :param downloaded: flag indicating whether the reports has been succesfully downloaded or not
    :type downloaded: bool
    :param valid: flag indicating whether the response has been succesfully retrieved or not
    :type valid: bool
    :param created_date: report save completition date
    :type created_date: datetime
    :param pull_date: report response completition date
    :type pull_date: datetime
    :param processing_time: the time it took to process the report in seconds 
    :type pull_date: timedelta
    :param attempt_count: number of attempts to process the report 
    :type attempt_count: int
    :param size: size of saved report file in Mb
    :type size: float
    :param response: container for request response
    :type response: str
    :param content: Pandas :class:`pd.DataFrame` based on response
    :type content: :class:`pd.DataFrame`
    """

    name: str
    id: str
    path: os.PathLike
    type: str
    export_params: str
    downloaded: bool
    valid: bool
    created_date: datetime
    pull_date: datetime
    processing_time: timedelta
    attempt_count: int
    size: float
    response: str
    content: DataFrame


@runtime_checkable
class ReportsContainerProtocol(Protocol):
    """Protocol class for report container object.

    :param report_params_list: collection of dictionaries with parameters for object crafting
    :type report_params_list: list[dict[str, Any]]
    :param summary_report_path: path to save location of summary report
    :type summary_report_path: :class:`os.PathLike`
    """

    def create_reports(self) -> list[ReportProtocol]:
        """Orchestrating method to handle report objects factory

        :return: collection of :class:`ReportProtocol` objects
        :rtype: list[:class:`ReportProtocol`]
        """
        ...

    def create_summary_report(self) -> None:
        """Creates summary report which consist of all important details regarding :class:`ReportProtocol` objects. 
        Summary report is generated once all the reports are completed.
        """
        ...


@dataclass(slots=True)
class SfdcReport():
    """Concrete class representing SFDC Report object.

    :param name: report name, propagated to report file name
    :type name: str
    :param id: report id, identification number of the report in SFDC
    :type id: str
    :param path: report path, save location for the report in form of :class:`pathlib.Path` object
    :type path: :class:`os.PathLike`
    :param type: report type, type drives connector and report objects selectiond, defaults to 'SFDC'
    :type type: str, optional
    :param export_params: default GET parameters required by SFDC, defaults to '?export=csv&enc=UTF-8&isdtp=p1'
    :type export_params: str, optional
    :param downloaded: flag indicating whether the reports has been succesfully downloaded or not, defaults to False
    :type downloaded: bool, optional
    :param valid: flag indicating whether the response has been succesfully retrieved or not, defaults to False
    :type valid: bool, optional
    :param created_date: report save completition date, defaults to current datetime
    :type created_date: datetime, optional
    :param pull_date: report response completition date, defaults to current datetime
    :type pull_date: datetime, optional
    :param processing_time: the time it took to process the report in seconds, defaults to 0 microseconds
    :type pull_date: timedelta, optional
    :param attempt_count: number of attempts to process the report, defaults to 0
    :type attempt_count: int, optional
    :param size: size of saved report file in Mb, defaults to 0.0
    :type size: float, optional
    :param response: container for request response, defaults ""
    :type response: str, optional
    :param content: Pandas DataFrame based on response, defaults to empty :class:`pd.DataFrame`
    :type content: :class:`pd.DataFrame` , optional
    """

    name: str
    id: str
    path: os.PathLike
    type: str = 'SFDC'
    export_params: str = '?export=csv&enc=UTF-8&isdtp=p1'
    downloaded: bool = False
    valid: bool = False
    created_date: datetime = datetime.now()
    pull_date: datetime = datetime.now()
    processing_time: timedelta = timedelta(microseconds=0)
    attempt_count: int = 0
    size: float = 0.0
    response: str = ""
    content: DataFrame = field(default_factory=DataFrame)


class ReportsContainer():
    """Concrete class representing ReportContainer object. 
    """

    def __init__(self,
                 reports_params_list: list[dict[str, Any]],
                 summary_path: os.PathLike | None):
        """Constructor method for ReportContainer, automatically creates reports after initialization
        """

        self.reports_params_list: list[dict[str, Any]] = reports_params_list
        self.summary_path: os.PathLike | None = summary_path
        self.reports_list: list[ReportProtocol]

        self.create_reports()

    def __len__(self):
        """Returns number of collected :class:`ReportProtocol` objects.
        """

        return len(self.reports_list)

    def _create_sfdc_reports(self) -> Generator[SfdcReport, None, None]:
        """Creates :class:`SfdcReport` objects.

        :return: generator with :class:`SfdcReport` objects
        :rtype: Generator[:class:`SfdcReport`, None, None]
        :yield: :class:`SfdcReport` instance based on parsed report parameters
        :rtype: :class:`SfdcReport`
        """

        logger_main.debug("Creating SFDC report objects")
        reports = (SfdcReport(**dict) for dict in self.reports_params_list)

        return reports

    def create_reports(self) -> list[ReportProtocol]:
        """Orchestrating method to handle report objects crafting

        :return: collection of :class:`ReportProtocol` objects
        :rtype: list[:class:`ReportProtocol`]
        """

        logger_main.debug("Creating all report objects")
        self.reports_list = list(self._create_sfdc_reports())

        return self.reports_list
    
    def _create_summary_folder_if_not_exist(self):
        """Creates folder for summary report if doesn't exist.
        """
        if self.summary_path is not None:
            if not os.path.exists(os.path.dirname(self.summary_path)):
                os.makedirs(os.path.dirname(self.summary_path))
        return None

    def create_summary_report(self) -> None:
        """Creates summary report which consist of all important details regarding :class:`ReportProtocol` objects. 
        Summary is generated once all the :class:`ReportProtocol` are completed.
        """
        if self.summary_path:
            logger_main.debug("Creating summary report, saved in %s",
                            self.summary_path)

            self._create_summary_folder_if_not_exist()

            header = ['file_name', 'report_id', 'type', 'valid', 'created_date',
                    'pull_date', 'processing_time', 'attempt_count', 'file_size']

            with open(self.summary_path, 'w', encoding='UTF8', newline='') as f:
                writer = csv.writer(f)

                writer.writerow(header)

                for report in self.reports_list:
                    writer.writerow([report.name, report.id, report.type, report.valid, report.created_date,
                                    report.pull_date, report.processing_time, report.attempt_count, report.size])

        return None
    
    def print_summary_table(self) -> None:
        """Prints summary table which consist of all important details regarding :class:`ReportProtocol` objects. 
        Table is generated once all the :class:`ReportProtocol` are completed.
        """
        logger_main.debug("Creating summary table")

        print("")

        header = ['report', 'valid', 'processing_time', 'file_size']
        data = []
        
        for report in self.reports_list:
            data.append([report.name, report.valid, report.processing_time, report.size])

        print(tabulate(data, headers=header, tablefmt='fancy_grid'))

        return None

if __name__ == '__main__':
    pass
