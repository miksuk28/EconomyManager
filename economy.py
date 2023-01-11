from db import DatabaseConnection
from users import UsersManagement
from sql_stmt import SQLStatements as sql

class EconomyManager(DatabaseConnection):
    def __init__(self):
        DatabaseConnection.__init__(self)


    def get_receipts(self, user_id):
        cur = self.conn.cursor()
        cur.execute(sql.get_receipts, {"user_id": user_id})
        receipts = self._list_and_dictify(cur.fetchall())

        return receipts


    def get_receipt_items(self, user_id, receipt_id):
        cur = self.conn.cursor()
        cur.execute(sql.get_receipt_items, 
            {"user_id": user_id, "receipt_id": receipt_id}
        )
        items = self._list_and_dictify(cur.fetchall())

        return items


    # Adding items
    def _create_empty_receipt(self, user_id, date):
        cur = self.conn.cursor()
        cur.execute(sql.set_user_timezone, user_id)
        cur.execute(
            sql.create_receipt,
            {
                "user_id": user_id,
                "date": date
            }
        )

    
    def get_categories(self, user_id):
        cur = self.conn.cursor()
        cur.execute(sql.get_categories, {"user_id": user_id})

        categories = self._list_and_dictify(cur.fetchall())

        return categories


    def add_category(self, user_id, name):
        cur = self.conn.cursor()
        try:
            cur.execute(
                sql.add_category,
                {
                    "category_name": name,
                    "user_id":       user_id
                }
            )
            return cur.lastrowid

        except psycopg2.errors.UniqueViolation:
            raise exc.ReceiptAlreadyExists(name)