import pytest
from pathlib import WindowsPath
from queue import Queue
from sfrout.components.config import Config
from sfrout.components.connectors import SfdcConnector
from sfrout.components.containers import ReportsContainer, SfdcReport


# Config fixtures

single_sfdc_wo_opt_params = {
    "domain": "https://corp.my.salesforce.com/",
    "reports_csv_path": "./tests/sample_files/correct_single_sfdc.csv"
    }

multi_sfdc_wo_opt_params = {
    "domain": "https://corp.my.salesforce.com/",
    "reports_csv_path": "./tests/sample_files/correct_multi_sfdc.csv"
    }

single_sfdc_wo_opt_params_cli_path = {
    "domain": "https://corp.my.salesforce.com/",
    "reports_csv_path": "./tests/sample_files/correct_single_sfdc.csv",  
    "path": "C:\\CLI_Path"
    }

multi_sfdc_wo_opt_params_cli_path = {
    "domain": "https://corp.my.salesforce.com/",
    "reports_csv_path": "./tests/sample_files/correct_multi_sfdc.csv",  
    "path": "C:\\CLI_Path"
    }

single_sfdc_wo_opt_params_cli_report = {
    "domain": "https://corp.my.salesforce.com/",
    "reports_csv_path": "./tests/sample_files/correct_single_sfdc.csv", 
    "report": "correct_sfdc_report_with_optional_export_params_manual,11A1B000001abVa,C:\\Manual"
    }

multi_sfdc_wo_opt_params_cli_report = {
    "domain": "https://corp.my.salesforce.com/",
    "reports_csv_path": "./tests/sample_files/correct_multi_sfdc.csv", 
    "report": "correct_sfdc_report_with_optional_export_params_manual,11A1B000001abVa,C:\\Manual"
    }

single_sfdc_wo_opt_params_cli_threads = {
    "domain": "https://corp.my.salesforce.com/",
    "reports_csv_path": "./tests/sample_files/correct_single_sfdc.csv", 
    "threads": 1}

multi_sfdc_wo_opt_params_cli_threads = {
    "domain": "https://corp.my.salesforce.com/",
    "reports_csv_path": "./tests/sample_files/correct_multi_sfdc.csv", 
    "threads": 1}

single_sfdc_wo_opt_params_cli_report_cli_path_cli_threads = {
    "domain": "https://corp.my.salesforce.com/",
    "reports_csv_path": "./tests/sample_files/correct_single_sfdc.csv", 
    "report": "correct_sfdc_report_with_optional_export_params_manual,11A1B000001abVa,C:\\Manual", 
    "path": "C:\\CLI_Path",
    "threads": 1}

multi_sfdc_wo_opt_params_cli_report_cli_path_cli_threads = {
    "domain": "https://corp.my.salesforce.com/",
    "reports_csv_path": "./tests/sample_files/correct_multi_sfdc.csv", 
    "report": "correct_sfdc_report_with_optional_export_params_manual,11A1B000001abVa,C:\\Manual", 
    "path": "C:\\CLI_Path",
    "threads": 1}

single_sfdc_w_opt_params = {
    "domain": "https://corp.my.salesforce.com/",
    "reports_csv_path": "./tests/sample_files/correct_single_sfdc_opt_params.csv"
    }

multi_sfdc_w_opt_params = {
    "domain": "https://corp.my.salesforce.com/",
    "reports_csv_path": "./tests/sample_files/correct_multi_sfdc_opt_params.csv"
    }


@pytest.fixture(scope='class', params=[single_sfdc_wo_opt_params, 
                                       multi_sfdc_wo_opt_params])
def config_obj_wo_opt_params(request):
    return Config(**request.param)

@pytest.fixture(scope='class', params=[single_sfdc_wo_opt_params_cli_path, 
                                       multi_sfdc_wo_opt_params_cli_path])
def config_obj_w_cli_path(request):
    return Config(**request.param)

@pytest.fixture(scope='class', params=[single_sfdc_wo_opt_params_cli_report,
                                       multi_sfdc_wo_opt_params_cli_report])
def config_obj_w_cli_report(request):
    return Config(**request.param)

@pytest.fixture(scope='class', params=[single_sfdc_wo_opt_params_cli_threads,
                                       multi_sfdc_wo_opt_params_cli_threads])
def config_obj_w_cli_threads(request):
    return Config(**request.param)

@pytest.fixture(scope='class', params=[single_sfdc_wo_opt_params_cli_report_cli_path_cli_threads,
                                       multi_sfdc_wo_opt_params_cli_report_cli_path_cli_threads])
def config_obj_w_cli_report_cli_path_cli_threads(request):
    return Config(**request.param)

@pytest.fixture(scope='class', params=[single_sfdc_w_opt_params,
                                       multi_sfdc_w_opt_params])
def config_obj_w_opt_params(request):
    return Config(**request.param)

# Connector fixtures

sfdc_report = {'name': 'TEST_REPORT_OBJ', 
          'id': '11A1B000001abVa',
          'path': WindowsPath('C:\\Test')}

list_of_sfdc_object_params = [sfdc_report for _ in range(3)]

@pytest.fixture(scope='class', params=[sfdc_report])
def sfdc_object(request):
    return SfdcReport(**request.param)

@pytest.fixture(scope='class', params=[list_of_sfdc_object_params])
def list_sfdc_objects(request):
    return ReportsContainer(reports_params_list=request.param,
                            summary_path=WindowsPath('C:/'))

@pytest.fixture(scope='class')
def connector():
    queue = Queue()
    domain = "https://corp.my.salesforce.com/"
    return SfdcConnector(queue, domain=domain)
