""" Script for DWGExportByFileList
"""

# pylint: disable=consider-using-with

from __future__ import annotations

from typing import TYPE_CHECKING, List, Any, cast

import fileinput
import os
import sys
import xml.etree.ElementTree as ET

import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_IFW_Input as AllplanIFW
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_Utility as AllplanUtil
import NemAll_Python_AllplanSettings as AllplanSettings

from BuildingElement import BuildingElement
from BuildingElementComposite import BuildingElementComposite
from BuildingElementControlProperties import BuildingElementControlProperties
from BuildingElementPaletteService import BuildingElementPaletteService
from CreateElementResult import CreateElementResult
from StringTableService import StringTableService
from Utils.TabularDataUtil import read_csv

if TYPE_CHECKING:
    from __BuildingElementStubFiles.DWGExportByFileListBuildingElement import DWGExportByFileListBuildingElement
else:
    DWGExportByFileListBuildingElement = BuildingElement

print('Load DWGExportByFileList.py')


def check_allplan_version(_build_ele: BuildingElement,
                          _version  : type) -> bool:
    """ Check the current Allplan version

    Args:
        _build_ele: building element with the parameter properties
        _version  : the current Allplan version

    Returns:
        True
    """

    # Support all versions
    return True


def create_element(_build_ele: BuildingElement,
                   _doc      : AllplanEleAdapter.DocumentAdapter) -> CreateElementResult:
    """ Creation of element (only necessary for the library preview)

    Args:
        _build_ele: building element with the parameter properties
        _doc:       document of the Allplan drawing files

    Returns:
        created element result
    """

    return CreateElementResult()


def create_interactor(coord_input              : AllplanIFW.CoordinateInput,
                      _pyp_path                : str,
                      _global_str_table_service: StringTableService,
                      build_ele_list           : List[BuildingElement],
                      build_ele_composite      : BuildingElementComposite,
                      build_ele_ctrl_props_list: List[BuildingElementControlProperties],
                      _modify_uuid_list        : List[str]) -> object:
    """ Create the interactor

    Args:
        coord_input              : API object for the coordinate input, element selection, ... in the Allplan view
        _pyp_path                : path of the pyp file
        _global_str_table_service: global string table service
        build_ele_list           : list with the building elements
        build_ele_composite      : building element composite with the building element constraints
        build_ele_ctrl_props_list: list with the building element control properties
        _modify_uuid_list        : list with the UUIDs of the modified elements

    Returns:
        created interactor
    """

    return DWGExportByFileList(coord_input, build_ele_list, build_ele_composite,  build_ele_ctrl_props_list)


class DWGExportByFileList():
    """ Definition of class DWGExportByFileList
    """

    def __init__(self,
                 coord_input              : AllplanIFW.CoordinateInput,
                 build_ele_list           : List[BuildingElement],
                 build_ele_composite      : BuildingElementComposite,
                 build_ele_ctrl_props_list: List[BuildingElementControlProperties]):
        """ Initialization of class DWGExportByFileList

        Args:
            coord_input              : API object for the coordinate input, element selection, ... in the Allplan view
            build_ele_list           : list with the building elements
            build_ele_composite      : building element composite with the building element constraints
            build_ele_ctrl_props_list: list with the building element control properties
        """

        self.coord_input               = coord_input
        self.build_ele_list            = build_ele_list
        self.build_ele_composite       = build_ele_composite
        self.build_ele_ctrl_props_list = build_ele_ctrl_props_list
        self.build_ele                 = cast(DWGExportByFileListBuildingElement, build_ele_list[0])

        self.palette_service = BuildingElementPaletteService(self.build_ele_list, self.build_ele_composite,
                                                             "DWGExportByFileList",
                                                             self.build_ele_ctrl_props_list, "")

        self.settings_path = AllplanSettings.AllplanPaths.GetStdPath() + "DWGExport\\"

        self.build_ele.CvsFile.value = self.settings_path + "DWGExport.csv"

        if len(sys.argv) > 1:
            self.build_ele.CvsFile.value = sys.argv[1]
            self.settings_path = os.path.dirname(sys.argv[1]) + "\\"

        self.build_ele_ctrl_props_list[0][1].text = self.build_ele.CvsFile.value

        self.palette_service.show_palette("")


        #----------------- get the properties and start the input

        if not sys.argv or sys.argv == ['']:
            self.coord_input.InitFirstElementInput(AllplanIFW.InputStringConvert("Execute by button click"))

            return

        self.export()

        AllplanBaseElements.ProjectService.CloseAllplan()


    def modify_element_property(self, page: int, name: str, value: Any):
        """ Modify property of element

        Args:
            page : page index of the modified property
            name : name of the modified property
            value: new value
        """

        self.palette_service.modify_element_property(page, name, value)

        self.settings_path = os.path.dirname(self.build_ele.CvsFile.value) + "\\"


    def on_cancel_function(self) -> bool:
        """ Check for input function cancel in case of ESC

        Returns:
            True
        """

        self.palette_service.close_palette()

        return True


    def on_preview_draw(self):
        """ Handles the preview draw event
        """


    def on_mouse_leave(self):
        """ Handles the mouse leave event
        """


    def on_control_event(self,
                         _event_id: int):
        """ On control event

        Args:
            _event_id: event id of the clicked button control
        """

        self.export()

    @staticmethod
    def read_dfselection_file(path: str) -> List[int]:
        """Read file names from df selection file 

        Args:
            path: path to xml file

        Returns:
            List[int]: returns a list of file numbers, typed as int
        """
        root             = ET.parse(path).getroot()
        xpath_teilbild   = ".//Teilbild"
        xpath_window_xml = ".//File[@Activated='1']"
        NODE_ID          = "NodeID"
        ID               = "ID"

        nodes_teilbild = [int(node.attrib["NodeID"])
                          for node in root.findall(xpath_teilbild) if NODE_ID in node.attrib]
        nodes_windows_xml = [int(node.attrib["ID"])
                             for node in root.findall(xpath_window_xml)
                                if ID in node.attrib and node.attrib["State"] in {"2", "3"}]

        return [*nodes_teilbild, *nodes_windows_xml]

    @staticmethod
    def read_settings(path              : str,
                      setting_file      : str,
                      default_file      : str,
                      folder_name       : str) -> str:
        """ Read settings from setting files

        Args:
            path        : Path to setting file
            setting_file: Default setting file
            default_file: Path to default file if no settings exists
            folder_name : Name of the folder in file system
        Return:
            type(str)   : settings from xml file  
        """
        if setting_file:
            setting_file = path + f"{folder_name}\\" + setting_file
        return setting_file if setting_file else default_file

    @staticmethod
    def update_nth_files(path: str,
                         cfg_file_path: str,
                         revert: dict):
        """Update nth file to add valid config path

        Args:
            path         : Path to nth file
            cfg_file_path: Path of cfg file
            revert       : A dictionary to hold original lines
        """
        config  = "AOConfigfile"
        for line in fileinput.input(path, inplace=True):
            if config in line:
                revert[path] = line
                print(f'"{config}="string:"{cfg_file_path}"\n', end='')
            else:
                print(line, end='')

    @staticmethod
    def revert_nth_file(path: str,
                        original_line: str):
        """Revert .nth file content back to original state

        Args:
            path : Path to .nth file
            original_line : Original line
        """
        config = "AOConfigfile"
        for line in fileinput.input(path, inplace=True):
            if config in line:
                print(f"{original_line}\n", end='')
            else:
                print(line, end='')

    def export(self):
        """ export the data
        """

        host_name_list      = []
        project_name_list   = []
        file_number_list    = []
        layer_favorite_list = []
        dwg_favorite_list   = []
        version_list        = []
        output_path_list    = []
        output_file_list    = []
        config_file_list    = []
        revert              = {}


        #----------------- check for existing file

        path = self.settings_path

        if not os.path.isfile(self.build_ele.CvsFile.value):
            AllplanUtil.ShowMessageBox("Datei " + self.build_ele.CvsFile.value + " ist nicht vorhanden", AllplanUtil.MB_OK)
            return

        save_layer_file_name = AllplanSettings.AllplanPaths.GetUsrPath() + "tmp\\CurrentLayerState.lfa"


        #----------------- read the data

        data_frame = read_csv(self.build_ele.CvsFile.value)

        log_file = open(path + "DWGExport.log", "w", encoding="UTF-8")

        for entry in data_frame:
            drawing_file = path + "dfSettings\\" + cast(str, entry["dfSelection"])

            try:
                file_numbers = DWGExportByFileList.read_dfselection_file(drawing_file)
                file_number_list.append(file_numbers)

                layer_favorite_list.append(DWGExportByFileList.read_settings(
                    path, entry["layerSetting"], save_layer_file_name, "layerSettings"))

                version_list.append(int(entry["version"]))

                # if (dwg_favorite_file := cast(str, entry["dwgSettings"])):
                #     dwg_favorite_file = path + "dwgSettings\\" + dwg_favorite_file
                dwg_favorite_file = DWGExportByFileList.read_settings(path,entry["dwgSetting"], "", "dwgSettings")
                cfg_file = DWGExportByFileList.read_settings(path,entry["cfgSetting"], "",  "cfgSettings")
                if cfg_file:
                    DWGExportByFileList.update_nth_files(dwg_favorite_file, cfg_file, revert)
                config_file_list.append(cfg_file)
                dwg_favorite_list.append(dwg_favorite_file)

                output_path_list.append(entry["destinationFolder"])
                output_file_list.append(entry["filename"])
                host_name_list.append(entry["hostName"])
                project_name_list.append(entry["projectName"])

            except FileNotFoundError:
                log_file.write("\n")
                log_file.write("File " + drawing_file + " not found !!!\n")
                log_file.write("\n")


        #----------------- save the current project, file and layer state

        current_project_name, current_host_name = AllplanBaseElements.ProjectService.GetCurrentProjectNameAndHost()

        drawing_file_serv = AllplanBaseElements.DrawingFileService()

        current_file_list = drawing_file_serv.GetFileState()

        doc = self.coord_input.GetInputViewDocument()

        layer_path = AllplanSettings.AllplanPaths.GetUsrPath() + "tmp"

        if not os.path.exists(layer_path):
            os.makedirs(layer_path)

        if not AllplanBaseElements.LayerService.SaveToFavoriteFile(doc, save_layer_file_name):
            AllplanUtil.ShowMessageBox("Not possible to save the current layer state", AllplanUtil.MB_OK)
            return


        #----------------- execute the export -------------------------------------------------------------------------


        usr_path = AllplanSettings.AllplanPaths.GetUsrPath()
        std_path = AllplanSettings.AllplanPaths.GetStdPath()
        prj_path = AllplanSettings.AllplanPaths.GetCurPrjPath()

        def get_final_path(path: str) -> str:
            """ get the final path

            Args:
                path: path

            Returns:
                final path
            """
            return path.replace("$usr$", usr_path).replace("$std$", std_path).replace("$prj$", prj_path).rstrip("\n")

        progress_bar = AllplanUtil.ProgressBar()
        progress_bar.StartProgressbar(len(file_number_list),"DWG Batch Export", "", True)

        progress_bar.MakeStep(1)

        for index, (host_name, project_name, file_numbers, layer_favorite_file, dwg_favorite_file, config_file, version) in \
                enumerate(zip(host_name_list, project_name_list, file_number_list, layer_favorite_list, dwg_favorite_list,
                              config_file_list, version_list)):
            self.check_structure_settings(host_name, project_name)

            result = AllplanBaseElements.ProjectService.OpenProject(self.coord_input.GetInputViewDocument(),
                                                                    host_name, project_name)

            if result == "Project not exist":
                AllplanUtil.ShowMessageBox("Project " + project_name + "(" + host_name + ") doesn't exist", AllplanUtil.MB_OK)
                continue

            if result == "Not possible to open the project":
                AllplanUtil.ShowMessageBox("Not possible to open the project " + project_name + "(" + host_name + ")", AllplanUtil.MB_OK)
                continue

            if result != "Active project":
                AllplanBaseElements.DrawingService.RedrawAll(self.coord_input.GetInputViewDocument())


            #---------------- load the drawing files

            drawing_file_serv.UnloadAll(doc)

            drawing_file_serv.LoadFile(doc, file_numbers[0], AllplanBaseElements.DrawingFileLoadState.ActiveForeground)

            for file_number in file_numbers[1:]:
                drawing_file_serv.LoadFile(doc, file_number, AllplanBaseElements.DrawingFileLoadState.ActiveBackground)

            #---------------- load the layer settings and draw all

            if not AllplanBaseElements.LayerService.LoadFromFavoriteFile(doc, layer_favorite_file):
                AllplanUtil.ShowMessageBox("Loading for layer favorite not possible: " + "\n\n" + layer_favorite_file, AllplanUtil.MB_OK)
                continue

            AllplanBaseElements.DrawingService.RedrawAll(self.coord_input.GetInputViewDocument())


            #---------------- export to DWG

            export_path = get_final_path(output_path_list[index])

            if not os.path.exists(export_path):
                os.makedirs(export_path)

            export_file_name = export_path + "\\" + output_file_list[index]

            try:
                os.remove(export_file_name)

            except OSError:
                pass

            log_file.write("-------------------------------------------------------------\n")
            log_file.write("Export files:   " + str(file_numbers) + "\n")
            log_file.write("Layer favorite: " + layer_favorite_file + "\n")
            log_file.write("DWG favorite:   " + dwg_favorite_file + "\n")
            log_file.write("DWG favorite:   " + config_file + "\n")
            log_file.write("export_file:    " + export_file_name + "\n")

            drawing_file_serv.ExportDWGByTheme(doc, export_file_name, dwg_favorite_file, version)

            progress_bar.MakeStep(1)


        #----------------- reset the current drawing file and layer state

        log_file.close()

        AllplanBaseElements.ProjectService.OpenProject(self.coord_input.GetInputViewDocument(),
                                                       current_project_name, current_host_name)

        drawing_state_dict = {1 : AllplanBaseElements.DrawingFileLoadState.PassiveBackground,
                              2 : AllplanBaseElements.DrawingFileLoadState.ActiveBackground,
                              3 : AllplanBaseElements.DrawingFileLoadState.ActiveForeground}

        for number, state in current_file_list:
            drawing_file_serv.LoadFile(doc, number, drawing_state_dict[state])

        if not AllplanBaseElements.LayerService.LoadFromFavoriteFile(doc, save_layer_file_name):
            AllplanUtil.ShowMessageBox("Not possible to load the current layer state", AllplanUtil.MB_OK)
            return

        for path, line in revert.items():
            DWGExportByFileList.revert_nth_file(path,line)

    def process_mouse_msg(self,
                          _mouse_msg: int,
                          _pnt      : AllplanGeo.Point2D,
                          _msg_info : AllplanIFW.AddMsgInfo) -> bool:
        """ Process the mouse message event

        Args:
            _mouse_msg: mouse message ID
            _pnt:       input point in Allplan view coordinates
            _msg_info:  additional mouse message info

        Returns:
            True
        """

        return True


    def check_structure_settings(self,
                                 host_name   : str,
                                 project_name: str):
        """ create the file with the structure settings

        Args:
            host_name:    host name
            project_name: project name
        """

        error, path = AllplanBaseElements.ProjectService.GetProjectPath(host_name, project_name)

        if error:
            return

        path += "\\BIM\\" + AllplanBaseElements.ProjectService.GetCurrentUserAsBwsPath() + "\\settings"

        settings_file = path + "\\Structure_settings.xml"

        if os.path.exists(settings_file):
            return

        if not os.path.exists(path):
            os.makedirs(path)

        with open(settings_file, "w", encoding = "UTF-8") as file:
            file.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
                       "<NemetschekBIMStructureSettings Activated=\"1\">\n"
                       "<Files>\n"
                       "    <File ID=\"0001\" State=\"3\" Activated=\"1\" />\n"
                       "</Files>\n"
                       "</NemetschekBIMStructureSettings>")
