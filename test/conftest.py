import pytest
import json
from downloader.Downloader import Downloader

@pytest.fixture
def downloader():
    with open('download_url.json', "r") as json_file:
        downloadlist = json.load(json_file)['url']
    downloader = Downloader.Downloader(downloadlist)
    return downloader 