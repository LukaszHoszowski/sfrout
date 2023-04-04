#!/usr/bin/env python3.11

import click
from main import run


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('domain', type=click.STRING)
@click.argument('reports_path', required=False, type=click.Path(exists=True))
@click.option('--summary_filepath', '-s', required=False, type=click.Path(exists=True), help='Path to the summary report -> c:/summary_report.csv')
@click.option('--report', '-r', type=click.STRING, help='Run single report -> "name,id,path,optional_report_params"')
@click.option('--path', '-p', type=click.Path(exists=True), help='Override save location of the reports')
@click.option('--threads', '-t', type=click.INT, default=0, show_default=True, help='Number of threads to spawn')
@click.option('--stdout_loglevel', '-ls', type=click.STRING, default="WARNING", show_default=True, 
              help='STDOUT logging level -> [DEBUG | INFO | WARN |WARNING | ERROR | CRITICAL]')
@click.option('--file_loglevel', '-lf', type=click.STRING, default="INFO", show_default=True, 
              help='File logging level -> [DEBUG | INFO | WARN| WARNING | ERROR | CRITICAL]')
@click.option('--verbose', '-v', is_flag=True, show_default=True, default=False, help='Turn off progress bar')
def cli(domain: str, 
         reports_path, 
         reports_list=[],
         summary_filepath="", 
         report="", 
         path="", 
         threads=0, 
         stdout_loglevel="WARNING", 
         file_loglevel="WARNING", 
         verbose=False,
         ):
    """
    SFR is a simple, but very efficient due to scalability, Python application which allows you to download various reports.  
    Program supports asynchronous requests and threading for saving/processing content. Logging and CLI parameters handlig is also included.

    So far the App supports SFDC reports with SSO authentication.
    """

    run(domain=domain,
        reports_path=reports_path,
        summary_filepath=summary_filepath,
        report=report, 
        path=path, 
        threads=threads, 
        stdout_loglevel=stdout_loglevel, 
        file_loglevel=file_loglevel, 
        verbose=verbose
        )

if __name__ == '__main__':
    cli()
