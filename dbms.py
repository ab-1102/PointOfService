import sqlite3
from datetime import datetime, timedelta
from typing import List, Any, Dict, Tuple, Optional
import csv
import os
import sys
def resource_path(relative_path):
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

DB_LOC = resource_path("mPos.db")



class POSDatabase:
    def __init__(self):
        self.conn = sqlite3.connect(DB_LOC)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.create_trigger()

    # --------------------------
    # CREATE TABLES
    # --------------------------
    def create_tables(self):

        # Inventory Table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            barcode TEXT UNIQUE,
            category TEXT,
            cost_price REAL NOT NULL,
            sales_price REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0
        )
        """)

        # Bills Table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS bills (
            bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            phone_no TEXT,
            datetime TEXT NOT NULL,
            amount REAL NOT NULL,
            payment_method TEXT NOT NULL,
            status TEXT DEFAULT 'PAID'
        )
        """)

        # Bill Items Table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS bill_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            total_price REAL NOT NULL,
            FOREIGN KEY (bill_id) REFERENCES bills(bill_id),
            FOREIGN KEY (product_id) REFERENCES inventory(id)
        )
        """)

        # Inventory Log Table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            delta INTEGER NOT NULL,
            final_stock INTEGER NOT NULL,
            date TEXT NOT NULL,
            reason TEXT NOT NULL
        )
        """)

        self.conn.commit()

    # --------------------------
    # TRIGGER
    # --------------------------
    def create_trigger(self):
        self.cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS stock_update_trigger
        AFTER UPDATE OF stock ON inventory
        BEGIN
            INSERT INTO inventory_logs (
                item_id,
                delta,
                final_stock,
                date,
                reason
            )
            VALUES (
                NEW.id,
                NEW.stock - OLD.stock,
                NEW.stock,
                DATETIME('now'),
                'Stock Updated'
            );
        END;
        """)
        self.conn.commit()

    # --------------------------
    # GET ALL UNIQUE CATEGORIES
    # Returns:
    # ["Drinks", "Snacks", "Dairy"]
    # --------------------------
    def get_all_categories(self) -> List[str]:
        self.cursor.execute("""
        SELECT DISTINCT category
        FROM inventory
        ORDER BY category ASC
        """)

        rows: list[tuple[str]] = self.cursor.fetchall()

        return [row[0] for row in rows]

    # --------------------------
    # GET ALL PRODUCTS
    # Returns:
    # [
    #   [id, product_name, barcode, category, cost_price, sales_price, stock],
    #   [...]
    # ]
    # --------------------------
    def get_all_products(self) -> List[List[Any]]:
        self.cursor.execute("""
        SELECT * FROM inventory
        """)

        rows: list[tuple] = self.cursor.fetchall()

        return [list(row) for row in rows]

    # --------------------------
    # GET ALL PRODUCT IDS
    # --------------------------
    def get_all_product_ids(self):
        self.cursor.execute("""
        SELECT id FROM inventory
        """)
        return [row[0] for row in self.cursor.fetchall()]

    # --------------------------
    # GET ALL BILL IDS
    # --------------------------
    def get_all_bill_ids(self):
        self.cursor.execute("""
        SELECT bill_id FROM bills
        """)
        return [row[0] for row in self.cursor.fetchall()]

    # --------------------------
    # FETCH PRODUCT
    # --------------------------
    def fetch_product(self, product_id=None, barcode=None):

        if product_id:
            self.cursor.execute(
                "SELECT * FROM inventory WHERE id = ?",
                (product_id,)
            )

        elif barcode:
            self.cursor.execute(
                "SELECT * FROM inventory WHERE barcode = ?",
                (barcode,)
            )

        return self.cursor.fetchone()

    # --------------------------
    # GET PRODUCTS GROUPED BY CATEGORY
    # Returns:
    # {
    #   "Drinks": [
    #       [1, "Coke", "123", "Drinks", 25.0, 40.0, 30],
    #       [2, "Pepsi", "124", "Drinks", 24.0, 38.0, 20]
    #   ],
    #   "Snacks": [
    #       [3, "Chips", "125", "Snacks", 10.0, 20.0, 50]
    #   ]
    # }
    # --------------------------
    def get_products_by_category(self) -> Dict[str, List[List[Any]]]:
        self.cursor.execute("""
        SELECT *
        FROM inventory
        ORDER BY category, product_name
        """)

        rows: list[tuple] = self.cursor.fetchall()

        products_by_category: Dict[str, List[List[Any]]] = {}

        for row in rows:
            product: List[Any] = list(row)
            category: str = product[3]

            if category not in products_by_category:
                products_by_category[category] = []

            products_by_category[category].append(product)

        return products_by_category

    # --------------------------
    # ADD PRODUCT
    # --------------------------
    def add_product(self, data):
        self.cursor.execute("""
        INSERT INTO inventory (
            product_name,
            barcode,
            category,
            cost_price,
            sales_price,
            stock
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """, (data[0], data[1], data[2], data[3], data[4], data[5]))

        self.conn.commit()

    # --------------------------
    # EDIT PRODUCT
    # --------------------------
    def edit_product(self, product):
        self.cursor.execute("""
        UPDATE inventory
        SET
            product_name = ?,
            barcode = ?,
            category = ?,
            cost_price = ?,
            sales_price = ?,
            stock = ?
        WHERE id = ?
        """, (product[1], product[2], product[3], product[4], product[5], product[6], product[0]))
        self.conn.commit()

    # --------------------------
    # RESTOCK / REMOVE
    # --------------------------
    def update_stock(self, product_id, delta):
        self.cursor.execute("""
        UPDATE inventory
        SET stock = stock + ?
        WHERE id = ?
        """, (delta, product_id))

        self.conn.commit()

    # bill_items format:
    # [
    #   (
    #       (id, name, barcode, category, cost_price, selling_price, stock),
    #       quantity,
    #       line_total
    #   )
    # ]

    def add_bill(
            self,
            bill_items: List[Tuple[Tuple[Any, ...], int, float]],
            total_amount: float,
            customer_name: str = "Walk-in",
            phone_number: str = "",
            payment_method: str = ""
    ) -> None:

        now: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Add bill
        self.cursor.execute("""
        INSERT INTO bills (
            customer_name,
            phone_no,
            datetime,
            amount,
            payment_method
        )
        VALUES (?, ?, ?, ?, ?)
        """, (customer_name, phone_number, now, total_amount, payment_method))

        bill_id: int = self.cursor.lastrowid

        # Add bill items
        for product, quantity, line_total in bill_items:
            product_id: int = product[0]
            product_name: str = product[1]
            unit_price: float = product[5]  # selling price

            self.cursor.execute("""
            INSERT INTO bill_items (
                bill_id,
                product_id,
                product_name,
                quantity,
                unit_price,
                total_price
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                bill_id,
                product_id,
                product_name,
                quantity,
                unit_price,
                line_total
            ))

            # Reduce stock
            self.cursor.execute("""
            UPDATE inventory
            SET stock = stock - ?
            WHERE id = ?
            """, (
                quantity,
                product_id
            ))

        self.conn.commit()


    # --------------------------
    # FETCH BILL LOG
    # --------------------------
    def fetch_bill_log(self):
        self.cursor.execute("SELECT * FROM bills")
        return self.cursor.fetchall()

    # --------------------------
    # FETCH SINGLE BILL ITEMS
    # --------------------------
    def fetch_bill_items(self, bill_id):
        self.cursor.execute("""
        SELECT * FROM bill_items
        WHERE bill_id = ?
        """, (bill_id,))
        return self.cursor.fetchall()

    # --------------------------
    # FETCH ALL BILL ITEMS
    # Returns:
    # {
    #   bill_id: [
    #       [id, bill_id, product_id, product_name, quantity, unit_price, total_price],
    #       ...
    #   ]
    # }
    # --------------------------
    def fetch_all_bill_items(self) -> Dict[int, List[List[Any]]]:
        self.cursor.execute("""
        SELECT *
        FROM bill_items
        ORDER BY bill_id
        """)

        rows: list[tuple] = self.cursor.fetchall()

        bills: Dict[int, List[List[Any]]] = {}

        for row in rows:
            item: List[Any] = list(row)
            bill_id: int = item[1]

            if bill_id not in bills:
                bills[bill_id] = []

            bills[bill_id].append(item)

        return bills

    # --------------------------
    # RESET INVENTORY FROM CSV
    # CSV Header:
    # Product Name, Barcode, Category, Cost Price, Selling Price, Stock
    # --------------------------
    def import_inventory_from_csv(self, file_path: str) -> None:
        # Clear existing inventory
        self.cursor.execute("DELETE FROM inventory")

        with open(file_path, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                self.cursor.execute("""
                INSERT INTO inventory (
                    product_name,
                    barcode,
                    category,
                    cost_price,
                    sales_price,
                    stock
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    row["Product Name"].strip(),
                    row["Barcode"].strip(),
                    row["Category"].strip().title(),
                    float(row["Cost Price"]),
                    float(row["Selling Price"]),
                    int(row["Stock"])
                ))

        self.conn.commit()


    # x, y = db.get_daily_revenue_trend()
    # plt.plot(x, y)
    # ---------------------------
    def get_daily_revenue_trend(self) -> Tuple[List[str], List[float]]:
        self.cursor.execute("""
        SELECT DATE(datetime), SUM(amount)
        FROM bills
        GROUP BY DATE(datetime)
        ORDER BY DATE(datetime)
        """)

        rows: list[tuple] = self.cursor.fetchall()

        if not rows:
            return [], []

        revenue_map = {
            row[0]: row[1]
            for row in rows
        }

        start_date = datetime.strptime(rows[0][0], "%Y-%m-%d")
        end_date = datetime.strptime(rows[-1][0], "%Y-%m-%d")

        dates: List[str] = []
        revenue: List[float] = []

        current = start_date
        while current <= end_date:
            date_str = current.strftime("%Y-%m-%d")
            dates.append(date_str)
            revenue.append(revenue_map.get(date_str, 0.0))
            current += timedelta(days=1)

        return dates, revenue

    # x, y = db.get_product_sales_volume()
    # plt.bar(x, y)
    # --------------------------
    def get_product_sales_volume(self) -> Tuple[List[str], List[int]]:
        self.cursor.execute("""
        SELECT product_name, SUM(quantity)
        FROM bill_items
        GROUP BY product_name
        ORDER BY SUM(quantity) DESC
        """)

        rows: list[tuple] = self.cursor.fetchall()

        products: List[str] = [row[0] for row in rows]
        quantities: List[int] = [row[1] for row in rows]

        return products, quantities

    # x, y = db.get_category_revenue()
    # plt.pie(y, labels=x)
    # --------------------------
    def get_category_revenue(self) -> tuple[list[str], list[float]]:
        self.cursor.execute("""
        SELECT 
            inventory.category,
            COALESCE(SUM(bill_items.total_price), 0)
        FROM inventory
        LEFT JOIN bill_items 
            ON inventory.id = bill_items.product_id
        GROUP BY inventory.category
        ORDER BY inventory.category
        """)

        rows: list[tuple] = self.cursor.fetchall()

        categories: list[str] = [row[0] for row in rows]
        revenue: list[float] = [row[1] for row in rows]

        return categories, revenue

    # x, y = db.get_profit_analysis()
    # plt.plot(x, y)
    # --------------------------
    def get_profit_analysis(self) -> Tuple[List[str], List[float]]:
        self.cursor.execute("""
        SELECT DATE(bills.datetime),
               SUM((bill_items.unit_price - inventory.cost_price) * bill_items.quantity)
        FROM bill_items
        JOIN inventory ON bill_items.product_id = inventory.id
        JOIN bills ON bill_items.bill_id = bills.bill_id
        GROUP BY DATE(bills.datetime)
        ORDER BY DATE(bills.datetime)
        """)

        rows: list[tuple] = self.cursor.fetchall()

        if not rows:
            return [], []

        profit_map = {
            row[0]: row[1]
            for row in rows
        }

        start_date = datetime.strptime(rows[0][0], "%Y-%m-%d")
        end_date = datetime.strptime(rows[-1][0], "%Y-%m-%d")

        dates: List[str] = []
        profits: List[float] = []

        current = start_date
        while current <= end_date:
            date_str = current.strftime("%Y-%m-%d")
            dates.append(date_str)
            profits.append(profit_map.get(date_str, 0.0))
            current += timedelta(days=1)

        return dates, profits

    # x, y = db.get_inventory_movement()
    # plt.bar(x, y)
    # --------------------------
    def get_inventory_movement(self) -> Tuple[List[str], List[int]]:
        self.cursor.execute("""
        SELECT date, SUM(delta)
        FROM inventory_logs
        GROUP BY DATE(date)
        ORDER BY DATE(date)
        """)

        rows: list[tuple] = self.cursor.fetchall()

        dates: List[str] = [row[0] for row in rows]
        changes: List[int] = [row[1] for row in rows]

        return dates, changes

    # --------------------------
    # CATEGORY REVENUE TREND
    # Returns:
    # (
    #   dates,
    #   {
    #       "Cake": [100, 200, 150],
    #       "Drinks": [50, 0, 90]
    #   }
    # )
    # --------------------------
    def get_category_revenue_trend(self) -> Tuple[List[str], Dict[str, List[float]]]:

        # Get all unique categories from inventory
        self.cursor.execute("""
        SELECT DISTINCT category
        FROM inventory
        ORDER BY category
        """)
        categories: List[str] = [row[0] for row in self.cursor.fetchall()]

        # Get revenue data
        self.cursor.execute("""
        SELECT
            DATE(bills.datetime),
            inventory.category,
            SUM(bill_items.total_price)
        FROM bill_items
        JOIN bills ON bill_items.bill_id = bills.bill_id
        JOIN inventory ON bill_items.product_id = inventory.id
        GROUP BY DATE(bills.datetime), inventory.category
        ORDER BY DATE(bills.datetime), inventory.category
        """)
        rows: list[tuple] = self.cursor.fetchall()

        # Get all dates
        dates: List[str] = sorted(list(set(row[0] for row in rows)))

        # Initialize all categories with 0 for every date
        category_data: Dict[str, List[float]] = {
            category: [0.0] * len(dates)
            for category in categories
        }

        # Map dates to indexes
        date_index: Dict[str, int] = {
            date: idx
            for idx, date in enumerate(dates)
        }

        # Fill actual revenue
        for date, category, revenue in rows:
            category_data[category][date_index[date]] = revenue

        return dates, category_data

    # --------------------------
    # CLOSE DB
    # --------------------------
    def close(self):
        self.conn.close()

