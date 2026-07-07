import dbms
db = dbms.POSDatabase()
#db.import_inventory_from_csv("data.csv")
print(db.fetch_bill_log())
print(db.fetch_all_bill_items()[5])