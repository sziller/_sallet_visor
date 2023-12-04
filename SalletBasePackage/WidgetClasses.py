"""All Widgets and Layouts defined for the main Python file"""

from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout

from SalletBasePackage.models import Utxo, Node


class LabelTitle(Label):
    """custom Label"""
    pass


class LabelInfo(Label):
    """custom Label"""
    pass


class LabelSubTitle(Label):
    """custom Label"""
    pass


class LabelSubSubTitle(Label):
    """custom Label"""
    pass


class LabelListitem(Label):
    """custom Label"""
    pass


class LabelLead(LabelListitem):
    """custom Label"""
    pass


class LabelEnd(LabelListitem):
    """custom Label"""
    pass


class LabelWelcomeListLeft(Label):
    """custom Label"""
    pass


class LabelWelcomeList(Label):
    """custom Label"""
    pass


class ScreenTitleLabel(Label):
    """custom Label"""
    pass


class ButtonSallet(Button):
    """custom Button"""
    pass


class ButtonListitem(ButtonSallet):
    """custom Button"""
    pass


class ButtonInfo(ButtonSallet):
    """custom Button"""
    pass


class TextInputSallet(TextInput):
    """custom TextInput"""
    pass


class UtxoDisplayArea(StackLayout):
    def __init__(self, **kwargs):
        super(UtxoDisplayArea, self).__init__(**kwargs)


class InputDisplayArea(StackLayout):
    def __init__(self, **kwargs):
        super(InputDisplayArea, self).__init__(**kwargs)


class OutputDisplayArea(StackLayout):
    def __init__(self, **kwargs):
        super(OutputDisplayArea, self).__init__(**kwargs)


class NodeDisplayArea(StackLayout):
    def __init__(self, **kwargs):
        super(NodeDisplayArea, self).__init__(**kwargs)


class OperationAreaBox(BoxLayout):
    """custom BoxLayout"""
    pass


class OutputRowObj(BoxLayout):
    orientation = "horizontal"

    def __init__(self, n: int, parent_op_area: OperationAreaBox, **kwargs):
        super(OutputRowObj, self).__init__(**kwargs)
        self.parent_op_area: OperationAreaBox = parent_op_area
        self.n: int = n
        self.value: int = 0
        self.script_type: str = "p2pkh"
        self.script: str = ""

        self.lbl_n = LabelLead(text=str(self.n))
        self.lbl_pl1 = LabelLead(text="style")
        self.txtinp_addr = TextInputSallet()
        self.txtinp_addr.bind(text=self.read_addr)
        self.txtinp_value = TextInputSallet()
        self.txtinp_value.bind(text=self.read_value)

        self.btn_del = ButtonListitem(text="-")
        self.btn_del.bind(on_release=self.del_this_row)
        self.btn_add = ButtonListitem(text="+")
        self.btn_add.bind(on_release=self.add_next_row)
        self.lbl_scrollbar = LabelEnd()

        self.lbl_n.size_hint = (0.1, 1)
        self.add_widget(self.lbl_n)

        self.lbl_pl1.size_hint = (0.2, 1)
        self.add_widget(self.lbl_pl1)

        self.txtinp_addr.size_hint = (0.2, 1)
        self.add_widget(self.txtinp_addr)

        self.txtinp_value.size_hint = (0.2, 1)
        self.add_widget(self.txtinp_value)

        if n:
            self.btn_del.size_hint = (0.05, 1)
            self.add_widget(self.btn_del)
            self.btn_add.size_hint = (0.05, 1)

        else:
            self.btn_add.size_hint = (0.1, 1)
        self.add_widget(self.btn_add)

        self.lbl_scrollbar.size_hint = (0.2, 1)
        self.add_widget(self.lbl_scrollbar)
        
    # Local methods to be called on generated Widget's action - redirecting to higher hierarchy object  -   START   -
    def add_next_row(self, inst=None, **kwargs):
        """=== Method name: add_next_row ===============================================================================
        Method to be called by generated Widget (Button or similar), and to activate subsequent actions in parent
        OperationArea.
        Method to be triggered on adding a row.
        ========================================================================================== by Sziller ==="""
        self.btn_add.disabled = True
        self.parent_op_area.add_new_output_rowobj()

    def del_this_row(self, inst=None, **kwargs):
        """=== Method name: del_this_row ===============================================================================
        Method to be called by generated Widget (Button or similar), and to activate subsequent actions in parent
        OperationArea.
        Method to be triggered on deleting a row.
        ========================================================================================== by Sziller ==="""
        self.parent_op_area.del_output(n=self.n)

    def update_n(self):
        """=== Method name: update_n ===================================================================================
        Method writes actual 'n' value into matching Label
        ========================================================================================== by Sziller ==="""
        self.lbl_n.text = str(self.n)

    def read_value(self, inst, value):
        """=== Method name: read_value =================================================================================
        Method to be called by generated Widget (Button or similar), and to activate subsequent actions in parent
        OperationArea.
        Handling data received by Widget.
        ========================================================================================== by Sziller ==="""
        print(type(value))
        try:
            self.value = float(value)
        except ValueError:
            print("Use numbers please!")
        self.parent_op_area.use_output_data()

    def read_addr(self, inst, value):
        """ TBD """
        print(value)

    # Local methods to be called on generated Widget's action - redirecting to higher hierarchy object  -   ENDED   -


class NodeRowObj(BoxLayout):
    orientation = "horizontal"

    def __init__(self, node_obj: Node, parent_op_area: OperationAreaBox, **kwargs):
        super(NodeRowObj, self).__init__(**kwargs)
        self.node_obj = node_obj
        self.parent_op_area: OperationAreaBox = parent_op_area
        
        self.lbl_alias              = LabelWelcomeList(text=self.node_obj.alias)
        self.lbl_ip                 = LabelWelcomeListLeft(text=self.node_obj.ip)
        self.lbl_port               = LabelWelcomeListLeft(text=str(self.node_obj.port))
        self.lbl_owner              = LabelWelcomeListLeft(text=self.node_obj.owner)
        self.lbl_desc               = LabelLead(text=self.node_obj.desc)
        self.btn_use                = ButtonSallet(text="use")
        self.btn_use.bind(on_release=self.use_this_node)
        self.lbl_scrollbar          = LabelEnd(text=" - ")

        self.lbl_alias.size_hint        = (0.2, 1)
        self.lbl_ip.size_hint           = (0.175, 1)
        self.lbl_port.size_hint         = (0.1, 1)
        self.lbl_owner.size_hint        = (0.225, 1)
        self.lbl_desc.size_hint         = (0.25, 1)
        self.btn_use.size_hint          = (0.03, 1)
        self.lbl_scrollbar.size_hint    = (0.02, 1)
        
        self.add_widget(self.lbl_alias)
        self.add_widget(self.lbl_ip)
        self.add_widget(self.lbl_port)
        self.add_widget(self.lbl_owner)
        self.add_widget(self.lbl_desc)
        self.add_widget(self.btn_use)
        self.add_widget(self.lbl_scrollbar)

    def use_this_node(self, inst=None, **kwargs):
        """=== Method to use actual Node to broadcast Transaction(s)"""
        print("Button pushed: <use_this_node>")
        self.disabled = True
        self.parent_op_area.use_node(node=self.node_obj)
        
        
class UtxoRowObj(BoxLayout):
    orientation = "horizontal"

    def __init__(self, utxo_obj: Utxo, parent_op_area: OperationAreaBox, field: str = "utxo", **kwargs):
        super(UtxoRowObj, self).__init__(**kwargs)
        self.utxo_obj = utxo_obj
        self.uxto_id_obj = self.utxo_obj.utxo_id
        self.value: float = self.utxo_obj.value
        self.parent_op_area: OperationAreaBox = parent_op_area
        self.field: str = field  # 'utxo' or 'input'

        self.lbl_id = LabelLead(text=self.uxto_id_obj.__repr__())
        self.lbl_value = LabelEnd(text="{}".format(self.value))
        if self.field == 'utxo':
            self.btn_mark = ButtonListitem(text="use")
            self.btn_mark.bind(on_release=self.use_this_utxo)

        elif self.field == 'input':
            self.btn_mark = ButtonListitem(text="del")
            self.btn_mark.bind(on_release=self.remove_this_utxo)

        self.lbl_scrollbar = LabelEnd()

        self.lbl_id.size_hint = (0.75, 1)
        self.lbl_value.size_hint = (0.175, 1)
        self.btn_mark.size_hint = (0.05, 1)
        self.lbl_scrollbar.size_hint = (0.025, 1)
        self.add_widget(self.lbl_id)
        self.add_widget(self.lbl_value)
        self.add_widget(self.btn_mark)
        self.add_widget(self.lbl_scrollbar)

    def use_this_utxo(self, inst=None, **kwargs):
        """=== Method to use actual utxo as Transaction input"""
        print("Button pushed: <use_this_utxo>")
        self.disabled = True
        self.parent_op_area.use_utxo_as_input(self.uxto_id_obj)

    def remove_this_utxo(self, inst=None, **kwargs):
        """=== Method to use actual utxo as Transaction input"""
        print("Button pushed: <remove_this_utxo>")
        self.parent_op_area.disregard_utxo_as_input(self.uxto_id_obj)
