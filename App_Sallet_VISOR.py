"""Sallet univers' VISOR app.
by Sziller"""

import os
import sys
import dotenv
import inspect
import cv2
from kivy.app import App  # necessary for the App class
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.image import AsyncImage
from pyzbar import pyzbar
from kivy.graphics.texture import Texture

from SalletBasePackage.WidgetClasses import *
from SalletBasePackage import SQL_interface as sql, models
from SalletBasePackage import units
from SalletNodePackage import NodeManager as NodeMan
from SalletVisorPackage import UtxoManager as UtxoMan

from kivy.config import Config

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

WELCOME_TITLE       = "Welcome to Sallet - protecting your assets!"
WELCOME_TXT         = ("This is the Visor module of the Sallet Universe: "
                       "The outside-world-facing Secure Wallet application. \n"
                       "The Sallet system was built with security in focus. "
                       "When planing security we at sziller.eu hope for the"
                       "best and plan for the worst."
                       "A flexible, low-level transaction-, utxo- and key-manager application for users "
                       "somewhat familiar with the nitty-gritties of Bitcoin.\n"
                       "Transactions created in Sallet-VISOR are be signed off-line, using the Sallet-HEAD module. "
                       "Communication between VISOR and HEAD is conducted using QR codes, providing an analogue"
                       " air-gap between"
                       "the digital word and your sensitive data\n")
FEATURE_SET         = ("- Manage and select your own UTXO's\n"
                       "- Generate and keep your Keys off-line\n"
                       "- Sign your transactions off-line\n"
                       "- Isolate sensitive data from the digital world\n"
                       "- Issuance and manage your own tokens on Bitcoin"
                       "- Customize the way you publish your transaction")
FEATURE_ALIASES     = ("- Coin selection\n"
                       "- No digital footprint\n"
                       "- Hidden entropy\n"
                       "- Privacy\n"
                       "- Asset management\n"
                       "- Node selection")


class SalletScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super(SalletScreenManager, self).__init__(**kwargs)
        self.statedict = {
            "screen_intro": {
                "seq": 0,
                'inst': "button_nav_intro",
                'down': ["button_nav_intro"],
                'normal': ["button_nav_btc", "button_nav_nft", "button_nav_tx",
                           "button_nav_qr_out", "button_nav_qr_in", "button_nav_send"]},
            "screen_btc": {
                "seq": 1,
                'inst': 'button_nav_btc',
                'down': ['button_nav_btc'],
                'normal': ["button_nav_intro", "button_nav_nft", "button_nav_tx",
                           "button_nav_qr_out", "button_nav_qr_in", "button_nav_send"]},
            "screen_nft": {
                "seq": 2,
                'inst': 'button_nav_nft',
                'down': ['button_nav_nft'],
                'normal': ["button_nav_intro", "button_nav_btc", "button_nav_tx",
                           "button_nav_qr_out", "button_nav_qr_in", "button_nav_send"]},
            "screen_tx":  {
                "seq": 3,
                'inst': 'button_nav_tx',
                'down': ['button_nav_tx'],
                'normal': ["button_nav_intro", "button_nav_btc", "button_nav_nft",
                           "button_nav_qr_out", "button_nav_qr_in", "button_nav_send"]},
            "screen_qr_out": {
                "seq": 4,
                'inst': 'button_nav_qr_out',
                'down': ['button_nav_qr_out'],
                'normal': ["button_nav_intro", "button_nav_btc", "button_nav_nft",
                           "button_nav_tx", "button_nav_qr_in", "button_nav_send"]},
            "screen_qr_in": {
                "seq": 5,
                'inst': 'button_nav_qr_in',
                'down': ['button_nav_qr_in'],
                'normal': ["button_nav_intro", "button_nav_btc", "button_nav_nft",
                           "button_nav_tx", "button_nav_qr_out", "button_nav_send"]},
            "screen_send": {
                "seq": 6,
                'inst': "button_nav_send",
                'down': ["button_nav_send"],
                'normal': ["button_nav_intro", "button_nav_btc", "button_nav_nft",
                           "button_nav_tx", "button_nav_qr_out", "button_nav_qr_in"]}
            }


class NavBar(BoxLayout):
    """=== Class name: NavBar ==========================================================================================
    This Layout can be used across all screens. Class handles complications of now yet drawn instances.
    It sets appearance for instances only appearing on screen.
    ============================================================================================== by Sziller ==="""

    @ staticmethod
    def on_release_navbar(inst):
        """=== Method name: on_toggle_navbar ===========================================================================
        Method manages multiple screen selection by Toggle button set.
        All Toggle Buttons call this same function. Their Class names are stored in the <buttons> list.
        Only one button of the entire set is down at a given time. Function is extendable.
        Once a given button is 'down', it becomes inactive, all other buttons are activated and set to "normal" state.
        The reason of the logic is as follows:
        Screen manager is the unit taking care of actual screen swaps, also it stores actually shown screen name.
        However, at the itme of instantiation of the Screen Manager's ids are still not accessible.
        So we refer to ScreenManager's id's only on user action.
        :var inst: - the instance (button) activating the Method.
        ========================================================================================== by Sziller ==="""
        # Retrieve the sequence number of the currently shown screen
        old_seq: int = 0
        for k, v in App.get_running_app().root.statedict.items():
            if k == App.get_running_app().root.current_screen.name:
                old_seq = v["seq"]
                break
        # Identify the sequence number of the target screen
        new_seq = App.get_running_app().root.statedict[inst.target]["seq"]

        # Change the screen based on the direction of the sequence change
        App.get_running_app().change_screen(screen_name=inst.target,
                                            screen_direction={True: "left", False: "right"}[old_seq - new_seq < 0])
        # Update button appearances based on the target screen's states
        for buttinst in App.get_running_app().root.current_screen.ids.navbar.ids:
            # Deactivate buttons linked to the target screen
            if buttinst in App.get_running_app().root.statedict[inst.target]['down']:
                App.get_running_app().root.current_screen.ids.navbar.ids[buttinst].disabled = True
                App.get_running_app().root.current_screen.ids.navbar.ids[buttinst].state = "normal"
            # Activate buttons not linked to the target screen
            if buttinst in App.get_running_app().root.statedict[inst.target]['normal']:
                App.get_running_app().root.current_screen.ids.navbar.ids[buttinst].disabled = False
                App.get_running_app().root.current_screen.ids.navbar.ids[buttinst].state = "normal"


class OpAreaIntro(OperationAreaBox):
    ccn = inspect.currentframe().f_code.co_name
    
    def __init__(self, **kwargs):
        super(OpAreaIntro, self).__init__(**kwargs)

    def on_init(self):
        """=== Method name: on_init ====================================================================================
        Default method to run right after startup (or whenever defaulting back to initial state is necessary)
        ========================================================================================== by Sziller ==="""
        print("Started: {}".format(self.ccn))


class QRdisplay(BoxLayout):
    ccn = inspect.currentframe().f_code.co_name
    qr_list = os.listdir("./qrcodes")
    qr_counter = 0
    
    def on_init(self):
        """=== Method name: on_init ====================================================================================
        Default method to run right after startup (or whenever defaulting back to initial state is necessary)
        ========================================================================================== by Sziller ==="""
        print("Started: {}".format(self.ccn))

    def on_buttonclick_qr_browse(self, inst):
        """=== Method name: on_buttonclick_qr_browse ===================================================================
        ========================================================================================== by Sziller ==="""
        print("Pushed from QRdisplay")
        self.qr_counter += inst.add
        if self.qr_counter >= len(self.qr_list): self.qr_counter = 0
        if self.qr_counter < 0: self.qr_counter = len(self.qr_list) - 1
        self.ids.qr_count.text = str(self.qr_counter)
        self.ids.qr_plot_layout.remove_widget(self.ids.qr_plot_layout.displayed_qr)
        passed = AsyncImage(source="./qrcodes/" + self.qr_list[self.qr_counter])
        self.ids.qr_plot_layout.swap_displayed_qr_widget(received=passed)
        
        
class QRPlotField(BoxLayout):
    def __init__(self, **kwargs):
        super(QRPlotField, self).__init__(**kwargs)
        self.displayed_qr = Label(text="Images will be displayed here")
        self.add_widget(self.displayed_qr)

    def swap_displayed_qr_widget(self, received):
        """=== Method name: swap_displayed_qr_widget ===================================================================
        ========================================================================================== by Sziller ==="""
        print("Pushed from QRPlotLayout")
        self.remove_widget(self.displayed_qr)
        self.displayed_qr = received
        self.add_widget(self.displayed_qr)


class ScanArea(BoxLayout):
    def __init__(self, **kwargs):
        super(ScanArea, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.cam = cv2.VideoCapture(0)
        self.cam.set(3, 1920)
        self.cam.set(4, 1080)

        self.fps = 60
        self.schedule = None
        self.collected_strings = []

    def start_scanning(self):
        """=== Method name: start_scanning =============================================================================
        ========================================================================================== by Sziller ==="""
        self.schedule = Clock.schedule_interval(self.update, 1.0 / self.fps)

    def stop_scanning(self):
        """=== Method name: stop_scanning ==============================================================================
        ========================================================================================== by Sziller ==="""
        self.schedule.cancel()
        for _ in self.collected_strings:
            print(_)

    def update(self, dt):
        """=== Method name: update =====================================================================================
        ========================================================================================== by Sziller ==="""
        if True:
            ret, frame = self.cam.read()
            if ret:
                buf1 = cv2.flip(frame, 0)
                buf = buf1.tobytes()
                image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
                image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

                self.ids.img.texture = image_texture

                barcodes = pyzbar.decode(frame)

                if not barcodes:
                    scan_img = cv2.putText(frame, 'Scanning', (50, 75), cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 255, 255), 2)
                    scan_buf = cv2.flip(scan_img, 0)
                    scan_buf = scan_buf.tobytes()
                    scan_texture = Texture.create(size=(scan_img.shape[1], scan_img.shape[0]), colorfmt='bgr')
                    scan_texture.blit_buffer(scan_buf, colorfmt='bgr', bufferfmt='ubyte')

                    self.ids.img.texture = scan_texture

                else:
                    for barcode in barcodes:
                        (x, y, w, h) = barcode.rect
                        rectangle_img = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 7)
                        rectangle_buf = cv2.flip(rectangle_img, 0)
                        rectangle_buf = rectangle_buf.tobytes()
                        rectangle_texture = Texture.create(size=(rectangle_img.shape[1], rectangle_img.shape[0]),
                                                           colorfmt='bgr')
                        rectangle_texture.blit_buffer(rectangle_buf, colorfmt='bgr', bufferfmt='ubyte')

                        self.ids.img.texture = rectangle_texture

                        actual_text = str(barcode.data.decode("utf-8"))
                        print(actual_text)
                        if actual_text not in self.collected_strings:
                            self.collected_strings.append(actual_text)


class OpAreaQrIn(OperationAreaBox):
    ccn = inspect.currentframe().f_code.co_name
    
    def __init__(self, **kwargs):
        super(OpAreaQrIn, self).__init__(**kwargs)
    
    def on_init(self):
        """=== Method name: on_init ====================================================================================
        Default method to run right after startup (or whenever defaulting back to initial state is necessary)
        ========================================================================================== by Sziller ==="""
        print("Started: {}".format(self.ccn))
        
    def on_toggle_scan_qr(self, inst):
        """=== Method name: on_toggle_scan_qr ==========================================================================
        ========================================================================================== by Sziller ==="""
        
        if inst.state == "normal":
            self.ids.scan_area.stop_scanning()
            inst.text = "scanning stopped"
            self.ids.scan_area.ids.img.texture = None
            self.ids.scan_area.ids.img.reload()
        else:
            self.ids.scan_area.start_scanning()
            inst.text = "now scanning..."
        print("toggled camera on/off")


class OpAreaBtc (OperationAreaBox):
    ccn = inspect.currentframe().f_code.co_name
    
    def __init__(self, **kwargs):
        super(OpAreaBtc, self).__init__(**kwargs)
    
    def on_init(self):
        """=== Method name: on_init ====================================================================================
        Default method to run right after startup (or whenever defaulting back to initial state is necessary)
        ========================================================================================== by Sziller ==="""
        print("Started: {}".format(self.ccn))
        
        
class OpAreaNft (OperationAreaBox):
    ccn = inspect.currentframe().f_code.co_name
    
    def __init__(self, **kwargs):
        super(OpAreaNft, self).__init__(**kwargs)
        
    def on_init(self):
        """=== Method name: on_init ====================================================================================
        Default method to run right after startup (or whenever defaulting back to initial state is necessary)
        ========================================================================================== by Sziller ==="""
        print("Started: {}".format(self.ccn))
        
        
class OpAreaSend(OperationAreaBox):
    ccn = inspect.currentframe().f_code.co_name
    
    def __init__(self, **kwargs):
        super(OpAreaSend, self).__init__(**kwargs)
        self.nodemanager: NodeMan.NODEManager or None   = None
        self.node_rowobj_dict_in_opareasend: dict = {}
        self.used_node: models.Node or None = None
        
    def on_init(self):
        """=== Method name: on_init ====================================================================================
        Default method to run right after startup (or whenever defaulting back to initial state is necessary)
        ========================================================================================== by Sziller ==="""
        self.nodemanager = NodeMan.NODEManager(session_in=App.get_running_app().db_session, dotenv_path="./.env")
        self.display_node_rowobj_list()
    
    def on_btn_release_broadcast(self):
        """=== Method name: on_btn_release_broadcast ===================================================================
        actions taken when button pushed.
        ========================================================================================== by Sziller ==="""
        print("PUSHED: on_btn_release_broadcast - says: {}".format(self.ccn))
    
    def on_btn_release_cancel(self):
        """=== Method name: on_btn_release_cancel ======================================================================
        actions taken when button pushed.
        ========================================================================================== by Sziller ==="""
        print("PUSHED: on_btn_release_cancel - says: {}".format(self.ccn))
    
    # def display_node_data(self):
    #     """=== Method name: display_node_data ========================================================================
    #     Method updates Utxo balance Label in current Object instance of OpAreaTx(OperationAreaBox)
    #     ========================================================================================== by Sziller ==="""
    #     self.ids.lbl_node_data.text = str(self.nodemanager.node_list)
    
    def display_node_rowobj_list(self):
        """=== Method name: add_new_node_rowobj ========================================================================
        Method checks number of outputs, and adds a new OutputRowObj to the output_display_area.
        It also updates any fields update logically affects.
        ========================================================================================== by Sziller ==="""
        for alias, node_rowobj in self.nodemanager.node_obj_dict.items():
            print(node_rowobj)
            newline = NodeRowObj(parent_op_area=self, node_obj=node_rowobj)
            self.ids.node_display_area.add_widget(newline)  # only add if key does not exist!!!
            self.node_rowobj_dict_in_opareasend[alias] = newline
        
    def use_node(self, node: models.Node):
        """=== Method name: use_node ===================================================================================
        ========================================================================================== by Sziller ==="""
        print(node)
        used_alias = node.alias
        for alias, node_rowobj in self.node_rowobj_dict_in_opareasend.items():
            if alias is not used_alias:
                node_rowobj.disabled = False
        self.ids.used_node_data.node_alias = node.alias
        self.ids.used_node_data.node_address = node.ip + ":" + str(node.port)
        
        
class OpAreaTx(OperationAreaBox):
    ccn = inspect.currentframe().f_code.co_name

    def __init__(self, **kwargs):
        super(OpAreaTx, self).__init__(**kwargs)
        self.utxo_set_in_opareatx: dict                 = {}    #
        self.input_set_in_opareatx: dict                = {}    #
        self.output_rowobj_list_in_opareatx: list       = []    #
        self.selected_input_list: list                  = []    #
        self.utxomanager: UtxoMan.UTXOManager or None   = None  #
        # --- Balance components --------------------------------------------   Balance components  -   START   -
        self.actual_total_input = 0
        self.actual_total_output = 0
        self.actual_fee = 0
        # --- Balance components --------------------------------------------   Balance components  -   ENDED   -
        # self.on_init()
    
    def on_init(self):
        """=== Method name: on_init ====================================================================================
        Default method to run right after startup (or whenever defaulting back to initial state is necessary)
        ========================================================================================== by Sziller ==="""
        self.utxomanager = UtxoMan.UTXOManager(session_in=App.get_running_app().db_session, dotenv_path="./.env")
        self.update_utxo_set()  # needs to be checked for duplicates, must eventually delete old entries also!
        self.update_total_input()  # calculate input side full balance from actual inputs
        # needs to delete all outputs before adding new single one if RESET is used, also:
        # self.output_rowobj_list_in_opareatx = []
        self.add_new_output_rowobj()
        self.update_total_output()
        self.update_fee()
        self.display_all()
        
        App.get_running_app().root.ids.screen_btc.ids.oparea_btc.ids.lbl_balance_btc.text =\
            str(self.utxomanager.balance_total)
    
    def create_tx(self):
        """=== Method name: create_tx ==================================================================================
        ========================================================================================== by Sziller ==="""
        print("PUSHED: <create_tx>")
    
    def add_new_output_rowobj(self):
        """=== Method name: add_new_output_rowobj ======================================================================
        Method checks number of outputs, and adds a new OutputRowObj to the output_display_area.
        It also updates any fields update logically affects.
        ========================================================================================== by Sziller ==="""
        n = len(self.output_rowobj_list_in_opareatx)
        newline = OutputRowObj(n=n, parent_op_area=self)
        self.ids.output_display_area.add_widget(newline)  # only add if key does not exist!!!
        self.output_rowobj_list_in_opareatx.append(newline)
        self.update_total_output()
        self.display_total_output()
        self.update_fee()
        self.display_fee()
    
    def update_fee(self):
        """=== Method name: ============================================================================
        ========================================================================================== by Sziller ==="""
        self.actual_fee = self.actual_total_input - self.actual_total_output
    
    def update_total_output(self):
        """=== Method name: ============================================================================
        ========================================================================================== by Sziller ==="""
        self.actual_total_output = 0
        for output_rowobj in self.output_rowobj_list_in_opareatx:
            self.actual_total_output += output_rowobj.value
            
    def update_total_input(self):
        """=== Method name: ============================================================================
        ========================================================================================== by Sziller ==="""
        self.actual_total_input = 0
        for input_rowobj in self.input_set_in_opareatx.values():
            self.actual_total_input += input_rowobj.value

    def del_output(self, n):
        """=== Method name: ============================================================================
        ========================================================================================== by Sziller ==="""
        self.ids.output_display_area.remove_widget(self.output_rowobj_list_in_opareatx[n])
        del (self.output_rowobj_list_in_opareatx[n])
        self.update_output_n()
        self.update_total_output()
        self.display_total_output()
        self.update_fee()
        self.display_fee()
        
    def update_output_n(self):
        """=== Method name: update_output_n ============================================================================
        ========================================================================================== by Sziller ==="""
        for c, output_rowobj in enumerate(self.output_rowobj_list_in_opareatx):
            output_rowobj.n = c
            output_rowobj.update_n()
    
    # ---------------------------------------------------------------------------------------------------------------
    # - Display methods - OpAreaTx                                                      Display methods -   START   -
    # ---------------------------------------------------------------------------------------------------------------
    def display_all(self):
        """=== Method name: display_all ================================================================================
        Method performs all Label updates in current Object instance of OpAreaTx(OperationAreaBox)
        ========================================================================================== by Sziller ==="""
        self.display_total_utxo_balance()
        self.display_total_output()
        self.display_total_input()
        self.display_fee()

    def display_total_utxo_balance(self):
        """=== Method name: display_total_utxo_balance =================================================================
        Method updates Utxo balance Label in current Object instance of OpAreaTx(OperationAreaBox)
        ========================================================================================== by Sziller ==="""
        shown_value = units.bitcoin_unit_converter(value=self.utxomanager.balance_total,
                                                   unit_in=App.get_running_app().unit_base,
                                                   unit_out=App.get_running_app().unit_use)
        self.ids.lbl_utxo_balance.text = App.get_running_app().display_format.format(shown_value)
    
    def display_total_output(self):
        """=== Method name: display_total_output =======================================================================
        Method updates Output balance Label in current Object instance of OpAreaTx(OperationAreaBox)
        ========================================================================================== by Sziller ==="""
        shown_value = units.bitcoin_unit_converter(value=self.actual_total_output,
                                                   unit_in=App.get_running_app().unit_base,
                                                   unit_out=App.get_running_app().unit_use)
        self.ids.lbl_output_balance.text = App.get_running_app().display_format.format(shown_value)

    def display_total_input(self):
        """=== Method name: display_total_input ========================================================================
        Method updates Input balance Label in current Object instance of OpAreaTx(OperationAreaBox)
        ========================================================================================== by Sziller ==="""
        shown_value = units.bitcoin_unit_converter(value=self.actual_total_input,
                                                   unit_in=App.get_running_app().unit_base,
                                                   unit_out=App.get_running_app().unit_use)
        self.ids.lbl_input_balance.text = App.get_running_app().display_format.format(shown_value)
        
    def display_fee(self):
        """=== Method name: display_fee ================================================================================
        Method updates Fee Label in current Object instance of OpAreaTx(OperationAreaBox)
        ========================================================================================== by Sziller ==="""
        shown_value = units.bitcoin_unit_converter(value=self.actual_fee,
                                                   unit_in=App.get_running_app().unit_base,
                                                   unit_out=App.get_running_app().unit_use)
        self.ids.lbl_fee_balance.text = App.get_running_app().display_format.format(shown_value)
    
    # ---------------------------------------------------------------------------------------------------------------
    # - Display methods - OpAreaTx                                                      Display methods -   ENDED   -
    # ---------------------------------------------------------------------------------------------------------------
    
    def update_utxo_set(self):
        """=== Method name: update_utxo_set ============================================================================
        ========================================================================================== by Sziller ==="""
        for row in self.utxomanager.utxo_set:
            utxo_id_obj = models.UtxoId.construct_from_string(row["utxo_id"])  # redesign UtxoId source
            utxo_obj = Utxo(utxo_id=utxo_id_obj)
            converted_value = units.bitcoin_unit_converter(value=row["value"],
                                                           unit_in="btc",
                                                           unit_out=os.getenv("UNIT_USE"))
            utxo_obj.value = converted_value
            newline = UtxoRowObj(utxo_obj=utxo_obj, parent_op_area=self, field="utxo")
            self.ids.utxo_display_area.add_widget(newline)  # only add if key does not exist!!!
            self.utxo_set_in_opareatx[utxo_id_obj.__repr__()] = newline
        
    def use_output_data(self):
        """=== Method name: ============================================================================
        ========================================================================================== by Sziller ==="""
        self.update_total_output()
        self.display_total_output()
        self.update_fee()
        self.display_fee()
    
    def use_utxo_as_input(self, utxo_id_obj: models.UtxoId):    # redesign UtxoId source
        """=== Method name: ============================================================================
        ========================================================================================== by Sziller ==="""
        utxo_obj = Utxo(utxo_id=utxo_id_obj)
        utxo_obj.value = self.utxomanager.utxo_set_dict[utxo_id_obj.__repr__()]["value"]
        newline = UtxoRowObj(utxo_obj=utxo_obj, parent_op_area=self, field="input")
        self.ids.input_display_area.add_widget(newline)  # only add if key does not exist!!!
        self.input_set_in_opareatx[utxo_id_obj.__repr__()] = newline
        self.update_total_input()
        self.update_fee()
        self.display_total_input()
        self.display_fee()
        
    def disregard_utxo_as_input(self, utxo_id_obj: models.UtxoId):  # redesign UtxoId source
        """=== Method name: ============================================================================
        ========================================================================================== by Sziller ==="""
        utxo_obj = Utxo(utxo_id=utxo_id_obj)
        utxo_obj.value = self.utxomanager.utxo_set_dict[utxo_id_obj.__repr__()]["value"]
        self.ids.lbl_input_balance.text = "{:.8f}".format(self.actual_total_input)
        # Removing transaction line object from screen:
        # ATTENTION!!! Following line destructs ITSELF!!!
        self.ids.input_display_area.remove_widget(self.input_set_in_opareatx[utxo_id_obj.__repr__()])
        del (self.input_set_in_opareatx[utxo_id_obj.__repr__()])
        self.utxo_set_in_opareatx[utxo_id_obj.__repr__()].disabled = False
        self.update_total_input()
        self.update_fee()
        self.display_total_input()
        self.display_fee()


class OpAreaQrOut(OperationAreaBox):
    ccn = inspect.currentframe().f_code.co_name

    def __init__(self, **kwargs):
        super(OpAreaQrOut, self).__init__(**kwargs)

    def on_init(self):
        """=== Method name: on_init ====================================================================================
        Default method to run right after startup (or whenever defaulting back to initial state is necessary)
        ========================================================================================== by Sziller ==="""
        print("Started: {}".format(self.ccn))
        
        
class SalletVISOR(App):
    """=== Class name: SalletVISOR =====================================================================================
    Child of built-in class: App
    This is the Parent application for the Sealed of Kex manager project.
    Instantiation should - contrary to what is used on the net - happen by assigning it to a variable name.
    :param window_content:
    ============================================================================================== by Sziller ==="""
    def __init__(self, window_content: str, csm: float = 1.0):
        super(SalletVISOR, self).__init__()
        self.window_content = window_content
        self.content_size_multiplier = csm
        self.title = "Sallet - Visor: your transaction handler"
        self.balance_onchain_sats: int = 0
        # --- Database settings ---------------------------------------------   - Database settings -   START   -
        self.db_session = sql.createSession(db_path=os.getenv("DB_PATH_VISOR"),
                                            style=os.getenv("DB_STYLE_VISOR"))
        # --- Database settings ---------------------------------------------   - Database settings -   ENDED   -

        # --- Bitcoin related settings ----------------------------------  Bitcoin related settings -   START   -
        self.unit_base: str         = os.getenv("UNIT_BASE")
        self.unit_use: str          = os.getenv("UNIT_USE")
        self.display_format: str    = os.getenv("DISPLAY_FORMAT") + " " + os.getenv("UNIT_USE")
        # --- Bitcoin related settings ----------------------------------  Bitcoin related settings -   ENDED   -

    def change_screen(self, screen_name, screen_direction="left"):
        """=== Method name: change_screen ==============================================================================
        Use this screenchanger instead of the built-in method for more customizability and to enable further
        actions before changing the screen.
        Also, if screenchanging first needs to be validated, use this method!
        ========================================================================================== by Sziller ==="""
        smng = self.root  # 'root' refers to the only one root instance in your App. Here it is the actual ROOT
        smng.current = screen_name
        smng.transition.direction = screen_direction

    def build(self):
        """=== Method name: ============================================================================
        ========================================================================================== by Sziller ==="""
        return self.window_content
    
    def on_start(self):
        """=== Method name: on_start ===================================================================================
        Redefinition of a built-in function to be run after app is fully loaded with all it's subclasses instantiated
        ===========================================================================================by Sziller ==="""
        # --- Initiating each OpArea's <on_init> methods                                        START   -
        for screen_name, screen_obj in self.root.ids.items():
            for widget_name, widget_obj in screen_obj.ids.items():
                if widget_name.startswith("oparea_"):
                    widget_obj.on_init()
        # --- Initiating each OpArea's <on_init> methods                                        ENDED   -

        # --- Navigation-button handling                                                        START   -
        for navname, navbutton in self.root.ids.screen_intro.ids.navbar.ids.items():
            if navname == "button_nav_intro":
                navbutton.disabled = True
            else:
                navbutton.disabled = False
        # --- Navigation-button handling                                                        ENDED   -
        
        # --- Filling in large text-fields of Labels                                            START   -
        self.root.ids.screen_intro.ids.oparea_intro.ids.lbl_welcome_title.text = WELCOME_TITLE
        self.root.ids.screen_intro.ids.oparea_intro.ids.lbl_welcome_intro.text = WELCOME_TXT
        # --- Filling in large text-fields of Labels                                            ENDED   -

        
if __name__ == "__main__":
    from kivy.lang import Builder  # to freely pick kivy files

    # Define different display settings based on an index.
    # 0: Full-screen on any display,
    # 1: Portrait,
    # 2: Elongated Portrait,
    # 3: Raspberry Pi touchscreen - Landscape,
    # 4: Raspberry Pi touchscreen - Portrait,
    # 5: Large square
    display_settings = {0: {'fullscreen': False, 'run': Window.maximize},  # Full-screen on any display
                        1: {'fullscreen': False, 'size': (600, 1000)},  # Portrait
                        2: {'fullscreen': False, 'size': (500, 1000)},  # Portrait elongated
                        3: {'fullscreen': False, 'size': (640, 480)},  # Raspi touchscreen - landscape
                        4: {'fullscreen': False, 'size': (480, 640)},  # Raspi touchscreen - portrait
                        5: {'fullscreen': False, 'size': (1200, 1200)}  # Large square
                        }

    dotenv.load_dotenv()
    style_code = int(os.getenv("SCREENMODE_VISOR"))

    Window.fullscreen = display_settings[style_code]['fullscreen']
    if 'size' in display_settings[style_code].keys(): Window.size = display_settings[style_code]['size']
    if 'run' in display_settings[style_code].keys(): display_settings[style_code]['run']()

    # Load a specified Kivy file from the command-line argument or a default file.
    try:
        content = Builder.load_file(str(sys.argv[1]))
    except IndexError:
        content = Builder.load_file("kivy_sallet_VISOR.kv")

    # Create an instance of the SalletVISOR app with loaded content and a content size multiplier.
    application = SalletVISOR(window_content=content, csm=1)

    # Run the Kivy application with defined settings.
    application.run()
    
    # Close any existing OpenCV windows.
    cv2.destroyAllWindows()
