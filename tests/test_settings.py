import pytest

from odk_servermanager.settings import ServerConfigSettings, ServerBatSettings, ServerInstanceSettings


class TestAServerConfigSettings:
    """Test: A Server Config Settings..."""

    def test_should_require_certain_fields(self, assert_requires_arguments):
        """A server config settings should require certain fields."""
        assert_requires_arguments(ServerConfigSettings, ['hostname', 'password', 'password_admin', 'mission_template'])

    def test_should_have_decent_defaults(self):
        """A server config settings should have decent defaults."""
        sc = ServerConfigSettings(
            hostname="test",
            password="123",
            password_admin="456",
            mission_template="mission.test"
        )
        assert sc.config_template == ""

    def test_should_accept_additional_field(self):
        """A server config settings should accept additional field."""
        hostname = "HOSTNAME"
        password = "secure"
        password_admin = "verysecure"
        template = "mission.template"
        my_template = r"c:\myconfig.txt"
        myconfig = "someconfig"
        sc = ServerConfigSettings(
            hostname=hostname,
            password=password,
            password_admin=password_admin,
            mission_template=template,
            config_template=my_template,
            myconfig=myconfig
        )
        assert sc.hostname == hostname
        assert sc.password == password
        assert sc.password_admin == password_admin
        assert sc.mission_template == template
        assert sc.myconfig == myconfig
        assert sc.config_template == my_template


class TestAServerBatSettings:
    """Test: A Server Bat Settings..."""

    def test_should_require_certain_arguments(self, assert_requires_arguments):
        """A server bat settings should require certain arguments."""
        assert_requires_arguments(ServerBatSettings, ["server_title", "server_port", "server_config_file_name",
                                                      "server_cfg_file_name", "server_max_mem"])

    def test_should_have_decent_defaults(self):
        """A server bat settings should have decent defaults."""
        server_title = "title"
        server_port = "2002"
        server_config_file_name = "somepath config"
        server_cfg_file_name = "somepath cfg"
        server_max_mem = "42"
        sb = ServerBatSettings(server_title=server_title, server_port=server_port,
                               server_config_file_name=server_config_file_name,
                               server_cfg_file_name=server_cfg_file_name, server_max_mem=server_max_mem)
        assert sb.server_flags == ""
        assert sb.bat_template == ""

    def test_should_set_its_fields(self):
        """A server bat settings should set its fields."""
        server_title = "title"
        server_port = "2002"
        server_config_file_name = "somepath config"
        server_cfg_file_name = "somepath cfg"
        server_max_mem = "42"
        bat_template = r"c:\mytemplate.txt"
        sb = ServerBatSettings(server_title=server_title, server_port=server_port,
                               server_config_file_name=server_config_file_name, bat_template=bat_template,
                               server_cfg_file_name=server_cfg_file_name, server_max_mem=server_max_mem)
        assert sb.server_title == server_title
        assert sb.server_port == server_port
        assert sb.server_config_file_name == server_config_file_name
        assert sb.server_cfg_file_name == server_cfg_file_name
        assert sb.server_max_mem == server_max_mem
        assert sb.bat_template == bat_template
        sb = ServerBatSettings(server_title=server_title, server_port=server_port,
                               server_config_file_name=server_config_file_name,
                               server_cfg_file_name=server_cfg_file_name, server_max_mem=server_max_mem,
                               server_flags="-custom", custom_field="custom")
        assert sb.server_flags == "-custom"
        assert sb.custom_field == "custom"


class TestAServerInstanceSettings:
    """Test: A Server Instance Settings..."""

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request):
        """TestAServerInstanceSettings setup"""
        request.cls.sb = ServerBatSettings("title", "c:", "2000", r"c:\server.config", r"c:\server.cfg", "128")
        request.cls.sc = ServerConfigSettings("title", "123", "456", "missionName")

    def test_should_have_some_required_arguments(self, assert_requires_arguments):
        """A server instance settings should have some required arguments."""
        assert_requires_arguments(ServerInstanceSettings, ["server_instance_name", "bat_settings", "config_settings"])

    def test_should_have_decent_defaults(self):
        """A server instance settings should have decent defaults."""
        server_instance_name = "training"
        si = ServerInstanceSettings(server_instance_name=server_instance_name,
                                    bat_settings=self.sb, config_settings=self.sc)
        assert si.arma_folder == r"C:\Program Files (x86)\Steam\steamapps\common\Arma 3"
        assert si.mods_to_be_copied == []
        assert si.linked_mod_folder_name == "!Mods_linked"
        assert si.copied_mod_folder_name == "!Mods_copied"
        assert si.server_instance_prefix == "__server__"
        assert si.server_instance_root == si.arma_folder
        assert si.user_mods_list == []
        assert si.server_mods_list == []
        assert si.skip_keys == ["!DO_NOT_CHANGE_FILES_IN_THESE_FOLDERS"]
        assert si.mod_fix_settings == {}

    def test_should_set_its_fields(self):
        """A server instance settings should set its fields."""
        server_instance_name = "training"
        arma_folder = r"c:\new path"
        mods_to_be_copied = ["CBA_A3"]
        linked_mod_folder_name = "!M_linked",
        copied_mod_folder_name = "!M_copied",
        server_instance_prefix = "__instance__"
        server_instance_root = r"c:\instance-path"
        server_mods_list = ["ODKMIN"]
        user_mods_list = ["ace", "CBA_A3"]
        skip_keys = ["CBA_A3"]
        mod_fix_settings = ["CBA_A3"]
        si = ServerInstanceSettings(server_instance_name=server_instance_name,
                                    bat_settings=self.sb, config_settings=self.sc,
                                    arma_folder=arma_folder,
                                    mods_to_be_copied=mods_to_be_copied, linked_mod_folder_name=linked_mod_folder_name,
                                    copied_mod_folder_name=copied_mod_folder_name,
                                    server_instance_prefix=server_instance_prefix,
                                    server_instance_root=server_instance_root,
                                    user_mods_list=user_mods_list, server_mods_list=server_mods_list,
                                    skip_keys=skip_keys, mod_fix_settings=mod_fix_settings)
        assert si.server_instance_name == server_instance_name
        assert si.arma_folder == arma_folder
        assert si.mods_to_be_copied == mods_to_be_copied
        assert si.linked_mod_folder_name == linked_mod_folder_name
        assert si.copied_mod_folder_name == copied_mod_folder_name
        assert si.server_instance_prefix == server_instance_prefix
        assert si.server_instance_root == server_instance_root
        assert si.user_mods_list == user_mods_list
        assert si.server_mods_list == server_mods_list
        assert si.skip_keys == skip_keys + ["!DO_NOT_CHANGE_FILES_IN_THESE_FOLDERS"]
        assert si.mod_fix_settings == mod_fix_settings
        assert si.server_drive == "c:"  # this is computed

    def test_should_accept_other_settings_container(self):
        """A server instance settings should accept other settings container."""
        si = ServerInstanceSettings("testing", bat_settings=self.sb, config_settings=self.sc)
        assert si.bat_settings == self.sb
        assert si.config_settings == self.sc
