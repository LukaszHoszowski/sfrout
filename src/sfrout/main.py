#!/usr/bin/env python3.11

"""
SFrout is a scalable, asynchronous SalesForce report downloader for SAML/SSO clients. The app allows you to download reports based on their ID 
using your personal SFDC account. Supports asynchronous requests, threaded processing of the files, logging to rotating file and stdout, produces 
summary report for the session. 
"""

import time
import asyncio
import logging

from queue import Queue

from sfrout.components.connectors import SfdcConnector
from sfrout.components.containers import ReportsContainer
from sfrout.components.handlers import WorkerFactory
from sfrout.components.config import Config
from sfrout.components.loggers import logger_configurer


def run(*,
        domain: str, 
        reports_path: str, 
        reports_list: list[dict[str, str]]=[],
        summary_filepath: str="",
        log_path: str="", 
        report: str="", 
        path: str="", 
        threads: int=0, 
        stdout_loglevel: str="WARNING", 
        file_loglevel: str="INFO", 
        verbose: bool=False
        ) -> None:
    """Main function of the program.

    :param domain: SalesForce domain of your organization -> `"https://corp.my.salesforce.com/"`
    :type domain: str    
    :param reports_path: Path to reports.csv file, template -> `Template <https://github.com/LukaszHoszowski/sfrout/blob/main/example/reports-default.csv>`_
    :type reports_path: str
    :param reports_list: List of the reports as dictionaries -> ``[{'name': 'RaportName', 'id': '00O1V00000999GHES', 'path': WindowsPath('C:/downloads')}]`` , defaults to []
    :type reports_list: list[dict[str, str]], optional
    :param summary_filepath: File path to summary report -> ``C:/downloads/summary.csv`` , defaults to ""
    :type summary_filepath: str, optional
    :param log_path: Path to log file -> ``C:/downloads/logs/`` , defaults to ""
    :type log_path: str, optional
    :param report: Single report mode -> ``RaportName,00O1V00000999GHES,C:/downloads`` , defaults to ""
    :type report: str, optional
    :param path: Save location path override -> ``C:/new_downloads`` , defaults to ""
    :type path: str, optional
    :param threads: Number of threads to use, defaults to 0 
    :type threads: int, optional
    :param stdout_loglevel: Log level for stdout logging -> ``['critical'|'error'|'warn'|'warning'|'info'|'debug']`` , defaults to WARNING
    :type stdout_loglevel: str, optional
    :param file_loglevel: Log level for file logging -> ``['critical'|'error'|'warn'|'warning'|'info'|'debug']`` , defaults to INFO
    :type file_loglevel: str, optional
    :param verbose: flag, stdout logging if ``True`` , Progress Bar if ``False`` , defaults to False
    :type verbose: bool, optional

    Usage::
    
        import sfrout
        sfrout.run(domain="https://corp.my.salesforce.com/", reports_path="C:/path/to/reports.csv")
    """

    t0 = time.time()

    config = Config(domain=domain,
                    reports_csv_path=reports_path,
                    reports_list=reports_list,
                    summary_filepath=summary_filepath,
                    log_path=log_path,
                    report=report, 
                    path=path, 
                    threads=threads,
                    stdout_loglevel=stdout_loglevel, 
                    file_loglevel=file_loglevel, 
                    verbose=verbose
                    )

    logger_main = logging.getLogger(__name__)
    logger_configurer(stdout_loglevel=config.stdout_loglevel,
                      file_loglevel=config.file_loglevel,
                      log_path=config.log_path,
                      verbose=config.verbose)
                      

    logger_main.info('SFR started')

    queue = Queue()    

    connector = SfdcConnector(queue=queue, 
                              domain=config.domain,
                              verbose=config.verbose)
    connector.check_connection()
    
    container = ReportsContainer(config.report_params_list, 
                                 config.summary_filepath)
    
    WorkerFactory(queue=queue, 
                  threads=config.threads)

    asyncio.run(connector.handle_requests(container.reports_list))

    queue.join()

    t1 = time.time()

     
    container.create_summary_report()

    container.print_summary_table()

    logger_main.info('SFR finished in %s', time.strftime(
        "%H:%M:%S", time.gmtime(t1 - t0)))

if __name__ == '__main__':
    pass
