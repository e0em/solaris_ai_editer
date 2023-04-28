# 將 disk-tool.py import 進來
import disk_tool


# 寫一個 disk_tool.linux_cmd() 的unitest
def test_linux_cmd():
    assert disk_tool.linux_cmd("uname -i") == "x86_64\n"


# disk_tool.linux_cmd_json_dict()  的unitest
def test_linux_cmd_json_dict():
    assert (
        disk_tool.linux_cmd_json_dict("sudo lshw -c cpu -json")[0]["class"]
        == "processor"
    )
