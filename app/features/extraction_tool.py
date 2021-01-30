from app.framework import Navi, mws
from app.util import system
import logging, time, pywinauto, copy, re

class ExtractionTool:
    IMPORT_OCR_REPLACE = { }
    EXPORT_OCR_REPLACE = { "Price Book": "FrICce BOOK" } # haha what
    DIR_LEVEL_OFFSET = 40
    DIR_WIN_BBOX = [241,253,634,592] if mws.is_high_resolution() else [135, 161, 530, 501]
    DIR_EXPAND_OFFSET = -50
    EXPORT_DATA_SELECT_ALL = "Select All"

    def __init__(self):
        self.log = logging.getLogger()
        ExtractionTool.navigate_to()

    @staticmethod
    def navigate_to():
        return Navi.navigate_to("Extraction Tool")

    def export_data(self, data, path, overwrite=True, timeout=300):
        """
        Export site settings to an XML file.
        Args:
            data: (dict) Which site settings to save. See example.
            path: (str) Where to save the file.
            overwrite: (bool) Whether to overwrite an existing XML if needed.
            timeout: (int) Maximum number of seconds to wait for the export to finish.
        Example:
            >>> data = { "Price Book": "Select All",
                       "Store": ["Store Options", "Accounting Options", "Security Groups"] }
            >>> ExtractionTool().export_data(data, "D:\ExtractionTool\SomePassportData.xml")
            True
            >>> ExtractionTool().export_data("Select All", "D:\ExtractionTool\AllPassportData.xml")
            True
        """
        mws.set_value("Export Data", True)
        mws.click_toolbar("Next")

        # Select data to export
        mws.search_click_ocr("Export Data") # Need a click in the window to dehighlight Price Book
        if data == ExtractionTool.EXPORT_DATA_SELECT_ALL:
            mws.click("Select All")
        else:
            for category, value in data.items():
                try:
                    category = ExtractionTool.EXPORT_OCR_REPLACE[category]
                except KeyError:
                    pass
                if value == "Select All": # All data in a category
                    if not self._search_click_with_scroll("Export Data List", category, bbox=ExtractionTool.DIR_WIN_BBOX):
                        mws.click_toolbar("Cancel", main=True)
                        return False
                else: # Selected data in a category
                    # Expand the category
                    if not self._search_click_with_scroll("Export Data List", category, bbox=ExtractionTool.DIR_WIN_BBOX, offset=(ExtractionTool.DIR_EXPAND_OFFSET, 0)):
                        mws.click_toolbar("Cancel", main=True)
                        return False
                    for setting in value: # Select data
                        try:
                            setting = ExtractionTool.EXPORT_OCR_REPLACE[setting]
                        except KeyError:
                            pass
                        if not self._search_click_with_scroll("Export directory", setting, bbox=ExtractionTool.DIR_WIN_BBOX):
                            mws.click_toolbar("Cancel", main=True)
                            return False
        mws.click_toolbar("Next")

        # Select path to export to
        self._select_treeview_file(path.split('\\')[:-1])
        # Calling set_text on this control crashes Passport for some reason
        mws.get_control("File").send_keystrokes("{DELETE}"*30+path.split('\\')[-1].replace('.xml', ''))

        # Run export process
        mws.click_toolbar("Start")
        if "already exists" in mws.get_top_bar_text():
            if overwrite:
                mws.click_toolbar("YES")
            else:
                self.log.warning(f"{path} already exists. Set overwrite to True if you want to replace it.")
                mws.click_toolbar("NO")
                mws.click_toolbar("Cancel", main=True)
                return False
        if not system.wait_for(lambda: ["Export process finished successfully"] in mws.get_value("Results"), timeout=timeout, verify=False):
            self.log.warning(f"Export did not complete within {timeout} seconds. Aborting.")
            mws.click_toolbar("Cancel")
            mws.click_toolbar("Exit", main=True)
            return False

        mws.click_toolbar("Exit", main=True)
        return True
    
    def import_data(self, path, timeout=300):
        """
        Import an extraction tool XML.
        Args:
            path: (str) File path for the XML to import. This function uses OCR, and it is not 100% accurate,
                  so you may have to slightly alter this string if the exact path doesn't work.
            timeout: (int) Maximum number of seconds to wait for the export to finish.
        Return: (bool) True/False for success/failure
        Example:
            >>> ExtractionTool().import_data(r"D:\ExtractionTool\PassportDataMaintenance.xml")
            True
        """
        bbox = ExtractionTool.DIR_WIN_BBOX.copy()
        mws.set_value("Import Data", True)
        mws.click_toolbar("Next")

        # Select the desired file
        mws.search_click_ocr("Import Data") # Need a click in the window to dehighlight C:
        path = path.replace(".xml", "")
        path_split = path.split("\\")
        for i in range(len(path_split)):
            try:
                dir = ExtractionTool.IMPORT_OCR_REPLACE[path_split[i]]
            except KeyError:
                dir = path_split[i]
            # Setting OCR clicks to 2 doesn't work here for some reason
            offset = (ExtractionTool.DIR_EXPAND_OFFSET, 0) if i < len(path_split)-1 else (0, 0)
            color = "6D6D6D" if i == 0 else "000000"
            if not self._search_click_with_scroll("Import directory", dir, color=color, offset=offset, click_loc=-1, bbox=bbox):
                self.log.warning("Couldn't navigate to the desired file.")
                mws.click_toolbar("Cancel")
                return False
            # bbox[0] += ExtractionTool.DIR_LEVEL_OFFSET
        src = mws.get_value("Source File")
        self.log.debug(f"Selected source file {src}.")
        mws.click_toolbar("Next")

        # Run import process
        try:
            mws.click_toolbar("Start", timeout=5)
        except mws.ConnException:
            self.log.warning(f"XML file is not valid. Passport error message: {mws.get_top_bar_text()}")
            mws.click_toolbar("Cancel", main=True)
            return False
        mws.click_toolbar("YES")
        if not system.wait_for(lambda: ["Import process finished successfully"] in mws.get_value("Results"), timeout=timeout, verify=False):
            self.log.warning(f"Import did not complete within {timeout} seconds. Aborting.")
            mws.click_toolbar("Cancel")
            mws.click_toolbar("Exit", main=True)
            return False

        mws.click_toolbar("Exit", main=True)
        return True

    @staticmethod
    def fix_version(path):
        """
        Rewrite the version number in an Extraction Tool XML to match the current system, eliminating version errors.
        Warning - Compatibility issues can result if there are major version differences. Use at your own risk.
        Args:
            path: (str) The path of the XML to change.
        Return: None
        Examples:
            >>> ExtractionTool.fix_version(r"D:\ExtractionTool\PassportDataMaintenance.xml")
        """
        version_pattern = "<Passport>\s*<Version>.*</Version>\s*</Passport>"
        replace_text = f"<Passport><Version>{system.get_version()}</Version></Passport>"
        with open(path, "r") as xml_file:
            lines = xml_file.read()
            lines = re.sub(version_pattern, replace_text, lines)
        with open(path, "w") as xml_file:
            xml_file.write(lines)

    def _search_click_with_scroll(self, control, *args, **kwargs):
        """Search and click wrapper that scrolls the control and tries again if it fails."""
        # Won't work if control is more than 2 "pages" long... find out how to check scroll position?
        if not mws.search_click_ocr(*args, **kwargs):
            mws.get_control(control).scroll("down", "end")
            if not mws.search_click_ocr(*args, **kwargs):
                return False
            mws.get_control(control).scroll("up", "end")
        return True

    def _select_treeview_file(self, path):
        bbox = ExtractionTool.DIR_WIN_BBOX.copy()
        for i in range(len(path)):
            try:
                dir = ExtractionTool.IMPORT_OCR_REPLACE[path[i]]
            except KeyError:
                dir = path[i]
            # Setting OCR clicks to 2 doesn't work here for some reason
            offset = (ExtractionTool.DIR_EXPAND_OFFSET, 0) if i < len(path)-1 else (0, 0)
            if not self._search_click_with_scroll(dir, color=["000000", "808080"], offset=offset, click_loc=-1, bbox=bbox):
                return False
            bbox[0] += ExtractionTool.DIR_LEVEL_OFFSET