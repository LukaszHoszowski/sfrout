![SFrout Downloads](https://static.pepy.tech/badge/sfrout)
![License Badge](https://img.shields.io/pypi/l/sfrout.svg)
![Wheel Support Badge](https://img.shields.io/pypi/wheel/sfrout.svg)
![Python Version Support Badge](https://img.shields.io/pypi/pyversions/sfrout.svg)

# SFrout - Sales Force Report Downloader

## What is it?

**SFrout** is a scalable, asynchronous SalesForce report downloader for SAML/SSO clients. The app allows you to download reports based on their ID using your personal SFDC account. Supports asynchronous requests, threaded processing of the files, logging to rotating file and stdout, produces summary report for the session. 

## Installation

SFrout require Python 3.11 to work properly.

- navigate to some convenient folder (optional)

```sh
cd c:/path/to/venv
```

- create Python virtual env (optional)

```sh
python -m venv c:/path/to/venv
```

- activate virtual env

for Windows:
```sh
c:\path\to\venv\Scripts\activate.bat
```

for Unix
```sh
source /path/to/venv/bin/activate
```

- install sfrout from PyPi 

```sh
pip install sfrout
```

## Usage

### Python interface

- create a python file and paste in below script. Amend domain and path to your reports file

```python
import sfrout


sfrout.run(domain="https://corp.my.salesforce.com/", 
           reports_path="C:\\path\\to\\reports.csv")
```

- fill in reports.csv file according to given template

[Input file template](https://github.com/LukaszHoszowski/sfrout/blob/main/example/reports-default.csv)

- execute the script

```sh
"c:/path/to/your/file.py"
```

- shortly after you might be prompted to log in to SalesForce in MS Edge, website will open automatically

- next the progress bar will show up

![](https://github.com/LukaszHoszowski/sfrout/blob/main/docs/_static/progress_bar.png?raw=True)

- once finish, **SFrout** will print summary table

![](https://github.com/LukaszHoszowski/sfrout/blob/main/docs/_static/summary.png?raw=True)

### CLI

- open terminal

```sh
cmd.exe
```

- type in command

```sh
sfrout "https://corp.my.salesforce.com/" "C:\\path\\to\\reports.csv"
```

- fill in reports.csv file according to given template

[Input file template](https://github.com/LukaszHoszowski/sfrout/blob/main/example/reports-default.csv)

CLI interface allow you to configure parameters according to below list:

```sh
Options:
  -s, --summary_filepath PATH  Path to the summary report ->
                               c:/summary_report.csv
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
```

### Windows Task Scheduler

Create `sfrout.bat`, save it with below script:

```sh
"c:\path\to\new\virtual\environment\Scripts\python.exe" sfrout "https://corp.my.salesforce.com/" "C:\\path\\to\\reports.csv"
pause
```

Test it, if works create a task and set some schedule

## How the program works

Once you run the program:

1) configuration, data parsing
2) creating connector, report, shared queue objects
3) initialization of workers listeners within file handler
4) connector will check the connection and execute all required steps to establish the connection
5) connector will produce asynchronous requests to given domain
6) once single request is fulfilled retrieved content is being put into the queue
7) workers keep on listen for items in the queue
8) once queue is not empty some worker will take the item and start processing
9) once all the request are fulfilled queue will close and send signals to workers to shutdown once they finish their last job

## SFDC Connector

**Authentication:**

Authorization and authentication in SFDC is based on `sid` cookie entry for SSO or on security tokens in other cases. 

SFrout will try to connect to CookieJar of your MS Edge browser and find `sid` entry for given domain. If `sid` is not found, the app will open MS Edge and request given SFDC domain. You will be asked to log in as usual. After 20 seconds program will retry to find `sid` in your CookieJar. Browsers usually store cookies in SQlite db. This information is not being transfered to db immediately, it can be triggered by closing the browser but it isn't the most elegant solution. SFrout will ask for `sid` in 2 seconds intervals as long as `sid` will be available. Entire process will repeat as many times as it takes.

**Sending requests:**

SFDC supports export GET requests by adding `?export=csv&enc=UTF-8&isdtp=p1` to address of your supplemented with headers and above `sid` entry. In response you will receive CSV-like data stream. Time window for entire operation is fixed and equal to **15 minutes**. If you will not be able to receive response in this narrow time window connection will be forceable shutdown and request cancelled regardless of the stage.

Requests are send out asynchronously to speed things up and restrain memory consumption to bare minimum. Once request will fail, regardless of that what has caused failure, SFrout will retry. Limit of attempts has been set to **20**. Once request is successful, response is saved in Report object and put to the queue for further processing.

## File handler

Thread based solution for saving request responses to a file. 

File handler spawns workers in separate threads. Number of workers is equal to half of available threads on your machine (e.g. if your cpu has 6 cores and 12 threads SFR will spawn 6 workers). If information about available resources is not reachable it will default to **2**. Such approach will not dramatically slow down other applications on your computer and will secure required resources for SFR. Each worker will observe `Queue`, if something will be put into `Queue` one of the workers will start processing of the report. Bare in mind that each saving operation erases response and content of the report due to memory consumption. `Queue` size is unlimited so sooner or later workers will handle entire workload. Workers will die once `Queue` will send signal that they shouldn't expect any new items. These workers who are just processing items will finish their jobs and die quietly.

All files are processed by `Pandas` which gives wide palette of available formats. Unfortunately such flexibility somes with the price. In current shape `Pandas` isn't the best in saving `csv` files due to `numpy` engine. On top of that `Pandas` is a relatively heavy library. I plan to switch to some other processing engine in the future.

## Limitations

- **Caution!** SFrout deletes last 5 lines from each response, SFDC adds footer to each data stream. This might be organization specific and require your attention if you plan to use it in your organization.

- be default number of workers is equal to half of available threads of the machine

- by default rotating file log is limitted to 3 parts, up to 1_000_000 bytes each 

- progress bar is based on quantity of items and may show incorrect ETA if report's size vary significantly 

- currently only save to `csv` method is available

## Benchmarks

My testing set consist of 33 reports from various universes of SFDC with size between 200 kb to 200 mb. In total 1.4 gb of data.

Tests were not bounded by network bandwidth. Tests were evaluated on i7-8850H, DDR4 32 gb, Windows 10 x64.

Processing of the testing set vary between 3 and 8 minutes, results strongly correlate to SFDC performance on given time. Time of processing is correlated to size of the reports, bigger = longer.

## Final remarks

This app has been created based on environment of my organization. There is alternative way of Authenticating to SFDC based on security token, unfortunately this option was blocked in my organization and only SSO is available. 

## Documentation available on [Read the Docs](https://sfrout.readthedocs.io)

[![](https://github.com/LukaszHoszowski/sfrout/blob/main/docs/_static/rtd.png?raw=True)](https://sfrout.readthedocs.io)

## Release Notes

[Changelog](https://github.com/LukaszHoszowski/sfrout/blob/main/CHANGELOG.md)

## License

[Apache 2.0](https://github.com/LukaszHoszowski/sfrout/blob/main/LICENSE.md)
