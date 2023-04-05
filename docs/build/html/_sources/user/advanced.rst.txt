.. _advanced:

Advanced usage
==============

Let's have a look at entire palette of options offered by **SFrout**.


Complete script
---------------

Import::

    import sfrout


    sfrout.run(domain="https://corp.my.salesforce.com/", 
               reports_path="C:\\path\\to\\reports.csv", 
               summary_filepath="C:\\path\\to\\summary.csv",
               log_path="C:\\path\\to\\log", 
               path="C:\new_reports", 
               threads=2, 
               stdout_loglevel="INFO", 
               file_loglevel="DEBUG", 
               verbose=True)

CLI::

    $ sfrout "https://corp.my.salesforce.com/" "C:\\path\\to\\reports.csv" 
            -s "C:\\path\\to\\summary.csv"
            -l "C:\\path\\to\\log"
            -p "C:\new_reports"
            -t 2
            -ls INFO
            -lf DEBUG

Both codes behave exactly the same. CLI module is equiped with help::

    $ sfrout -h

CLI help::

    Options:
        -s, --summary_filepath PATH  Path to the summary report ->
                                    c:/summary_report.csv
        -l, --log_path PATH         Path to the log file -> c:/log                            
        -r, --report TEXT            Run single report ->
                                    "name,id,path,optional_report_params"
        -p, --path PATH              Override save location of the reports
        -t, --threads INTEGER        Number of threads to spawn  [default: 0]
        -ls, --stdout_loglevel TEXT  STDOUT logging level -> [DEBUG | INFO | WARN
                                    |WARNING | ERROR | CRITICAL]  [default:
                                    WARNING]
        -lf, --file_loglevel TEXT    File logging level -> [DEBUG | INFO | WARN|
                                    WARNING | ERROR | CRITICAL]  [default: INFO]
        -v, --verbose                Turn off progress bar
        -h, --help                   Show this message and exit.


Let's disassemble it!
---------------------

- ``summary_filepath`` (-s) - saves summary report with all the details regarding your reports in given location

- ``log_path`` (-l) - saves log file in given location

- ``path`` (-p) - overrides save path for your reports to given location

- ``threads`` (-t) - allows you to enter number of workers to be spawned for IO operations. By default it's equal to half of available threads. Bare in mind that if threads > max(threads) it may degraded the performance.

- ``stdout_loglevel`` (-ls) - let you decide your stdout logs granularity. Default: WARNING

- ``file_loglevel`` (-lf) - let you decide your file logs granularity. Default: INFO

- ``verbose`` (-v) - toggle between Progress Bar and stdout logging, once selected sets stdout_loglevel to INFO, otherwise ERROR. Stdout_loglevel if set overrides default setup of verbose regarding loglevel.


There is something more!
------------------------

**SFrout** accepts three formats of input report records:

- ``csv`` - list of reports is csv format 
    `Template <https://github.com/LukaszHoszowski/sfrout/blob/main/example/reports-default.csv>`_
- ``list`` - list of reports as dictionaries, this option isn't supported in CLI mode
    ``[{'name': 'RaportName', 'id': '00O1V00000999GHES', 'path': WindowsPath('C:/downloads')}]``
- ``Single report mode`` - string with comma seperated values, like one line from csv
    ``RaportName,00O1V00000999GHES,C:/downloads``

-----------------------

Courious how **SFrout** works? Check out the :ref:`how does it work? <how>` section.