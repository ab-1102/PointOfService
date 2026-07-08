import datetime
import textwrap
from escpos.printer import Win32Raw
import os
import sys

PRINTER_NAME = "Rugtek RP326"

def resource_path(relative_path):
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


class Printer:
    def __init__(self):
        self.customer_name = ""
        self.customer_phone = ""
        self.items = []
        self.total = 0
        self.tokens = []

        self.printer = Win32Raw(PRINTER_NAME)
        self.printer.profile.profile_data["media"]["width"]["pixels"] = 576

        self.margin = "  "

    def line(self, text=""):
        self.printer.text(self.margin + text + "\n")

    def print_bill(self):
        now = datetime.datetime.now()

        # Logo
        self.printer.image(
            resource_path("assets/logo.png"),
            center=True,
            impl="bitImageRaster"
        )

        # Shop Info
        self.printer.set(align="center", bold=True)
        self.printer.text("SOL Bites\n")

        self.printer.set(align="center", bold=False)
        self.printer.text("Ground Floor, CH 5, MR 10 Rd, Sector C\n")
        self.printer.text("Sukhliya, Indore, Madhya Pradesh 452010\n")
        self.printer.text("Mobile: 9644363636\n")
        self.printer.text("Email: solbites2026@gmail.com\n")

        self.line("-" * 46)

        # Customer details
        self.printer.set(align="left", bold=False)
        self.line(f"Customer : {self.customer_name}")
        self.line(f"Mobile   : {self.customer_phone}")
        self.line(f"Date     : {now.strftime('%d-%m-%Y')}")
        self.line(f"Time     : {now.strftime('%H:%M:%S')}")

        self.line("-" * 46)

        # Table Header
        self.printer.set(bold=True)
        self.line(
            f"{'Item':<24}{'Rate':>6}{'Qty':>4}{'Amount':>10}"
        )

        self.line("-" * 46)

        # Items
        self.printer.set(bold=False)

        for item in self.items:
            name = str(item[0])
            price = str(item[1])
            qty = str(item[2])
            amount = str(item[3])

            wrapped_name = textwrap.wrap(name, width=24)

            for i, line_name in enumerate(wrapped_name):
                if i == 0:
                    self.line(
                        f"{line_name:<24}{price:>6}{qty:>4}{amount:>10}"
                    )
                else:
                    self.line(f"{line_name:<24}")

        self.line("-" * 46)

        # Final Total
        self.printer.set(
            bold=True,
            width=1,
            height=1,
            align="left"
        )

        self.line(
            f"{'TOTAL:':<26}{('Rs. ' + str(self.total)):>20}"
        )

        self.line("-" * 46)

        # Footer
        self.printer.set(align="center", bold=False)
        self.line("Thank you!")
        self.line("Visit Again")
        self.line("This is a computer-generated invoice.")
        self.line("Food once served will not be taken back.")
        self.line("")

        self.printer.cut()

    def print_token(self):
        if not self.tokens:
            return

        now = datetime.datetime.now()

        self.printer.set(align="center", bold=True, width=2, height=2)
        self.printer.text("KITCHEN TOKEN\n")

        self.printer.set(align="left", bold=False, width=1, height=1)

        self.line("-" * 46)
        self.line(f"Customer : {self.customer_name}")
        self.line(f"Mobile   : {self.customer_phone}")
        self.line(f"Date     : {now.strftime('%d-%m-%Y')}")
        self.line(f"Time     : {now.strftime('%H:%M:%S')}")
        self.line("-" * 46)

        # Token header
        self.printer.set(bold=True)
        self.line(
            f"{'Item':<34}{'Qty':>8}"
        )

        self.line("-" * 46)

        self.printer.set(bold=False)

        for item in self.tokens:
            print(item)
            name = str(item[0])
            qty = str(item[2])

            wrapped_name = textwrap.wrap(name, width=34)

            for i, line_name in enumerate(wrapped_name):
                if i == 0:
                    self.line(
                        f"{line_name:<34}{qty:>8}"
                    )
                else:
                    self.line(f"{line_name:<34}")

        self.line("-" * 46)

        self.printer.set(align="center")
        self.line("Prepare Order")
        self.line("")

        self.printer.cut()

    def print(self):
        self.print_bill()

        #print("2nd print called")
        #self.print_bill()

        self.print_token()

        # Reset
        self.customer_name = ""
        self.customer_phone = ""
        self.items.clear()
        self.tokens.clear()
        self.total = 0
        self.printer.close()


if __name__ == "__main__":
    p = Printer()

    p.customer_name = "Test Customer"
    p.customer_phone = "9876543210"

    p.items.append(["Classic Cold Coffee Large", 120, 2, 240])
    p.items.append(["Belgian Chocolate Brownie With Ice Cream", 180, 1, 180])
    p.items.append(["Garlic Bread", 110, 1, 110])

    p.tokens.append(["Classic Cold Coffee Large", 120, 2, 240])
    p.tokens.append(["Belgian Chocolate Brownie With Ice Cream", 180, 1, 180])

    p.total = 530

    print("Printing sample bill...")
    p.print()
    print("Done.")