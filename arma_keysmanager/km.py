from bs4 import BeautifulSoup


def parse_preset(filename):
    with open(filename, "r") as f:
        xml = f.read()

    parsed_xml = BeautifulSoup(xml, 'html.parser')
    mods_data = parsed_xml.select("tr[data-type=\"ModContainer\"]")
    mods_name = list(map(
        lambda x: x.select_one("td[data-type=\"DisplayName\"]").text,
        mods_data ))
    return mods_name
