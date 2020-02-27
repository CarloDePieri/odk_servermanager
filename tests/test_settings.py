import pytest

from odk_servermanager.settings import ServerConfigSettings, ServerBatSettings


class TestAServerConfigSettings:
    """Test: A Server Config Settings..."""

    def test_should_require_certain_fields(self, assert_requires_arguments):
        """A server config settings should require certain fields."""
        assert_requires_arguments(ServerConfigSettings, ['hostname', 'password', 'password_admin', 'template'])

    def test_should_accept_additional_field(self):
        """A server config settings should accept additional field."""
        hostname = "HOSTNAME"
        password = "secure"
        password_admin = "verysecure"
        template = "mission.template"
        myconfig = "someconfig"
        sc = ServerConfigSettings(
            hostname=hostname,
            password=password,
            password_admin=password_admin,
            template=template,
            myconfig=myconfig
        )
        assert sc.hostname == hostname
        assert sc.password == password
        assert sc.password_admin == password_admin
        assert sc.template == template
        assert sc.myconfig == myconfig


@pytest.mark.runthis
class TestAServerBatSettings:
    """Test: A Server Bat Settings..."""

    def test_should_require_certain_arguments(self, assert_requires_arguments):
        """A server bat settings should require certain arguments."""
        assert_requires_arguments(ServerBatSettings, ["server_title", "server_root", "server_port", "server_config",
                                                      "server_cfg", "server_max_mem"])

    def test_should_set_its_fields(self):
        """A server bat settings should set its fields."""
        server_title = "title"
        server_root = r"C:\somefolder\someotherfolder"
        server_port = "2002"
        server_config = "somepath config"
        server_cfg = "somepath cfg"
        server_max_mem = "42"
        sb = ServerBatSettings(server_title=server_title, server_root=server_root, server_port=server_port,
                               server_config=server_config, server_cfg=server_cfg, server_max_mem=server_max_mem)
        assert sb.server_title == server_title
        assert sb.server_root == server_root
        assert sb.server_port == server_port
        assert sb.server_config == server_config
        assert sb.server_cfg == server_cfg
        assert sb.server_max_mem == server_max_mem
        assert sb.server_drive == "C:"  # this should be computed
        assert sb.server_flags == ""  # this should have an empty default
        sb = ServerBatSettings(server_title=server_title, server_root=server_root, server_port=server_port,
                               server_config=server_config, server_cfg=server_cfg, server_max_mem=server_max_mem,
                               server_flags="-custom", custom_field="custom")
        assert sb.server_flags == "-custom"
        assert sb.custom_field == "custom"


