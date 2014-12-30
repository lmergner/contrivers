#-*- coding: utf-8 -*-

import os

db_user = os.environ.get('TESTING_DB_USER', 'contrivers')
db_name = os.environ.get('TESTING_DB_NAME', 'contrivers-testing')

testing_db_url = 'postgres://' + db_user + '@localhost/' + db_name

