from pathlib import Path
import pytest


@pytest.mark.usefixtures("config_obj_wo_opt_params")
class TestConfigWoParams:
    def test_config_init_wo_params(self, config_obj_wo_opt_params):
        assert len(config_obj_wo_opt_params.report_params_list) >= 1
    
    def test_config_sfdc_wo_params_id(self, config_obj_wo_opt_params):    
        for dict in config_obj_wo_opt_params.report_params_list:
            assert dict['id'] == '11A1B000001abVa'
    
    def test_config_sfdc_wo_params_path(self, config_obj_wo_opt_params):    
        for dict in config_obj_wo_opt_params.report_params_list:
            assert isinstance(dict['path'], Path) 

    def test_config_sfdc_wo_params_name(self, config_obj_wo_opt_params):    
        for dict in config_obj_wo_opt_params.report_params_list:
            assert 'SFDC_Report' in dict['name']

@pytest.mark.usefixtures("config_obj_w_opt_params")
class TestConfigWParams:
    def test_config_w_opt_params(self, config_obj_w_opt_params):
        for dict in config_obj_w_opt_params.report_params_list:
            assert '?export=&xf=localecsv&enc=UTF-8&scope=organization&pv1=4/1/2019&pv2=4/7/2019&isdtp=p1' in dict['params']

@pytest.mark.usefixtures("config_obj_w_cli_path")
class TestConfigPath:
    def test_config_sfdc_path(self, config_obj_w_cli_path):    
        for dict in config_obj_w_cli_path.report_params_list:
            assert isinstance(dict['path'], Path)
            assert dict['path'] == Path("C:\\CLI_Path")

@pytest.mark.usefixtures("config_obj_w_cli_report")
class TestConfigReport:
    def test_config_sfdc_report(self, config_obj_w_cli_report):    
        assert len(config_obj_w_cli_report.report_params_list) == 1
        assert config_obj_w_cli_report.report_params_list[0]['name'] == "correct_sfdc_report_with_optional_export_params_manual"
        assert config_obj_w_cli_report.report_params_list[0]['id'] == "11A1B000001abVa"
        assert config_obj_w_cli_report.report_params_list[0]['path'] == Path("C:\\Manual")
        assert config_obj_w_cli_report.report_params_list[0]['params'] == ""

@pytest.mark.usefixtures("config_obj_w_cli_threads")
class TestConfigThreads:
    def test_config_sfdc_thread(self, config_obj_w_cli_threads):    
        assert config_obj_w_cli_threads.threads == 1

@pytest.mark.usefixtures("config_obj_w_cli_threads")
class TestConfigAll:
    def test_config_sfdc_all(self, config_obj_w_cli_report_cli_path_cli_threads):    
        assert config_obj_w_cli_report_cli_path_cli_threads.threads == 1
        assert config_obj_w_cli_report_cli_path_cli_threads.report_params_list[0]['name'] == "correct_sfdc_report_with_optional_export_params_manual"
        assert config_obj_w_cli_report_cli_path_cli_threads.report_params_list[0]['id'] == "11A1B000001abVa"
        assert config_obj_w_cli_report_cli_path_cli_threads.report_params_list[0]['path'] == Path("C:\\CLI_Path")
        assert config_obj_w_cli_report_cli_path_cli_threads.report_params_list[0]['params'] == ""
