"""
requests.adapters
~~~~~~~~~~~~~~~~~
This module contains the transport adapters that Requests uses to define
and maintain connections.
"""

import os
import logging
import logging.handlers
from pathlib import Path


def logger_configurer(*,
                      stdout_loglevel: str, 
                      file_loglevel: str,
                      log_path: os.PathLike | None, 
                      verbose: bool) -> None:
    """
    Configures logger settings for file and stdout handlers.

    :param cli_stdout_loglevel: LogLevel for stdout logger handler based on CLI option. Defaults to ERROR.
    :type cli_stdout_loglevel: str
    :param cli_file_loglevel: LogLevel for file logger handler based on CLI option. Defaults to INFO.
    :type cli_stdout_loglevel: str
    :param verbose: Flag toggling LogLevel for stdout logger handler, if True sets to ERROR, else INFO.
    :type verbose: str
    """

    levels = {
        'critical': logging.CRITICAL,
        'error': logging.ERROR,
        'warn': logging.WARNING,
        'warning': logging.WARNING,
        'info': logging.INFO,
        'debug': logging.DEBUG
    }

    if not verbose:
        slevel = levels.get(stdout_loglevel.lower(), logging.ERROR)
    else:
        slevel = 20

    flevel = levels.get(file_loglevel.lower(), 20)

    logger = logging.getLogger()
    logger.setLevel(slevel)

    formatter = logging.Formatter('%(asctime)-20s| %(levelname)-8s| %(processName)-12s| '
                                  '%(message)s', '%Y-%m-%d %H:%M:%S')

    if log_path:
        f_path = os.path.join(Path(log_path), 'sfrout.log')

        handler_f = logging.handlers.RotatingFileHandler(
            f_path, 'a', 1_000_000, 3)
        handler_f.setFormatter(formatter)
        logger.addHandler(handler_f)

    handler_s = logging.StreamHandler()
    handler_s.setLevel(flevel)
    handler_s.setFormatter(formatter)
    logger.addHandler(handler_s)

    return None

if __name__ == '__main__':
    pass
