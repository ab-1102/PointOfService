# Point of Service (POS) System

A comprehensive Point of Service (POS) application built for **SOL Bites**, a modern restaurant/cafe. This system manages billing, inventory, customer transactions, and provides detailed analytics and reporting.

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Dependencies](#dependencies)
- [Architecture](#architecture)
- [Configuration](#configuration)

## ✨ Features

### Core Functionality

- **Billing System**: Fast and efficient bill processing with customer details tracking
- **Inventory Management**: Real-time inventory tracking with stock alerts
- **Product Catalog**: Categorized product management with pricing and cost tracking
- **Customer Management**: Store customer names and contact information for transactions
- **Payment Methods**: Support for multiple payment options (Cash, Card, Digital Payment, etc.)

### Reporting & Analytics

- Daily revenue trends analysis
- Product sales volume tracking
- Category-wise revenue analysis
- Profit and loss analysis
- Inventory movement tracking
- Category revenue trends
- Interactive graphs and visualizations

### Printing & Receipts

- Thermal receipt printer integration (Rugtek RP326)
- Professional bill printing with:
  - Customer details
  - Itemized purchase list
  - Total amount and payment method
  - Company branding and contact information
- Kitchen token printing for food preparation tracking
- Barcode and QR code support

### User Interface

- Full-screen PyQt6 GUI with dark theme
- Multiple tabs: Billing, Inventory, Analytics
- Quick product selection from categories
- Real-time bill updates
- Inventory editing and product addition

## 📁 Project Structure

```
PointOfService/
├── main.py                    # Application entry point
├── gui.py                     # PyQt6 GUI implementation (654 lines)
├── dbms.py                    # SQLite database management (612 lines)
├── BillMaker.py              # Bill processing and management
├── pos.py                     # Thermal printer integration
├── config.json                # Runtime configuration (database path, printer name)
├── pos.ui                     # Main UI layout (PyQt6 Designer)
├── productEditPopup.ui       # Product edit dialog layout
├── productAddPopup.ui        # Product add dialog layout
├── logo.png                   # Company logo for receipts
├── mPos.db                    # Default SQLite database file (created automatically)
├── data.csv                   # Product/transaction data
├── requirements.txt           # Python package dependencies
└── test.py                    # Testing utilities
```

## 🔧 Installation

### Prerequisites

- Python 3.8 or higher
- Windows OS (for thermal printer support)
- Receipt printer (Rugtek RP326 recommended)

### Steps

1. **Clone or download the project**

   ```bash
   cd D:\doc\PycharmProjects\PointOfService
   ```

2. **Create a virtual environment** (recommended)

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**

   ```bash
   python main.py
   ```

## 🚀 Usage

### Starting the Application

```bash
python main.py
```

The application will:
- Initialize the SQLite database if it doesn't exist
- Load all products from the database
- Display the main GUI in full-screen mode
- Connect all UI components and signals

### Main Operations

#### Billing Tab
1. Select products from categories
2. Products are added to the current bill
3. Adjust quantities using increase/decrease buttons
4. Enter customer details (name, phone number)
5. Choose payment method
6. Click "Pay" to finalize and print receipt
7. Bill is saved to database

#### Inventory Tab
1. View all products and their stock levels
2. Click on a product to edit details
3. Update product name, price, cost, category, or stock
4. Click "Add New Product" to create new items
5. Changes are immediately reflected

#### Analytics Tab
1. View multiple charts showing:
   - Daily revenue trends
   - Product sales volumes
   - Category revenue breakdown
   - Profit analysis
   - Inventory movement
   - Category trends over time

### Database Operations

The system automatically handles:
- Product inventory management
- Bill history tracking
- Customer transaction records
- Stock change logs with timestamps
- Payment method tracking

## 📦 Dependencies

Key dependencies include:

```
PyQt6==6.11.0              # GUI Framework
PyQt6-Qt6==6.11.1
PyQt6_sip==13.11.1
matplotlib==3.11.0         # Data visualization
numpy==2.5.0              # Numerical computing
python-barcode==0.16.1    # Barcode generation
qrcode==8.2               # QR code generation
python-escpos==3.1        # Thermal printer control
Pillow==12.2.0            # Image processing
pywin32==312              # Windows API integration
PyYAML==6.0.3             # Configuration files
```

For a complete list, see `requirements.txt`.

## 🏗️ Architecture

### Database Schema

#### Inventory Table
- `id`: Product ID (Primary Key)
- `product_name`: Product name
- `barcode`: Product barcode
- `category`: Product category
- `cost_price`: Purchase cost
- `sales_price`: Selling price
- `stock`: Current stock quantity

#### Bills Table
- `bill_id`: Bill ID (Primary Key)
- `customer_name`: Customer name
- `phone_no`: Customer phone number
- `datetime`: Transaction timestamp
- `amount`: Bill total
- `payment_method`: Payment type
- `status`: Transaction status

#### Bill Items Table
- `id`: Item ID (Primary Key)
- `bill_id`: Reference to Bills
- `product_id`: Reference to Inventory
- `product_name`: Product name (denormalized)
- `quantity`: Quantity sold
- `unit_price`: Price per unit
- `total_price`: Line total

#### Inventory Logs Table
- `id`: Log ID (Primary Key)
- `item_id`: Product reference
- `delta`: Stock change amount
- `final_stock`: Stock after change
- `date`: Change timestamp
- `reason`: Reason for change

### Module Overview

**gui.py**: PyQt6 GUI implementation
- `GUI` class: Main window with tabs for Billing, Inventory, Analytics
- `ProductEditPopup` class: Dialog for editing products
- `ProductAddPopup` class: Dialog for adding new products
- Integrated matplotlib canvas for analytics graphs

**dbms.py**: SQLite Database Management System
- `POSDatabase` class: Handles all database operations
- CRUD operations for products, bills, and inventory
- Analytics query methods
- Database triggers for automatic logging

**BillMaker.py**: Bill Processing
- `Bill` class: Manages cart operations
- Add/remove products
- Calculate totals
- Generate formatted output for printing

**pos.py**: Thermal Printer Integration
- `Printer` class: Interfacing with Rugtek RP326 printer
- Format and print bills
- Print kitchen tokens
- Image and barcode printing support

**main.py**: Application Entry Point
- Initializes database and GUI
- Connects signals and slots
- Manages application state and refresh cycles
- Handles bill finalization

## ⚙️ Configuration

### Configuration (config.json + GUI)

This project now supports a small JSON configuration file and an in-app configuration panel. The application will read `config.json` at startup (from the application directory) and apply the settings. The two primary configuration keys are:

- `database_path` — path to the SQLite database file used by the application (overrides the built-in default `mPos.db`).
- `printer_name` — the name of the thermal printer to use (overrides the built-in default printer name).

Example `config.json`:

```json
{
    "database_path": "D:\\doc\\PycharmProjects\\PointOfService\\mPos.db",
    "printer_name": "Rugtek RP326"
}
```

Behavior:

- `main.py` loads `config.json` at startup and, if provided, sets `dbms.DB_LOC` to `database_path` and `BillMaker.PRINTER_NAME` to `printer_name` before initializing the database and GUI.
- The GUI exposes a configuration panel (the main window calls `app.set_config(...)` and emits `config_update` events). When configuration is changed in the UI, `main.py` saves updates back to `config.json` so changes persist across restarts.

Defaults:

- Database: `mPos.db` (created in the application directory by default — the path is `dbms.DB_LOC` in code and defaults to the packaged resource path)
- Printer: `Rugtek RP326` (default set in `BillMaker.PRINTER_NAME` and pushed to the `pos` module)

To change settings manually, edit `config.json` or use the application's configuration dialog (if available). To change the printer programmatically, adjust `PRINTER_NAME` in `BillMaker.py` or update the `printer_name` key in `config.json`.

### Receipt Format

Customize receipt content in `pos.py`:
- Shop name and address (lines ~40-47 in `pos.py`)
- Logo image path (near the top of `pos.py`, usually `logo.png` in the project root)
- Line width and printer profile settings (in `pos.py` where the printer profile is configured)

### Database Location

By default, the application uses `mPos.db` in the application directory (the variable `DB_LOC` in `dbms.py`). To use a different database, either set `database_path` in `config.json` or update `dbms.DB_LOC` in the code.

## 📊 Key Features Explained

### Real-time Inventory Tracking
- Stock updates automatically when bills are processed
- Inventory logs track all changes with timestamps and reasons
- Stock alerts can be configured

### Multi-tab Interface
1. **Billing Tab**: Fast checkout interface
2. **Inventory Tab**: Product and stock management
3. **Analytics Tab**: Business intelligence and reporting

### Receipt Printing
- Professional thermal receipt printing
- Itemized bill with pricing breakdown
- Kitchen token for order preparation
- Customer information for record-keeping

### Data Persistence
- All transactions saved to SQLite database
- Inventory changes logged with timestamps
- Complete bill history for auditing
- Easy data export through CSV

## 🐛 Troubleshooting

 - **Printer not found**: Ensure the printer is installed and the configured name matches. Check `config.json` -> `printer_name`, or `PRINTER_NAME` in `BillMaker.py` / `pos.py`.
 - **Database locked**: Close all other instances of the application. Verify `config.json` -> `database_path` points to the correct database file (default: `mPos.db`).
 - **GUI display issues**: Update PyQt6 packages
 - **Missing logo**: Ensure `logo.png` is in the application directory

## 📝 License

This project is created for SOL Bites restaurant operations.

## 👥 Support

For issues or questions, refer to the inline code documentation or contact the development team.

---

**Version**: 1.0  
**Last Updated**: July 2026  
**Application**: SOL Bites Point of Service System

