#!/usr/bin/env python3.11

"""
sfrout is a scalable, asynchronous SalesForce report downloader for SAML/SSO clients. The app allows you to download reports based on their ID 
using your personal SFDC account. Supports asynchronous requests, threaded processing of the files, logging to rotating file and stdout, produces 
summary report for the session. 
"""

import time
import asyncio
import logging

from queue import Queue

from components.connectors import SfdcConnector
from components.containers import ReportsContainer
from components.handlers import WorkerFactory
from components.config import Config
from components.loggers import logger_configurer


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
        file_loglevel: str="WARNING", 
        verbose: bool=False
        ) -> None:
    """Main function of the program.

    :param domain: SalesForce domain of your organization -> "https://corp.my.salesforce.com/"
    :type domain: str    
    :param reports_path: Path to reports.csv file, template -> https://github.com/LukaszHoszowski/sfrout/blob/main/example/reports-default.csv
    :type reports_path: str
    :param reports_list: List of the reports as dictionaries -> ``[{'name': 'RaportName', 'id': '00O1V00000999GHES', 'path': WindowsPath('C:/downloads')}]``
    :type reports_list: list[dict[str, str]]
    :param summary_filepath: File path to summary report -> ``C:/downloads/summary.csv``
    :type summary_filepath: str
    :param log_path: Path to log file -> ``C:/downloads/logs/``
    :type log_path: str
    :param report: Single report mode -> ``RaportName,00O1V00000999GHES,C:/downloads``
    :type report: str
    :param path: Save location path override -> ``C:/new_downloads``
    :type path: str
    :param threads: Number of threads to use. (Default: ``half of available threads of the machine``) 
    :type threads: int
    :param stdout_loglevel: Log level for stdout logging -> ``['critical'|'error'|'warn'|'warning'|'info'|'debug']`` (Default: ``WARNING``)
    :type stdout_loglevel: str
    :param file_loglevel: Log level for file logging -> ``['critical'|'error'|'warn'|'warning'|'info'|'debug']`` (Default: ``WARNING``)
    :type file_loglevel: str 
    :param verbose: Toggles between Progress Bar and stdout logging (Default: ``False``)
    :type verbose: bool
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

    connector = SfdcConnector(queue, 
                              domain=config.domain,
                              verbose=config.verbose)
    connector.check_connection()
    
    container = ReportsContainer(config.report_params_list, 
                                 config.summary_filepath)
    
    WorkerFactory(queue, 
                  threads=config.threads)

    asyncio.run(connector.handle_requests(container.reports_list))

    queue.join()

    t1 = time.time()

     
    container.create_summary_report()

    container.print_summary_table()

    logger_main.info('SFR finished in %s', time.strftime(
        "%H:%M:%S", time.gmtime(t1 - t0)))
