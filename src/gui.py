import os
import sys

from PyQt6.QtGui import QColor
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from typing import List, Any, Tuple, Dict

from PyQt6.QtGui import QFont
from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QPushButton, QTableWidgetItem, QWidget, QDialog, QGridLayout, QHBoxLayout, \
    QLabel, QListWidgetItem, QSizePolicy, QVBoxLayout, QTreeWidgetItem, QLayout, QHeaderView
from PyQt6.QtCore import pyqtSignal, Qt

def resource_path(relative_path):
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

def get_hue(index, divisions):
    return int(index * 359//divisions)

BG = "#252526"
BG2 = "#2D2D30"
BG3 = "#3C3C3C"

TEXT = "#F0F0F0"
TEXT_DISABLED = "#808080"

BORDER = "#555555"

ACCENT = "#007ACC"
ACCENT_HOVER = "#1F8CE6"
ACCENT_PRESSED = "#0062A3"

SUCCESS = "#2E7D32"
WARNING = "#F9A825"
ERROR = "#C62828"

GRID = "#4B4B4B"
HEADER = "#3A3A3A"

SELECTION = "#264F78"

class GUI(QMainWindow):
    # Button connections
    edit_product_inventory = pyqtSignal(int)
    add_new_product = pyqtSignal()
    product_to_bill = pyqtSignal(list)
    bill_edit = pyqtSignal(list)
    finished_billing = pyqtSignal(list)
    switch_tab = pyqtSignal(str)
    config_update = pyqtSignal(list)

    # Class Variables
    categories = []
    def __init__(self):
        super().__init__()

        # Load UI file
        uic.loadUi(resource_path("../ui/pos.ui"), self)

        font = QFont("Google Sans", 12)  # Change 11 to your desired size
        self.setFont(font)

        self.setStyleSheet(f"""
        QMainWindow {{
            background: {BG};
        }}

        QWidget {{
            background: {BG};
            color: {TEXT};
        }}

        QLabel {{
            color: {TEXT};
            background: transparent;
        }}

        QPushButton {{
            background: {BG3};
            color: {TEXT};
            border: 1px solid {BORDER};
            border-radius: 6px;
            padding: 5px;
        }}

        QPushButton:hover {{
            background: #4A4A4A;
        }}

        QPushButton:pressed {{
            background: #202020;
        }}

        QPushButton:disabled {{
            background: #303030;
            color: {TEXT_DISABLED};
        }}

        QLineEdit,
        QComboBox {{
            background: {BG2};
            color: {TEXT};
            border: 1px solid {BORDER};
            padding: 4px;
        }}

        QComboBox QAbstractItemView {{
            background: {BG2};
            color: {TEXT};
            selection-background-color: {SELECTION};
        }}

        QListWidget,
        QTableWidget,
        QTreeWidget {{
            background: {BG2};
            alternate-background-color: {BG};
            color: {TEXT};
            border: 1px solid {BORDER};
            gridline-color: {GRID};
            selection-background-color: {SELECTION};
        }}

        QHeaderView::section {{
            background: {HEADER};
            color: {TEXT};
            border: 1px solid {BORDER};
            padding: 4px;
        }}

        QTabWidget::pane {{
            border: 1px solid {BORDER};
        }}

        QTabBar::tab {{
            background: {BG3};
            color: {TEXT};
            padding: 8px;
        }}

        QTabBar::tab:selected {{
            background: {ACCENT};
        }}

        QScrollBar:vertical,
        QScrollBar:horizontal {{
            background: {BG};
        }}

        QScrollBar::handle {{
            background: {BG3};
        }}

        QMenuBar,
        QMenu {{
            background: {BG2};
            color: {TEXT};
        }}

        QToolTip {{
            background: {BG3};
            color: {TEXT};
            border: 1px solid {BORDER};
        }}
        """)

        # Initial variable setup
        self.inventory = None
        self.InventoryAddNewPushButton.clicked.connect(self.add_new_product)
        self.PayPushButton.clicked.connect(lambda checked: self.finished_billing.emit(['pay', self.BillingNameLineEdit.text(), self.BillingPhoneNoLineEdit.text(), self.paymentMethodComboBox.currentText()]))
        self.CanclePushButton.clicked.connect(lambda checked: self.finished_billing.emit(['cancel', self.BillingNameLineEdit.text(), self.BillingPhoneNoLineEdit.text(), self.paymentMethodComboBox.currentText()]))
        self.ConfigSavePushButton.clicked.connect(lambda checked: self.config_update.emit(self.get_config_update()))
        self.CloseButton.clicked.connect(lambda checked: self.close())

        # Graphs
        self.drt_graph = GraphWidget()
        self.psv_graph = GraphWidget()
        self.cr_graph = GraphWidget()
        self.pa_graph = GraphWidget()
        self.im_graph = GraphWidget()
        self.c_graph = GraphWidget()

        QVBoxLayout(self.DRTgraph).addWidget(self.drt_graph)
        QVBoxLayout(self.PSVgraph).addWidget(self.psv_graph)
        QVBoxLayout(self.CRgraph).addWidget(self.cr_graph)
        QVBoxLayout(self.PAgraph).addWidget(self.pa_graph)
        QVBoxLayout(self.IMgraph).addWidget(self.im_graph)
        QVBoxLayout(self.Cgraph).addWidget(self.c_graph)

    def get_config_update(self):
        return [self.PrinterNameLineEdit.text(),self.DatabasePathLineEdit.text()]

    def set_config(self, printer_name, database_path):
        self.PrinterNameLineEdit.setText(printer_name)
        self.DatabasePathLineEdit.setText(database_path)

    def update_inventory(self, inv: List[List] = None):
        if inv is not None:
            self.inventory = inv
            self.InventoryList.setSortingEnabled(False)
            self.InventoryList.clearContents()  # remove cell contents
            self.InventoryList.setRowCount(len(self.inventory))  # set exact rows
            self.InventoryList.setColumnCount(len(self.inventory[0]) + 1) # set 1+ column for button
            self.InventoryList.setHorizontalHeaderLabels(["ID", "Name", "Barcode", "Category", "Cost Price", "Sales Price", "Stock", ""])

            self.InventoryList.setColumnWidth(0, 60)  # ID
            self.InventoryList.setColumnWidth(1, 300)  # Name
            self.InventoryList.setColumnWidth(2, 120)  # Barcode
            self.InventoryList.setColumnWidth(3, 150)  # Category
            self.InventoryList.setColumnWidth(4, 100)  # Cost Price
            self.InventoryList.setColumnWidth(5, 100)  # Sales Price
            self.InventoryList.setColumnWidth(6, 80)  # Stock
            self.InventoryList.setColumnWidth(7, 80)  # Edit button

            for row, row_data in enumerate(self.inventory):
                for col, value in enumerate(row_data):
                    item = QTableWidgetItem()
                    item.setData(Qt.ItemDataRole.DisplayRole, value)
                    item.setData(Qt.ItemDataRole.EditRole, value)

                    self.InventoryList.setItem(
                        row,
                        col,
                        item
                    )

                # Create button
                edit_btn = QPushButton("Edit")

                # Connect button click
                edit_btn.clicked.connect(lambda checked, id=row_data[0]: self.edit_product_inventory.emit(id))

                # Adding edit button at the end of each row
                self.InventoryList.setCellWidget(row, len(self.inventory[0]), edit_btn) # as index starts from 0

            self.InventoryList.setSortingEnabled(True)
            font = self.InventoryList.font()
            font.setPointSize(12)
            self.InventoryList.setFont(font)
        else:
            self.inventory = inv

    def set_categories(self, categories):
        if categories is not None:
            self.categories = categories
        else:
            self.categories = []
        # Inventory Page
        self.InventoryCategoryComboBox.clear()
        self.InventoryCategoryComboBox.addItem("ALL")
        self.InventoryCategoryComboBox.addItems(self.categories)

    def update_billing(self, data:dict[str, List[List[Any]]]) -> None:
        if data is not None:
            self.categories = data.keys()
            self.ProductCategoryTabs.clear()
            self.CategoryButtonsTable.clearContents()  # remove cell contents
            self.CategoryButtonsTable.horizontalHeader().hide()
            self.CategoryButtonsTable.verticalHeader().hide()
            self.CategoryButtonsTable.setRowCount(len(self.categories)//2 + len(self.categories)%2)  # set exact rows
            self.CategoryButtonsTable.setColumnCount(2)  # set 2 columns for button
            for row in range(self.CategoryButtonsTable.rowCount()):
                self.CategoryButtonsTable.setRowHeight(row, self.CategoryButtonsTable.size().height() // self.CategoryButtonsTable.rowCount() - 5)
            for col in range(self.CategoryButtonsTable.columnCount()):
                self.CategoryButtonsTable.setColumnWidth(col, 120)
            self.CategoryButtonsTable.setFixedWidth(120 * 2 + 5)
            self.CategoryButtonsTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
            self.CategoryButtonsTable.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

            for q, category in enumerate(self.categories):
                # Tab Stuff
                tab = QWidget()
                grid = QGridLayout()
                tab.setLayout(grid)

                # List Stuff
                c_row = q // 2
                c_col = q % 2
                c_btn = QPushButton(category)

                base = QColor.fromHsl(get_hue(q, len(self.categories)), 125, 70)  # Hue, Saturation, Lightness
                hover = base.lighter(110)  # 10% lighter
                pressed = base.darker(130)  # 30% darker
                checked = base.darker(160)

                c_btn.setStyleSheet(f"""
                QPushButton {{
                    font-family: "Google Sans";
                    font-size: 12pt;
                    background-color: {base.name()};
                    color: white;
                    border: none;
                    border-radius: 6px;
                }}

                QPushButton:hover {{
                    background-color: {hover.name()};
                }}

                QPushButton:pressed {{
                    background-color: {pressed.name()};
                }}

                QPushButton:checked {{
                    background-color: {checked.name()};
                }}
                """)

                c_btn.clicked.connect(lambda checked=False, index = q: self.ProductCategoryTabs.setCurrentIndex(index))

                self.CategoryButtonsTable.setCellWidget(c_row, c_col, c_btn)

                for i, product in enumerate(data[category]):
                    btn = QPushButton(product[1])
                    btn.setMinimumHeight(100)
                    btn.setStyleSheet(f"""
                    QPushButton {{
                        font-family: "Google Sans";
                        font-size: 12pt;
                        border-width: 2px;
                        border-style: solid;
                        border-color: {base.name()};
                        border-radius: 10px;
                        background-color: #393939; 
                    }}
                    QPushButton:hover {{
                        background-color: #474747;
                    }}
    
                    QPushButton:pressed {{
                        background-color: #1E1E1E;
                    }}
    
                    QPushButton:checked {{
                        background-color: #1E1E1E;
                    }}
                    """)

                    if product[6] <= 0:
                        btn.setEnabled(False)
                    else:
                        btn.setEnabled(True)
                    btn.clicked.connect(lambda checked, pro=product: self.product_to_bill.emit(pro))
                    p_row = i // 3
                    p_col = i % 3

                    grid.addWidget(btn, p_row, p_col)
                self.ProductCategoryTabs.addTab(tab, category)

            self.ProductCategoryTabs.tabBar().hide()
        return

    def update_bill(self, data, total) -> None:
        if data is not None:
            self.CartList.clear()
            self.CartList.setFixedWidth(400)
            for unit in data:
                widget = QWidget()
                layout = QHBoxLayout(widget)
                name_label = QLabel(str(unit[0][1]))
                layout2 = QVBoxLayout()
                minus_btn = QPushButton("-")
                minus_btn.setFixedSize(30, 20)
                minus_btn.clicked.connect(lambda checked, pro=unit[0]: self.bill_edit.emit([pro, 'decrease']))
                plus_btn = QPushButton("+")
                plus_btn.setFixedSize(30, 20)
                plus_btn.clicked.connect(lambda checked, pro=unit[0]: self.bill_edit.emit([pro, 'increase']))

                qty_label = QLabel(str(unit[1]))
                qty_label.setMinimumWidth(50)
                qty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

                cost_label = QLabel(str(unit[2]))
                cost_label.setMinimumWidth(50)
                cost_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

                # Add to layout
                layout.addWidget(name_label)
                layout.addStretch()
                layout2.addWidget(plus_btn)
                layout2.addWidget(minus_btn)
                layout.addLayout(layout2)
                layout.addWidget(qty_label)
                layout.addWidget(cost_label)

                item = QListWidgetItem()
                item.setSizeHint(widget.sizeHint())

                self.CartList.addItem(item)
                self.CartList.setItemWidget(item, widget)
            self.TotalLabel.setText(f"Total: ₹{total}")
        return

    def set_bill_log(self, bills, bill_items):
        self.BillsTreeWidget.clear()
        if bills is not None:
            self.BillsTreeWidget.setColumnCount(7)
            self.BillsTreeWidget.setHeaderLabels([
                "Bill-Id",
                "Customer Name",
                "Customer Phone",
                "Date Time",
                "Amount",
                "Payment Method",
                "Payment Status"
            ])
            self.BillsTreeWidget.setColumnWidth(0, 250)  # Bill ID
            self.BillsTreeWidget.setColumnWidth(1, 180)  # Customer Name
            self.BillsTreeWidget.setColumnWidth(3, 200)  # Date Time

            for bill in bills:
                element  = QTreeWidgetItem([
                    str(bill[0]), # bill id
                    str(bill[1]), # customer name
                    str(bill[2]), # customer phone
                    str(bill[3]), # date time
                    str(bill[4]), # total price
                    str(bill[5]), # payment method
                    str(bill[6]) # payment status
                ])
                element.addChild(QTreeWidgetItem(['', '', '', '']))
                element.addChild(QTreeWidgetItem(['PRODUCT', 'QTY', 'RATE', 'TOTAL']))
                for bill_item in bill_items[bill[0]]:
                    product = QTreeWidgetItem([
                        str(bill_item[3]), # name
                        str(bill_item[4]), # quantity
                        str(bill_item[5]), # rate
                        str(bill_item[6])  # total
                    ])
                    element.addChild(product)
                element.addChild(QTreeWidgetItem(['', '', '', '']))
                self.BillsTreeWidget.addTopLevelItem(element)
            self.BillsTreeWidget.setSortingEnabled(False)
            font = self.BillsTreeWidget.font()
            font.setPointSize(12)
            self.BillsTreeWidget.setFont(font)

    def line_edit_reset(self):
        self.BillingNameLineEdit.setText('')
        self.BillingPhoneNoLineEdit.setText('')

    def draw_graphs(self,
                    drt: Tuple[List[str], List[float]],
                    psv: Tuple[List[str], List[float]],
                    cr: Tuple[List[str], List[float]],
                    pa: Tuple[List[str], List[float]],
                    im: Tuple[List[str], List[int]],
                    crt: Tuple[List[str], Dict[str, List[float]]]
                    ):

        # ----------Daily Revenue Trend----------
        self.drt_graph.draw_line_graph(
            drt,
            "Date",
            "Revenue(₹)",
            "Daily Revenue Trend"
        )

        # ----------Product Sales Volume---------
        self.psv_graph.draw_bar_graph(
            psv,
            "Product",
            "Sales(₹)",
            "Product Sales Volume"
        )

        # ----------Category-wise Revenue---------
        self.cr_graph.draw_pie_graph(
            cr,
            "Category-wise Revenue"
        )

        # ----------Profit Analysis---------
        self.pa_graph.draw_line_graph(
            pa,
            "Date",
            "Profit(₹)",
            "Profit Analysis"
        )

        # ----------Inventory Movement---------
        self.im_graph.draw_bar_graph(
            im,
            "Date",
            "Change in Stock",
            "Inventory Movement"
        )

        # ----------Category Revenue Trend---------
        self.c_graph.draw_multi_line_graph(
            crt,
            "Date",
            "Revenue (₹)",
            "Category Revenue Trend"
        )

class ProductEditPopup(QDialog):
    # Class Variables
    categories = []
    # Button Connections
    popup_save = pyqtSignal(str)
    popup_cancel = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        uic.loadUi(resource_path("../ui/productEditPopup.ui"), self)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.PopupSaveButton.clicked.connect(lambda checked: self.popup_save.emit('save'))
        self.PopupCancleButton.clicked.connect(lambda checked: self.popup_cancel.emit('cancel'))

        self.setWindowFlag(
            Qt.WindowType.FramelessWindowHint
        )
        self.PopupSaveButton.setFocus()

    def popup_data(self):
        return [
            self.PopupProductId.text(),
            self.PopupName.text(),
            self.PopupBarcode.text(),
            self.PopupCategory.currentText(),
            self.PopupCostPrice.text(),
            self.PopupSalesPrice.text(),
            self.PopupStock.text()
        ]

    def set_value(self, product_data: List = None):
        self.PopupProductId.setText(str(product_data[0]))
        self.PopupName.setText(str(product_data[1]))
        self.PopupBarcode.setText(str(product_data[2]))
        self.PopupCategory.setCurrentText(str(product_data[3]))
        self.PopupCostPrice.setText(str(product_data[4]))
        self.PopupSalesPrice.setText(str(product_data[5]))
        self.PopupStock.setText(str(product_data[6]))

    def set_categories(self, categories):
        if categories is not None:
            self.categories = categories
        else:
            self.categories = []
        # popup page
        self.PopupCategory.clear()
        self.PopupCategory.addItem("ALL")
        self.PopupCategory.addItems(self.categories)

class ProductAddPopup(QDialog):
    # Button Connections
    popup_add = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        uic.loadUi(resource_path("../ui/productAddPopup.ui"), self)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.PopupSaveButton.clicked.connect(lambda checked: self.popup_add.emit('add'))
        self.PopupCancleButton.clicked.connect(lambda checked: self.popup_add.emit('cancle'))

        self.setWindowFlag(
            Qt.WindowType.FramelessWindowHint
        )
    def new_product_data(self):
        return [
        self.PopupName.text(),
        self.PopupBarcode.text(),
        self.PopupCategory.currentText(),
        self.PopupCostPrice.text(),
        self.PopupSalesPrice.text(),
        self.PopupStock.text()
    ]

    def set_categories(self, categories):
        if categories is not None:
            self.categories = categories
        else:
            self.categories = []
        # popup page
        self.PopupCategory.clear()
        self.PopupCategory.addItems(self.categories)

    def set_value(self):
        self.PopupName.setText('')
        self.PopupBarcode.setText('')
        #self.PopupCategory.setCurrentText('')
        self.PopupCostPrice.setText('')
        self.PopupSalesPrice.setText('')
        self.PopupStock.setText('')

class GraphWidget(FigureCanvasQTAgg):
    def __init__(self):
        self.figure = Figure()
        super().__init__(self.figure)
        self.ax = self.figure.add_subplot(111)

    def draw_line_graph(self, data, x_label, y_label, name):
        x, y = data

        self.ax.clear()
        self.ax.set_aspect("auto")

        self.ax.plot(x, y)

        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        self.ax.set_title(name)

        self.ax.grid(True)

        self.figure.tight_layout()
        self.draw()

    def draw_bar_graph(self, data, x_label, y_label, name):
        x, y = data

        self.ax.clear()
        self.ax.set_aspect("auto")

        self.ax.bar(x, y)

        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        self.ax.set_title(name)

        self.ax.tick_params(axis='x', labelrotation=90)

        self.ax.grid(True, axis="y")

        self.figure.tight_layout()
        self.draw()

    def draw_pie_graph(self, data, name):
        labels, values = data

        self.ax.clear()

        self.ax.pie(
            values,
            labels=labels,
            autopct="%1.1f%%",
            startangle=90
        )

        self.ax.axis("equal")
        self.ax.set_title(name)

        self.figure.tight_layout()
        self.draw()

    def draw_multi_line_graph(self,data: Tuple[List[str], Dict[str, List[float]]],x_label: str,y_label: str,name: str) -> None:
        dates, category_data = data

        self.ax.clear()
        self.ax.set_aspect("auto")

        for category, revenue in category_data.items():
            self.ax.plot(
                dates,
                revenue,
                label=category
            )

        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        self.ax.set_title(name)

        self.ax.grid(True)

        self.ax.legend()

        self.figure.tight_layout()
        self.draw()