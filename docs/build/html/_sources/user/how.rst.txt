.. _how:

How does it work?
=================

**SFrout** seems to be simple application which just downloads the files from SFDC. In fact a lot of things is happening under the hood. Let's try to understand why it isn't as simple as it looks. Most of the complexity comes with SSO/SAML authentication so let's start here.


Authentication
--------------

Authorization and authentication in SFDC is based on `sid` cookie entry for SSO or on security tokens in other cases. 

SFrout will try to connect to CookieJar of your MS Edge browser and find `sid` entry for given domain. If `sid` is not found, the app will open MS Edge browser and request given SFDC domain. You will be asked to log in as usual. After 20 seconds program will retry to find `sid` in your CookieJar. Browsers usually store cookies in SQlite db. This information is not being transfered to db immediately, it can be triggered by closing the browser but it isn't the most elegant solution. SFrout will ask for `sid` in 2 seconds intervals as long as `sid` will be available. Entire process will repeat as many times as it takes.


Sending requests
----------------

SFDC supports export GET requests by adding `?export=csv&enc=UTF-8&isdtp=p1` to address of your report supplemented with headers and above `sid` entry. In response you will receive CSV-like data stream. Time window for entire operation is fixed and equal to **15 minutes**. If you will not be able to receive response in this narrow time window connection will be forceable shutdown and request cancelled regardless of the stage.

Requests are send out asynchronously to speed things up and restrain memory consumption to bare minimum. Once request will fail, regardless of that what has caused failure, SFrout will retry. Limit of attempts has been set to **20**. Once request is successful, response is saved in Report object and put to the queue for further processing.


Handler
-------

Thread based solution for saving request responses to a file. 

File handler spawns workers in separate threads. Number of workers is equal to half of available threads on your machine (e.g. if your cpu has 6 cores and 12 threads SFR will spawn 6 workers). If information about available resources is not reachable it will default to **2**. Such approach will not dramatically slow down other applications on your computer and will secure required resources for SFR. Each worker will observe `Queue`, if something will be put into `Queue` one of the workers will start processing of the report. Bare in mind that each saving operation erases response and content of the report due to memory consumption. `Queue` size is unlimited so sooner or later workers will handle entire workload. Workers will die once `Queue` will send signal that they shouldn't expect any new items. These workers who are just processing items will finish their jobs and die quietly.

All files are processed by `Pandas` which gives wide palette of available formats. Unfortunately such flexibility somes with the price. In current shape `Pandas` isn't the best in saving `csv` files due to `numpy` engine. On top of that `Pandas` is a relatively heavy library. I plan to switch to some other processing engine in the future.


Limitations
-----------

- **Caution!** SFrout deletes last 5 lines from each response, SFDC adds footer to each data stream. This might be organization specific and require your attention if you plan to use it in your organization.

- be default number of workers is equal to half of available threads of the machine

- by default rotating file log is limitted to 3 parts, up to 1_000_000 bytes each 

- progress bar is based on quantity of items and may show incorrect ETA if report's size vary significantly 

- currently only save to `csv` method is available


Benchmarks
----------

My testing set consist of 33 reports from various universes of SFDC with size between 200 kb to 200 mb. In total 1.4 gb of data.

Tests were not bounded by network bandwidth. Tests were evaluated on i7-8850H, DDR4 32 gb, Windows 10 x64.

Processing of the testing set vary between 3 and 8 minutes, results strongly correlate to SFDC performance on given time. Time of processing is correlated to size of the reports, bigger = longer.


Final remarks
-------------

This app has been created based on environment of my organization. There is alternative way of Authenticating to SFDC based on security token, unfortunately this option was blocked in my organization and only SSO is available. 


That's it! Shortly after executing the command **SFrout** might ask to log in to SFDC in MS Edge. Once you authenticate entire process will start, progres bar will show up. Once **SFrout** finishes you will see conveninent table with summary. Shortly after your reports will be dropped to given location. 
Time required for entire operation is impacted by report size, bandwidth of your internet connection and current SFDC condition.

-----------------------

.. Still hungry, let's have a look at the code! Check out the :ref:`x <x>` section.
