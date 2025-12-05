from django.db import connection; cursor = connection.cursor(); cursor.execute('DROP TABLE IF EXISTS waitlist_waitlist CASCADE;'); print("Waitlist table deleted!") 
