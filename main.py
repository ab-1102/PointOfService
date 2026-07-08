from PyQt6.QtGui import QFont
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication
import dbms
import gui
import sys
import BillMaker

if __name__ == "__main__":
    # DBMS Setup and Data Fetch
    db = dbms.POSDatabase()
    inventory = db.get_all_products()

    # BillMaker
    bill = BillMaker.Bill()

    # GUI Initialization
    application = QApplication(sys.argv)
    app = gui.GUI()
    app.showFullScreen()
    app.raise_()
    app.activateWindow()
    app.setFont(QFont("Google Sans", 12))
    popup = gui.ProductEditPopup()
    addPopup = gui.ProductAddPopup()

    # Setting Data
    categorizedProducts = db.get_products_by_category()
    categories = db.get_all_categories()
    app.categories = categories

    def refresh():
        global inventory, categories, categorizedProducts
        inventory = db.get_all_products()
        categories = db.get_all_categories()
        categorizedProducts = db.get_products_by_category()
        app.categories = categories
        app.set_categories(categories) #Inventory page
        popup.set_categories(categories) #Popup page
        addPopup.set_categories(categories) #AddPopup page
        app.update_billing(categorizedProducts) #Billing page
        app.update_inventory(inv = inventory) #Invetory Page
        app.update_bill(bill.get_items(), bill.get_total())
        app.line_edit_reset()
        app.set_bill_log(db.fetch_bill_log(),db.fetch_all_bill_items())
        app.draw_graphs(db.get_daily_revenue_trend(),
                        db.get_product_sales_volume(),
                        db.get_category_revenue(),
                        db.get_profit_analysis(),
                        db.get_inventory_movement(),
                        db.get_category_revenue_trend()
                        )


    refresh()

    # GUI Inventory Page Setup
    def edit_product(product_id:int):
        popup.show()
        popup.set_value(db.fetch_product(product_id))
        return

    app.update_inventory(inv = inventory)
    app.edit_product_inventory.connect(edit_product)

    # GUI editPopup
    def popup_edit_save():
        db.edit_product(popup.popup_data())
        popup.close()
        refresh()
        return
    def popup_edit_cancel():
        popup.close()
        refresh()
        return
    popup.popup_save.connect(popup_edit_save)
    popup.popup_cancel.connect(popup_edit_cancel)

    # GUI NewProPopup
    def add_new_product(state:str):
        if state == 'add':
            db.add_product(addPopup.new_product_data())
            refresh()
            addPopup.set_value()
            addPopup.close()
        else:
            addPopup.set_value()
            addPopup.close()
        return
    def open_add_new_product():
        addPopup.show()
        return
    app.add_new_product.connect(open_add_new_product)
    addPopup.popup_add.connect(add_new_product)


    # GUI Billing Page Setup
    def add_product_to_bill_page(product:list):
        bill.add(product)
        app.update_bill(bill.get_items(),bill.get_total())
        return
    app.product_to_bill.connect(add_product_to_bill_page)

    def edit_bill(product:list):
        if product[1] == 'increase':
            bill.add(product[0])
            app.update_bill(bill.get_items(),bill.get_total())
        elif product[1] == 'decrease':
            bill.reduce(product[0])
            app.update_bill(bill.get_items(),bill.get_total())
    app.bill_edit.connect(edit_bill)

    def finish_bill(code:list):
        if code[0] == 'pay':
            if code[1] == '':
                name = 'Walk In'
            else:
                name = code[1]
            if code[2] == '':
                number = '0000000000'
            else:
                number = code[2]
            payment_method = code[3]
            db.add_bill(bill.get_items(),bill.get_total(), name, number, payment_method)

            bill.print(name, int(number))
            refresh()
        if code[0] == 'cancel':
            bill.clear()
            refresh()
    app.finished_billing.connect(finish_bill)

    # Closer
    if application.exec()==0:
        db.close()
        sys.exit()
    else:
        print("ERROR")
        sys.exit()
