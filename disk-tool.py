#
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

    output = subprocess.check_output(command, shell=True)
    return output.decode()


def linux_cmd_json_dict(command):
    import json

    output = linux_cmd(command)
    return json.loads(output)


def linux_all_disk_list():
    output = linux_cmd(hdd_test_cmd_disk_device_list).split("\n")
    print(output)
    return output


# print(linux_cmd("sudo fdisk -l"))
# print(linux_cmd_json_dict("sudo lshw -c disk -json"))
hdd_test_cmd_smartctl = "sudo smartctl -x /dev/cdrom -j"
hdd_test_cmd_partition_info = "sudo sgdisk -p /dev/sda"
hdd_test_cmd_clean_disk_partition_head = (
    "sudo dd if=/dev/zero of=/dev/sdc status=progress bs=512 count=34"
)
hdd_test_cmd_clean_disk_partition_tail = "sudo dd if=/dev/zero of=/dev/sdc bs=512 count=34 seek=$((`sudo /sbin/blockdev --getsz /dev/sdb` - 34))"
hdd_test_cmd_read_whole_disk = (
    "sudo dd if=/dev/sdc of=/dev/null status=progress bs=256M conv=sync,noerror"
)
hdd_test_cmd_write_whole_disk = (
    "sudo dd if=/dev/zero of=/dev/sdc status=progress bs=256M conv=sync,noerror"
)
hdd_test_cmd_disk_device_list = "sudo lshw -c disk -short -quiet |grep disk"
if __name__ == "__main__":
    import os

    s = scn.Screen()

    dev_disk = "/dev/"
    disk_list = []
    for file in os.listdir(dev_disk):
        if file.startswith("sd"):
            disk_list.append(file)

    choices = disk_list
    disks_info_dict = linux_cmd_json_dict("sudo lshw -c disk -json -quiet")
    disks_logicalname_dict = {}
    for i in disks_info_dict:
        print(i["product"], i["logicalname"], i["description"])
        if isinstance(i["logicalname"], list):
            disks_logicalname_dict[i["logicalname"][0]] = {
                "product": i["product"],
                "description": i["description"],
            }
        else:
            disks_logicalname_dict[i["logicalname"]] = {
                "product": i["product"],
                "description": i["description"],
            }
=======
    import subprocess
    import json

    s = scn.Screen()

    disks_dict = {}
    for i in linux_all_disk_list():
        single_disk_info = re.split(r"\s{2,}", i)
        if i:
            disks_dict[single_disk_info[3]] = single_disk_info[1]
>>>>>>> 4b20127412a3936c78e483345ee7196a214c6719

    print(disks_dict)
    # choices = disks_dict.items()
    choices = list(disks_dict.keys())
    try:
        s.init_tty()
        s.enable_mouse()
        s.attr_color(defs.C_WHITE, defs.C_BLACK)
        s.cls()
        s.attr_reset()
        d = wgs.Dialog(5, 5, 20, 12, "芙奕達硬碟檢測工具")

        # DropDown and ListBox widgets
        d.add(1, 1, "選擇硬碟:")
        w_dropdown_target_disk = wgs.WDropDown(
<<<<<<< HEAD
            15, ["All"] + list(disks_logicalname_dict.keys()), dropdown_h=6
=======
            15, ["All"] + list(disks_dict.items()), dropdown_h=6
>>>>>>> 4b20127412a3936c78e483345ee7196a214c6719
        )
        d.add(11, 1, w_dropdown_target_disk)

        d.add(1, 3, "List:")
        w_listbox = wgs.WListBox(24, 6, choices)
        d.add(1, 4, w_listbox)

        # Filter the ListBox based on the DropDown selection
        def dropdown_changed(w):
            new_choices = []
            for i in range(len(choices)):
                if w.items[w.choice] == "All" or w.items[w.choice] in choices[i]:
                    new_choices.append(choices[i])

            # As we're going to set completely new items, reset current/top item of the widget
            w_listbox.top_line = 0
            w_listbox.cur_line = 0
            w_listbox.row = 0
            w_listbox.set_items(new_choices)

        w_dropdown_target_disk.on("changed", dropdown_changed)

        d.add(1, 10, "選擇檢測:")
        w_dropdown_test_type = wgs.WDropDown(
            24,
            [
                "Read All Disk",
                "Write All Disk",
                "mke2fs Disk",
                "Read SMART info",
            ],
            dropdown_h=6,
        )

        d.add(11, 10, w_dropdown_test_type)
        b = wgs.WButton(8, "OK")
        d.add(2, 12, b)
        b.finish_dialog = "ACTION_OK"
        b = wgs.WButton(8, "Cancel")
        d.add(12, 12, b)
        b.finish_dialog = "ACTION_CANCEL"

        res = d.loop()
    finally:
        s.goto(0, 50)
        s.cursor(True)
        s.disable_mouse()
        s.deinit_tty()

    print("Result:", w_listbox.get_cur_line())
    print("Result:", w_dropdown_target_disk.items[w_dropdown_target_disk.get()])
    # print(output_dict)
    # os.system("sudo dd of=/dev/null if=/dev/sda3 status=progress")
    # os.system("sudo smartctl -a /dev/sda")
    # os.system("sudo fdisk -l")
