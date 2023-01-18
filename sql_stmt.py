class SQLStatements:
    #### User Management ####
    #Get user timezone
    get_user_timezone = '''
        SELECT timezone
        FROM users
        WHERE user_id=%s
    '''

    # Set timezone for user
    set_user_timezone = '''
        SET TIME ZONE (SELECT timezone FROM users WHERE user_id=%s)
    '''

    get_user_credentials = '''
        SELECT user_id, username, password_hash, salt, timezone
        FROM users
        WHERE username=%(username)s
    '''
    # Used by UserManagement.authenticate to get token
    get_user_by_token = '''
        SELECT u.user_id, username, expiration, timezone
        FROM sessions s
        LEFT JOIN users u ON s.user_id = u.user_id
        WHERE expiration > now() AND token=%(token)s
    '''

    register_user_token = '''
        INSERT INTO sessions (user_id, token)
        VALUES (%(user_id)s, %(token)s)
    '''

    delete_all_users_sessions = '''
        DELETE FROM sessions
        WHERE user_id=%(user_id)s
    '''

    delete_single_session = '''
        DELETE FROM sessions
        WHERE user_id=%(user_id)s AND token=%(token)s
    '''

    delete_all_sessions = '''
        TRUNCATE sessions
    '''

    #### Receipts ####
    get_receipts = '''
        SELECT r.receipt_id, r.description, SUM(i.quantity) AS total_items, COUNT(i.item_id) AS unique_items, SUM(i.price * i.quantity) AS total, r.date, COUNT(f.file_id) AS files
        FROM items i
        LEFT JOIN receipts r ON r.receipt_id = i.receipt_id
        LEFT JOIN files f ON f.receipt_id = r.receipt_id
        WHERE r.user_id = %(user_id)s
        GROUP BY r.receipt_id
        ORDER BY r.receipt_id DESC
    '''

    get_receipt_info = '''
        SELECT r.receipt_id, r.description, SUM(i.quantity) AS total_items, COUNT(i.item_id) AS unique_items, SUM(i.price * i.quantity) AS total, r.date, COUNT(f.file_id) AS files
        FROM items i
        LEFT JOIN receipts r ON r.receipt_id = i.receipt_id
        LEFT JOIN files f ON f.receipt_id = r.receipt_id
        WHERE r.user_id = %(user_id)s AND r.receipt_id = %(receipt_id)s
        GROUP BY r.receipt_id
    '''

    get_receipt_items = '''
        SELECT i.item_id, i.name, c.category_name AS category, price, quantity, (price * quantity) AS sum
        FROM items i
        LEFT JOIN categories c ON i.category_id = c.category_id
        LEFT JOIN receipts r ON i.receipt_id = r.receipt_id
        WHERE r.user_id=%(user_id)s AND i.receipt_id=%(receipt_id)s
    '''

    get_receipt_files = '''
        SELECT f.file_id, f.file_name, f.name_on_disk, pg_size_pretty(f.size_bytes) AS size, f.size_bytes
        FROM files f
        LEFT JOIN receipts r ON r.receipt_id = f.receipt_id
        LEFT JOIN users u ON r.user_id = u.user_id
        WHERE f.receipt_id=%(receipt_id)s AND r.user_id=%(user_id)s
    '''

    create_receipt = '''
        INSERT INTO receipts (user_id, description, date)
        VALUES (%(user_id)s, %(description)s, %(date)s)
        RETURNING receipt_id
    '''

    insert_items = '''
        INSERT INTO items (receipt_id, name, price, quantity, category_id)
        VALUES (%(receipt_id)s, %(name)s, %(price)s, %(quantity)s, %(category_id)s)
    '''

    #### Categories ####
    # Add category for user
    add_category = '''
        INSERT INTO categories (category_name, user_id)
        VALUES (%(category_name)s, %(user_id)s)
        RETURNING category_id
    '''

    # Get categories for user
    get_categories = '''
        SELECT category_id, category_name
        FROM categories
        WHERE user_id = %(user_id)s
    '''