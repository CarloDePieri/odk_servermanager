from bs4 import BeautifulSoup
import os
from typing import List


def parse_preset(filename: str) -> List[str]:
    """Parse an Arma preset and return the List of all selected mods names."""
    # Open the preset file and read its content
    with open(filename, "r") as f:
        xml = f.read()
    # Parse the file and extract all mods names
    parsed_xml = BeautifulSoup(xml, 'html.parser')
    mods_data = parsed_xml.select("tr[data-type=\"ModContainer\"]")
    mods_name = list(map(
        lambda x: x.select_one("td[data-type=\"DisplayName\"]").text,
        mods_data ))
    return mods_name

def clear_keys_folder(folder_name: str) -> None:
    """Delete every key in the Keys folder."""
    for filename in os.listdir(folder_name):
        file_path = os.path.join(folder_name, filename)
        file_ext = os.path.splitext(file_path)[-1].lower()
        if os.path.isfile(file_path) and (file_ext == ".bikey"):
            os.unlink(file_path)
