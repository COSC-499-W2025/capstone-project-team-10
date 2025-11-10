from pathlib import Path

import src.param.param as param


def param_setup():
    param.init()
    param.clear()


class TestParam:
    def test_param_defaults(self):
        param_setup()
        with open("src/param/param_defaults.json", "r") as default_params:
            default_data = param.json.load(default_params)
        for key in default_data:
            assert param.get(key) == default_data[key]

    def test_param_invalid_parse(self):
        # Created Corrupted param file for this test
        param_setup()
        invalid_param_file = param.optional_parameters_path
        open(invalid_param_file, "w").write('{"invalid_json": true,,}')
        param.load_additional_params()
        assert param.get("config") == {
            "project_name": param.project_name,
            "config_info": param.project_version,
        }

    def test_param_parse(self):
        param_setup()
        # Set a test param to ensure load/save works
        param.set("test_key", "test_value")
        param.load_additional_params()
        assert param.get("config") == {
            "project_name": param.project_name,
            "config_info": param.project_version,
        }

    def test_param_save(self):
        param_setup()
        param.save_additional_params()
        param.set("testing.test_key", "test_value")
        param.load_additional_params()
        assert param.get("testing.test_key") == "test_value"

    def test_param_not_found(self):
        param_setup()
        Path(param.optional_parameters_path).unlink(missing_ok=True)
        param.load_additional_params()
        assert param.get("config") == {
            "project_name": param.project_name,
            "config_info": param.project_version,
        }

    def test_param_clear(self):
        param_setup()
        param.set("testing.test_key", "test_value")
        param.clear()
        assert param.get("testing.test_key") is None

    def test_param_invalid_get(self):
        param_setup()
        assert param.get("testing.invalid_key") is None

    def test_param_invalid_set(self):
        param_setup()
        assert param.set("testing.invalid_key", "invalid_value") is False

    def test_param_invalid_remove(self):
        param_setup()
        assert param.remove("testing.invalid_key") is False

    def test_param_remove(self):
        param_setup()
        param.set("testing.test_key", "remove_value")
        param.remove("testing.test_key")
        param.load_additional_params()
        assert param.get("testing.test_key") is None
