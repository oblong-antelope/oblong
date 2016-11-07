import pg

import os
import psycopg2
import urlparse

urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(os.environ["DATABASE_URL"])

class DBm:

    _create_table = "CREATE TABLE"
    _primary_key = "PRIMARY KEY"
    _from = "FROM"
    _where = "WHERE"
    _and = "AND"
    _select = "SELECT"
    _insert_into = "INSERT INTO"
    _values = "VALUES"
    _update = "UPDATE"
    _set = "SET"
    _empty = ""
    _space = " "
    _equal = "="
    _semi_colon = ";"
    _comma = ","
    _left_p = "("
    _right_p = ")"
    _format_3 = "%s%s%s"
    _format_4 = "%s%s%s%s"
    _format_5 = "%s%s%s%s%s"
    _format_6 = "%s%s%s%s%s%s"
    _format_7 = "%s%s%s%s%s%s%s"
    _format_8 = "%s%s%s%s%s%s%s%s"
    _format_9 = "%s%s%s%s%s%s%s%s%s"
    _format_15 = "%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s"

    def __init__(self):
        self._database = psycopg2.connect(
    		database=url.path[1:],
    		user=url.username,
    		password=url.password,
    		host=url.hostname,
    		port=url.port)

        self.dbname = url.path[1:]
        self.host = url.hostname
        self.port = url.port
        self.user = url.username
        self.passwd = url.password
        self.isOpen = True

    def close(self, query):
        self._database.close()
        self.isOpen = False

    def _query(self, query):
        return (self._database.query(query)).dictresult()

    def _update(self, query):
        self._database.query(query)

    def create_table(self, name, cols, primary=[]):
        """name is a string name of the table
        cols is a list of pairs of strings (attribute, type)
            e.g. [("name", "text"), ("age", "integer")]
        primary is a list of strngs, denotes the primary key
            e.g. ["name"]"""
        cmd = DBm._format_4 % (DBm._create_table,
                               DBm._space,
                               name,
                               DBm._left_p)
        l1 = len(cols)
        l2 = len(primary)
        count = 0
        for (col, t) in cols:
            if (l2 > 0 or count < l1 - 1):
                cmd = DBm._format_6 % (cmd,
                                       DBm._space,
                                       col,
                                       DBm._space,
                                       t,
                                       DBm._comma)
                count += 1
            else:
                cmd = DBm._format_5 % (cmd,
                                       DBm._space,
                                       col,
                                       DBm._space,
                                       t)
        if (l2 > 0):
            cmd = DBm._format_4 % (cmd,
                                   DBm._space,
                                   DBm._primary_key,
                                   DBm._left_p)
            count = 0
            for k in primary:
                if (count < l2 - 1):
                    cmd = DBm._format_4 % (cmd,
                                           DBm._space,
                                           k,
                                           DBm._comma)
                    count += 1
                else:
                    cmd = DBm._format_5 % (cmd,
                                           DBm._space,
                                           k,
                                           DBm._space,
                                           DBm._right_p)
        cmd = DBm._format_4 % (cmd,
                               DBm._space,
                               DBm._right_p,
                               DBm._semi_colon)
        cols_name, cols_type = zip(*cols)
        self.cols_name = cols_name
        self.cols_type = cols_type
        self.tname = name
        self.no_cols = len(cols)
        self.primary = primary
        self._update(cmd)
        
    def _where_cond(self, conds):
        l = len(conds)
        cmd = DBm._where
        count = 0
        for cond in conds:
            if (count < l - 1):
                cmd = DBm._format_5 % (cmd,
                                      DBm._space,
                                      cond,
                                      DBm._space,
                                      DBm._and)
                count += 1
            else:
                cmd = DBm._format_3 % (cmd,
                                       DBm._space,
                                       cond)
        return cmd
        
    def _gen_list(self, cols):
        l = len(cols)
        cmd = DBm._empty
        count = 0
        for col in cols:
            if (count < l - 1):
                cmd = DBm._format_4 % (cmd,
                                       DBm._space,
                                       col,
                                       DBm._comma)
                count += 1
            else:
                cmd = DBm._format_3 % (cmd,
                                       DBm._space,
                                       col)
        return cmd
        
        
    def search(self, conds):
        """conds is a list of strings, denotes the conds for filter
        format: attribut=value, attribute>value etc.
            e.g. ["name = \"john\"", "age > 36"]
        returns a list of dictionaries, each one is a row in the
        database"""
        cmd = DBm._format_9 % (DBm._select,
                               self._gen_list(self.cols_name),
                               DBm._space,
                               DBm._from,
                               DBm._space,
                               self.tname,
                               DBm._space,
                               self._where_cond(conds),
                               DBm._semi_colon)
        return self._query(cmd)
        
    def insert(self, values):
        """values is a list of string, must provide value for each column
        in the table, values must be passed in the correct order
            e.g. ["Marry", "32"]"""
        cmd = DBm._format_15 % (DBm._insert_into,
                                DBm._space,
                                self.tname,
                                DBm._space,
                                DBm._left_p,
                                self._gen_list(self.cols_name),
                                DBm._space,
                                DBm._right_p,
                                DBm._space,
                                DBm._values,
                                DBm._left_p,
                                self._gen_list(values),
                                DBm._space,
                                DBm._right_p,
                                DBm._semi_colon)
        
        self._update(cmd)
        
    def _gen_pair_assign_list(self, cols_values):
        l = len(cols_values)
        cmd = DBm._empty
        count = 0
        for (col, value) in cols_values:
            if (count < l - 1):
                cmd = DBm._format_8 % (cmd,
                                       DBm._space,
                                       col,
                                       DBm._space,
                                       DBm._equal,
                                       DBm._space,
                                       value,
                                       DBm._comma)
                count += 1
            else:
                cmd = DBm._format_7 % (cmd,
                                       DBm._space,
                                       col,
                                       DBm._space,
                                       DBm._equal,
                                       DBm._space,
                                       value)
        return cmd
        
    def update(self, cols_values, conds):
        """cols_values is a list of pairs of strings
        format: (attribute, value)
           e.g. [("name", "\"john\""), ("age", "30")]
        conds is the same as in search"""
        cmd = DBm._format_9 % (DBm._update,
                               DBm._space,
                               self.tname,
                               DBm._space,
                               DBm._set,
                               self._gen_pair_assign_list(cols_values),
                               DBm._space,
                               self._where_cond(conds),
                               DBm._semi_colon)
        self._update(cmd)


    
