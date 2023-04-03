import pytest


@pytest.mark.usefixtures("connector", "sfdc_object")
class TestConnectorObject:
    def test_convert_domain_for_cookies_lookup(self, connector):
        assert connector._convert_domain_for_cookies_lookup() == "corp.my.salesforce.com"

    def test_parse_headers(self, connector):
        connector.sid = "XYZ"
        assert len(connector.headers) == 2
        connector._parse_headers()
        assert len(connector.headers) == 3
        assert connector.headers["Authorization"] == 'Bearer XYZ'

    def test_parse_report_url(self, connector, sfdc_object):
        connector.sid = "XYZ"
        assert connector._parse_report_url(sfdc_object) == "https://corp.my.salesforce.com/11A1B000001abVa?export=csv&enc=UTF-8&isdtp=p1"
        