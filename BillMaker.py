import pos

PRINTER_NAME = "Rugtek RP326"
pos.PRINTER_NAME = PRINTER_NAME

class Bill:
    def __init__(self):
        super().__init__()
        self.products = {}
        self.total = 0

    def add(self, product):
        product_id = product[0]

        if product_id in self.products:
            self.products[product_id]["qty"] += 1
        else:
            self.products[product_id] = {
                "product": tuple(product),
                "qty": 1
            }

        self.total += product[5]   # sales price
        return

    def remove(self, product):
        product_id = product[0]

        if product_id in self.products:
            qty = self.products[product_id]["qty"]
            price = self.products[product_id]["product"][5]

            self.total -= qty * price
            del self.products[product_id]

        return

    def reduce(self, product: list):
        product_id = product[0]

        if product_id in self.products:
            self.products[product_id]["qty"] -= 1
            self.total -= self.products[product_id]["product"][5]

            if self.products[product_id]["qty"] <= 0:
                del self.products[product_id]

        return

    def clear(self):
        self.products.clear()
        self.total = 0
        return

    def print(self,name:str, number:int):
        printer = pos.Printer()
        printer.customer_name = name
        printer.customer_phone = number
        for product_id, data in self.products.items():
            product = data["product"]
            qty = data["qty"]
            line_total = product[5] * qty

            printer.items.append([product[1], product[5], qty, line_total])

            if product[3] == "Stall":
                printer.tokens.append([product[1], product[5], qty, line_total])

        printer.total = self.total
        printer.print()
        self.clear()
        return

    def get_items(self):
        return [
            (data["product"], data["qty"], data["product"][5] * data["qty"])
            for data in self.products.values()
        ]

    def get_total(self):
        return int(self.total)