#
# This example shows how to change the items of a ListBox widget
# when the current selection of a DropDown widget changes.
#
import picotui.screen as scn
import picotui.widgets as wgs

# from picotui.defs import C_B_WHITE, C_WHITE, C_B_BLUE, C_BLACK
import picotui.defs as defs


if __name__ == "__main__":
    s = scn.Screen()
    import os

    img_path = "./files/"
    img_list = os.listdir(img_path)

    # with open('testImagelist.txt', 'w') as f:
    #     for img_name in img_list:
    #         f.write(img_name + '\n')
    # Set the list of all available DropDown choices
    choices = img_list

    try:
        s.init_tty()
        # s.enable_mouse()
        s.attr_color(defs.C_WHITE, defs.C_BLACK)
        s.cls()
        s.attr_reset()
        d = wgs.Dialog(5, 5, 20, 12, "AI 備份檔設定工具")

        # DropDown and ListBox widgets
        d.add(1, 1, "選擇日期:")
        w_dropdown = wgs.WDropDown(15, ["All", "03", "04", "05"], dropdown_h=6)
        d.add(11, 1, w_dropdown)
        d.add(1, 2, "選擇主機:")
        w_dropdown_hosts = wgs.WDropDown(
            24,
            [
                "All",
                "CEDS",
                "CFS",
                "TIS",
                "SCADA DAC",
                "SCADA OIF",
                "Scenario Player(SCADA)",
                "TCS UC",
                "ADS",
                "TLMS",
                "TDRD",
                "Maintenance Workstation",
                "PMC (Main)",
                "PMC (Local)",
                "Interface Server",
            ],
            dropdown_h=6,
        )
        d.add(11, 2, w_dropdown_hosts)

        d.add(1, 3, "List:")
        w_listbox = wgs.WListBox(24, 8, choices)
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

        w_dropdown.on("changed", dropdown_changed)

        b = wgs.WButton(8, "OK")
        d.add(2, 10, b)
        b.finish_dialog = "ACTION_OK"
        b = wgs.WButton(8, "Cancel")
        d.add(12, 10, b)
        b.finish_dialog = "ACTION_CANCEL"

        res = d.loop()
    finally:
        s.goto(0, 50)
        s.cursor(True)
        s.disable_mouse()
        s.deinit_tty()

    print("Result:", w_listbox.get_cur_line())
