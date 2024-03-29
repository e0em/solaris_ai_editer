#! env python3
# This example shows how to change the items of a ListBox widget
# when the current selection of a DropDown widget changes.
#
import picotui.screen as scn
import picotui.widgets as wgs
import re

# from picotui.defs import C_B_WHITE, C_WHITE, C_B_BLUE, C_BLACK
import picotui.defs as defs


def linux_cmd(command):
    import subprocess

    try:
        output = subprocess.check_output(command, shell=True)
        return output.decode()
    except subprocess.CalledProcessError as e:
        print(e.output.decode())
        return e.output.decode()
        # raise e


def linux_cmd_json_dict(command):
    import json

    output = linux_cmd(command)
    return json.loads(output)


def linux_all_disk_list():
    import subprocess

    lsblk_result = "lsblk -S -J -o SERIAL,NAME,TRAN,WWN,VENDOR,MODEL,path,type"
    hdd_test_cmd_disk_device_dict = linux_cmd_json_dict(lsblk_result)["blockdevices"]
    print(hdd_test_cmd_disk_device_dict)
    return hdd_test_cmd_disk_device_dict


def hdd_test_compose(disk_name, action):
    hdd_test_cmd_partition_info = "sudo sgdisk -p {device_name}"
    hdd_test_cmd_clean_disk_partition_head = (
        "sudo dd if=/dev/zero of={device_name} status=progress bs=512 count=34"
    )
    hdd_test_cmd_clean_disk_partition_tail = (
        "sudo dd if=/dev/zero of={device_name} bs=512 count=34 seek={seek_no}"
    )
    hdd_test_cmd_clean_disk_partition_tail_seek = (
        "sudo /sbin/blockdev --getsz {device_name}"
    )
    hdd_test_cmd_read_whole_disk = "sudo dd if={device_name} of=/dev/null status=progress bs=256M conv=sync,noerror"
    hdd_test_cmd_write_whole_disk = "sudo dd if=/dev/zero of={device_name} status=progress bs=256M conv=sync,noerror"
    hdd_test_cmd_format_whole_disk = "sudo mkfs.ext4 {device_name}"
    hdd_test_cmd_smartctl = "sudo smartctl -x -a -T permissive -i {device_name}"
    if action == "partition_info":
        return_cmd = hdd_test_cmd_partition_info.format(device_name=disk_name)
    elif action == "clean_disk_partition_head":
        return_cmd = hdd_test_cmd_clean_disk_partition_head.format(
            device_name=disk_name
        )
    elif action == "clean_disk_partition_tail":
        seek_no = linux_cmd(
            hdd_test_cmd_clean_disk_partition_tail_seek.format(device_name=disk_name)
        )
        return_cmd = hdd_test_cmd_clean_disk_partition_tail.format(
            device_name=disk_name, seek_no=int(seek_no) - 34
        )
    elif action == "read_whole_disk":
        return_cmd = hdd_test_cmd_read_whole_disk.format(device_name=disk_name)
    elif action == "write_whole_disk":
        return_cmd = hdd_test_cmd_write_whole_disk.format(device_name=disk_name)
    elif action == "format_whole_disk":
        return_cmd = hdd_test_cmd_format_whole_disk.format(device_name=disk_name)
    elif action == "smartctl":
        return_cmd = hdd_test_cmd_smartctl.format(device_name=disk_name)
    else:
        return_cmd = ""

    print("執行指令：", return_cmd)
    return return_cmd


if __name__ == "__main__":
    import os

    s = scn.Screen()
    disks_dict = {}
    disk_interfaces = set()
    disk_device_name_list = []
    disk_model_and_device_name = []
    for i in linux_all_disk_list():
        disks_dict[i["name"]] = i
        disk_interfaces.add(i["tran"])
        disk_device_name_list.append(i["path"])
        disk_model_and_device_name.append(i["name"] + "," + i["model"] + "," + i["serial"])
        #disk_model_and_device_name.append(i["model"] + "," + i["name"])

    print(disks_dict)
    # choices = disks_dict.items()
    choices = list(disk_interfaces)

    try:
        s.init_tty()
        s.enable_mouse()
        s.attr_color(defs.C_WHITE, defs.C_BLACK)
        s.cls()
        s.attr_reset()
        d = wgs.Dialog(5, 5, 20, 12, "芙奕達硬碟檢測工具")

        # DropDown and ListBox widgets
        d.add(1, 1, "選擇硬碟:")
        # 下拉選單，寬 15，選單內容為 choices，dropdown_h 高度6
        w_dropdown_target_disk = wgs.WDropDown(15, ["All"] + choices, dropdown_h=6)
        # 將下拉過濕工具放置地方，左上角 Col:1 Row:11
        d.add(11, 1, w_dropdown_target_disk)

        d.add(1, 3, "List:")
        w_listbox = wgs.WListBox(60, 6, disk_model_and_device_name)
        d.add(1, 4, w_listbox)

        # Filter the ListBox based on the DropDown selection
        def dropdown_changed(w):
            new_choices = []
            for i in disks_dict.keys():
                if (
                    w.items[w.choice] == "All"
                    or w.items[w.choice] == disks_dict[i]["tran"]
                ):
                    new_choices.append(
                            disks_dict[i]["name"] + "," + disks_dict[i]["model"] + "," + disks_dict[i]["serial"]
                    )

            # As we're going to set completely new items, reset current/top item of the widget
            w_listbox.top_line = 0
            w_listbox.cur_line = 0
            w_listbox.row = 0
            w_listbox.set_items(new_choices)

        w_dropdown_target_disk.on("changed", dropdown_changed)

        d.add(1, 13, "選擇檢測:")
        w_dropdown_test_type = wgs.WDropDown(
            28,
            [
                "No Action",
                "All in Once",
                "Read Disk Partition info",
                "Read SMART info",
                "Read All Disk",
                "Write All Disk",
                "Write&Read All Disk",
                "Clean Disk Partition head",
                "Clean Disk Partition tail",
                "Clean Disk Partition all",
                "mke2fs Disk",
            ],
            dropdown_h=11,
        )
        d.add(11, 13, w_dropdown_test_type)
        # 增加一個 checkbox  widget，左上角 Col:1 Row:14
        w_checkbox = wgs.WCheckbox("save output to log file", True)
        # 將 checkbox 放置地方，左上角 Col:1 Row:14
        d.add(11, 14, w_checkbox)
        # 境外按鈕，左上角 Col:8 Row:15

        b = wgs.WButton(8, "OK")
        d.add(2, 15, b)
        b.finish_dialog = "ACTION_OK"
        b = wgs.WButton(8, "Cancel")
        d.add(12, 15, b)
        b.finish_dialog = "ACTION_CANCEL"

        res = d.loop()
    finally:
        s.goto(0, 50)
        s.cursor(True)
        s.disable_mouse()
        s.deinit_tty()
    # 打印出 checkbox 的狀態
    print("Show command output:", w_checkbox.choice)
    # 打印出 w_listbox 的選擇中的結果
    print("Result:", w_listbox.get_cur_line())
    # 以選定的硬碟 設定 device name
    target_disk_name = w_listbox.get_cur_line()
    print(disks_dict)
    target_disk_device_name = disks_dict[target_disk_name.split(",")[0]]["path"]
    print("選定硬碟:", target_disk_device_name)
    # 以選定的action 設定行動指令
    action_type = w_dropdown_test_type.items[w_dropdown_test_type.get()]
    print("執行內容：", action_type)
    if action_type == "Read All Disk":
        output_message = linux_cmd(
            hdd_test_compose(target_disk_device_name, "read_whole_disk")
        )
    elif action_type == "Write All Disk":
        output_message = linux_cmd(
            hdd_test_compose(target_disk_device_name, "write_whole_disk")
        )
    elif action_type == "Write&Read All Disk":
        output_message = linux_cmd(
            hdd_test_compose(target_disk_device_name, "write_whole_disk")
        )
        output_message_2 = linux_cmd(
            hdd_test_compose(target_disk_device_name, "read_whole_disk")
        )
        output_message = output_message + "\n" + output_message_2 
    elif action_type == "All in Once":
        output_message_1 = linux_cmd(
            hdd_test_compose(target_disk_device_name, "smartctl")
        )
        output_message_2 = linux_cmd(
            hdd_test_compose(target_disk_device_name, "write_whole_disk")
        )
        output_message_3 = linux_cmd(
            hdd_test_compose(target_disk_device_name, "read_whole_disk")
        )
        output_message = output_message_1 + "\n" + output_message_2 + "\n" + output_message_3
    elif action_type == "mke2fs Disk":
        output_message = linux_cmd(
            hdd_test_compose(target_disk_device_name, "format_whole_disk")
        )
    elif action_type == "Read SMART info":
        output_message = linux_cmd(
            hdd_test_compose(target_disk_device_name, "smartctl")
        )
    elif action_type == "Read Disk Partition info":
        output_message = linux_cmd(
            hdd_test_compose(target_disk_device_name, "partition_info")
        )
    elif action_type == "Clean Disk Partition head":
        output_message = linux_cmd(
            hdd_test_compose(target_disk_device_name, "clean_disk_partition_head")
        )
    elif action_type == "Clean Disk Partition tail":
        output_message = linux_cmd(
            hdd_test_compose(target_disk_device_name, "clean_disk_partition_tail")
        )
    elif action_type == "Clean Disk Partition all":
        output_message = linux_cmd(
            hdd_test_compose(target_disk_device_name, "clean_disk_partition_head")
        )
        output_message = (
            output_message
            + " "
            + linux_cmd(
                hdd_test_compose(target_disk_device_name, "clean_disk_partition_tail")
            )
        )
    else:
        output_message = "No Action"

    print("output_message:", output_message)
    # wcheckbox.choice 是否打勾 checkbox 如果是 將 output_message 存到 log file
    if w_checkbox.choice:
        import datetime

        # today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        today = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        log_file_name = (
            disks_dict[target_disk_name.split(",")[0]]["model"].replace(" ", "_")
            + "-"
            + disks_dict[target_disk_name.split(",")[0]]["serial"].replace(" ", "_")
            + "-"
            + today
            + ".log"
        )
        with open(log_file_name, "a") as f:
            f.write(output_message)
    # print(output_message)
    # 以選的的硬碟 讀取 smartctl info
    # print("Result:", w_dropdown_target_disk.items[w_dropdown_target_disk.get()])
    # print(output_dict)
    # os.system("sudo dd of=/dev/null if=/dev/sda3 status=progress")
    # os.system("sudo smartctl -a /dev/sda")
    # os.system("sudo fdisk -l")
