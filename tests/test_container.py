from pathlib import WindowsPath
import pytest


@pytest.mark.usefixtures("sfdc_object")
class TestSfdcReportObject:
    def test_init_sfdc_report_object(self, sfdc_object):
        assert sfdc_object.name == 'TEST_REPORT_OBJ'
        assert sfdc_object.id == '11A1B000001abVa'
        assert sfdc_object.path == WindowsPath('C:\\Test')

@pytest.mark.usefixtures("list_sfdc_objects")
class TestReportContainerObject:
    def test_init_report_container_object(self, list_sfdc_objects):
        assert len(list_sfdc_objects) == 3

    def test_create_sfdc_reports(self, list_sfdc_objects):
        assert next(list_sfdc_objects._create_sfdc_reports()).name == 'TEST_REPORT_OBJ'

    def test_create_reports(self, list_sfdc_objects):
        assert len(list_sfdc_objects.create_reports()) == 3
