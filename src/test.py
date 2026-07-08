import dbms
db = dbms.POSDatabase()
#db.import_inventory_from_csv("data.csv")
#print(db.get_products_by_category())

for a in db.get_all_products()[2]:
    print(a, ' - ', type(a))