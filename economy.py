from db import DatabaseConnection
from users import UsersManagement
from sql_stmt import SQLStatements as sql
import economy_exceptions as exc
import psycopg2.errors


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


    # Create empty receipt
    def _create_empty_receipt(self, user_id, description=None, date=None, commit=False):
        cur = self.conn.cursor()
        #cur.execute(sql.set_user_timezone, (user_id,))
        try:
            cur.execute(
                sql.create_receipt,
                {
                    "user_id": user_id,
                    "description": description,
                    "date": date
                }
            )
            if commit:
                self.conn.commit()
            # SQL Stmt returns id
            return cur.fetchone()["receipt_id"]
        
        except psycopg2.errors.DatetimeFieldOverflow:
            self.conn.rollback()
            raise exc.IncorrectTime(date)
    

    def create_receipt(self, user_id, items, description=None, date=None):
        # Create an empty receipt and get the id of it
        cur = self.conn.cursor()
        receipt_id = self._create_empty_receipt(user_id, description, date)

        for item in items:
            item.update({"receipt_id": receipt_id})

        try:
            cur.executemany(sql.insert_items, items)
            self.conn.commit()
            
            return receipt_id

        except psycopg2.errors.UniqueViolation as e:
            self.conn.rollback()
            raise exc.DuplicateItems(e.pgerror)

    
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
            self.conn.commit()
            # SQL Stmt returns id
            return cur.fetchone()["category_id"]

        except psycopg2.errors.UniqueViolation:
            self.conn.rollback()
            raise exc.CategoryAlreadyExists(name)