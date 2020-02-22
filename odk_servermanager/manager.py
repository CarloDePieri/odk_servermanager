from typing import List

from bs4 import BeautifulSoup


class ServerManager:

    def _parse_preset(self, filename: str) -> List[str]:
        """Parse an Arma 3 preset and return the List of all selected mods names."""
        # Open the preset file and read its content
        with open(filename, "r") as f:
            xml = f.read()
        # Parse the file and extract all mods names
        parsed_xml = BeautifulSoup(xml, 'html.parser')
        mods_data = parsed_xml.select("tr[data-type=\"ModContainer\"]")
        mods_name = list(map(
            lambda x: x.select_one("td[data-type=\"DisplayName\"]").text,
            mods_data))
        return mods_name
