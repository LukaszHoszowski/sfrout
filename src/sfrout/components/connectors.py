import logging
import asyncio
import requests
import aiohttp
import browser_cookie3
import webbrowser

from typing import Protocol, runtime_checkable
from queue import Queue
from datetime import datetime
from tqdm.asyncio import tqdm
from time import sleep

from .containers import ReportProtocol


logger_main = logging.getLogger(__name__)


@runtime_checkable
class ConnectorProtocol(Protocol):
    """Protocol class for connector object.

    :param queue: shared queue object
    :type queue: :class:`Queue`
    :param timeout: request's timeout value in seconds
    :type timeout: int
    :param headers: headers required to establish the connection
    :type headers: dict[str, str]
    """

    queue: Queue
    timeout: int
    headers: dict[str, str]

    def check_connection(self) -> bool:
        """Checks connection with given domain.

        :return: flag, ``True`` if connection is established, ``False`` otherwise.
        :rtype: bool
        """
        ...

    async def report_gathering(self, reports: list[ReportProtocol], session: aiohttp.ClientSession) -> None:
        """Collects asynchronous responses from the servers.

        :param reports: collection of :class:`ReportProtocol` objects.
        :type reports: list[:class:`ReportProtocol`]
        :param session: HTTP client session object to handle request in transaction.
        :type session: :class:`ClientSession`
        """
        ...


class SfdcConnector():
    """Concrete class representing SFDC Connector object.

    :param queue: shared queue object
    :type queue: :class:`Queue`
    :param domain: SalesForce domain of your organization -> `"https://corp.my.salesforce.com/"`
    :type domain: str
    :param verbose: flag, parameter used as switch between progress bar and logging to stdout, defaults to False
    :type timeout: int, optional
    :param timeout: Request's timeout value in seconds, defaults to 900
    :type timeout: int, optional
    :param headers: headers required connection, defaults to {'Content-Type': 'application/csv', 'X-PrettyPrint': '1'}
    :type headers: dict[str, str], optional
    :param export_params: GET request parameters required by SFDC, defaults to '?export=csv&enc=UTF-8&isdtp=p1'
    :type export_params: str, optional
    """

    def __init__(self,
                 *,
                 queue: Queue,
                 domain: str,
                 verbose: bool = False, 
                 timeout: int = 900,
                 headers: dict[str, str] = {'Content-Type': 'application/csv',
                                            'X-PrettyPrint': '1'}):

        """Constructor method for SFDC Connector.
        """

        self.queue: Queue = queue
        self.verbose: bool = verbose
        self.domain: str = domain 
        self.timeout: int = timeout
        self.headers: dict[str, str] = headers
        self.check:bool = False
        self.sid: str = ""
        self.sid_valid: bool = False
        self.edge_path: str = '"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe" --profile-directory=Default %s'

    def _convert_domain_for_cookies_lookup(self) -> str:
        """Converts domain string according to ``sid`` CookieJar lookup requirements.

        :return: converted url complaiant with CookieJar schema
        :rtype: str
        """

        logger_main.debug('Parsing domain key for cookies')
        return self.domain.replace('https://', '').replace('/', '')

    def _parse_headers(self) -> None:
        """Parses headers for request.
        """

        logger_main.debug('Parsing headers for SFDC request check')
        self.headers['Authorization'] = ''.join(
            filter(None, ['Bearer ', self.sid]))

        return None

    def _intercept_sid(self) -> str:
        """Intercepts `sid` from MS Edge's CookieJar.

        :return: Intercepted ``sid`` or empty string if ``sid`` doesn't exist.
        :rtype: str
        """

        logger_main.info('SID interception started')
        try:
            logger_main.debug("Trying to access MS Edge's CookieJar")
            cookie_jar = browser_cookie3.edge()

            logger_main.debug('Retrieving SID entry from CookieJar')
            sid = [cookie.value for cookie in cookie_jar if cookie.name ==
                   'sid' and cookie.domain == self._convert_domain_for_cookies_lookup()]

            return sid[0] or ""
        except:
            logger_main.debug('SID entry not there')

            return ""

    def _open_sfdc_site(self) -> None:
        """Opens SFDC website on given domain url if ``sid`` is not present or not valid.
        """
        
        logger_main.warning(
            'SID not valid! -> Login to SFDC -> SalesForce webpage will open shortly')

        logger_main.debug('Openning SFDC webside to log in to SalesForce')
        
        self.sid = ""
        webbrowser.get(self.edge_path).open(self.domain)

        logger_main.debug(
            'Starting 20 sec sleep to let user log in to SalesForce')
        sleep(20)

        return None
    
    def _sid_check(self) -> bool:
        """Checks ``sid`` valididty for given SFDC domain.

        :return: Flag, ``True`` if ``sid`` was valid, ``False`` when wasn't.
        :rtype: bool
        """
        
        response = requests.get(self.domain,
                                cookies={'sid': self.sid},
                                allow_redirects=True)
        
        if response.headers['Cache-Control'] == 'private':
            logger_main.info('SID ok!')

            self.sid_valid = True
            self.check = True

            return True
        else:
            logger_main.critical('SID not ok!!!')
            self.sid = ""
            self.sid_valid = False
            self.check = False
            
            return False
          
    def check_connection(self) -> bool:
        """Checks the connection with given domain and ``sid`` validity.

        :return: flag, ``True`` if connection was successful, ``False`` if wasn't.
        :rtype: bool
        """
        logger_main.info("SID checking in progress ...")

        self._parse_headers()
        self.sid = self._intercept_sid()
        self._sid_check()

        if not self.sid:
            self._open_sfdc_site()
                
            while not self.sid_valid:
                logger_main.info('intercepting SID! Hold on tight!')
                self.sid = self._intercept_sid()
                sleep(2)
                self._sid_check()
                
        return True

    def _parse_report_url(self, report: ReportProtocol) -> str:
        """Parses report object url.

        :param report: instance of :class:`ReportProtocol`
        :type report: :class:`ReportProtocol`
        :return: parsed url
        :rtype: str
        """
        return self.domain + report.id + report.export_params

    
    async def _request_report(self, report: ReportProtocol, session: aiohttp.ClientSession) -> None:
        """Sends asynchronous request to given domain with given parameters within shared session. Checks response status:
            | 200: response is saved in :meth:`ReportProtocol.response` , :meth:`ReportProtocol.valid` set to ``True`` , :class:`ReportProtocol` is being put to the ``queue`` .
            | 404: error in response, :meth:`ReportProtocol.valid` set to ``False`` , no retries.
            | 500: request timeour, :meth:`ReportProtocol.valid` set to ``False`` , another attempt.
            | *: unknown error, :meth:`ReportProtocol.valid` set to ``False``, another attempt.

        :param report: instance of :class:`ReportProtocol`
        :type report: :class:`ReportProtocol`
        :param session: shared session object
        :type session: :class:`aiohttp.ClientSession`
        """

        report.created_date = datetime.now()

        report_url = self._parse_report_url(report)

        logger_main.info("%s -> Sending request", report.name)
        logger_main.debug(
            'Sending asynchronous report request with params: %s, %s', report_url, self.headers)

        while not report.valid and report.attempt_count < 20:
            async with session.get(report_url,
                                   headers=self.headers,
                                   cookies={'sid': str(self.sid)},
                                   timeout=self.timeout,
                                   allow_redirects=True) as r:

                report.attempt_count += 1

                if r.status == 200:
                    logger_main.info(
                        '%s -> Request successful, retrieving content', report.name)
                    try:
                        report.response = await r.text()
                        report.valid = True
                        logger_main.debug(
                            'Sending the content to the queue for processing, %s elements in the queue before transfer', self.queue.qsize())
                        self.queue.put(report)
                        logger_main.debug(
                            '%s succesfuly downloaded and put to the queue', report.name)
                    except aiohttp.ClientPayloadError as e:
                        logger_main.warning(
                            '%s is invalid, Unexpected end of stream, SFDC just broke the connection -> %s', report.name, e)
                        continue
                elif r.status == 404:
                    logger_main.error(
                        '%s is invalid, Report does not exist - check ID, SFDC respond with status %s - %s', report.name, r.status, r.reason)
                    report.valid = False
                    break
                elif r.status == 500:
                    logger_main.warning(
                        '%s is invalid, Timeout, SFDC respond with status %s - %s', report.name, r.status, r.reason)
                    report.valid = False
                else:
                    logger_main.warning(
                        '%s is invalid, Unknown Error, SFDC respond with status %s - %s', report.name, r.status, r.reason)
                    report.valid = False
        return None

    async def _toggle_progress_bar(self, tasks: list[asyncio.Task]) -> None:
        """Toggles between showing progress bar or stdout logging.

        :param tasks: collection of asynchronous request tasks
        :type tasks: list[:class:`asyncio.Task`]
        """
        print("")

        if not self.verbose:
            
            _ = [await task_ for task_ in tqdm.as_completed(tasks, total=len(tasks))]

    def _create_async_tasks(self, reports: list[ReportProtocol], session: aiohttp.ClientSession) -> list[asyncio.Task]:
        """Creates collection of asynchronous request tasks. 

        :param reports: collection of :class:`ReportProtocol` instances
        :type reports: list[:class:`ReportProtocol`]
        :param session: shared, asynchronous session
        :type session: :class:`aiohttp.ClientSession`
        :return: collection of asynchronous request tasks
        :rtype: list[:class:`asyncio.Task`]
        """

        logger_main.debug('Creating tasks for asynchronous processing')
        return [asyncio.create_task(self._request_report(report, session)) for report in reports]

    async def _report_request_all(self, reports: list[ReportProtocol], session: aiohttp.ClientSession) -> None:
        """Orchestrates entire process of processing tasks.

        :param reports: collection of :class:`ReportProtocol` instances
        :type reports: list[:class:`ReportProtocol`]
        :param session: shared, asynchronous session
        :type session: :class:`aiohttp.ClientSession`
        """

        tasks = self._create_async_tasks(reports, session)

        await self._toggle_progress_bar(tasks)

        await asyncio.gather(*tasks)

        return None

    async def handle_requests(self, reports: list[ReportProtocol]) -> None:
        """Creates session and processes asynchronous tasks.

        :param reports: collection of :class:`ReportProtocol` instances
        :type reports: list[:class:`ReportProtocol`]
        """

        logger_main.debug('Awaiting responses')
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            await self._report_request_all(reports, session)

        return None

if __name__ == '__main__':
    pass
