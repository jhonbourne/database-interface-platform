import pymysql
# NOTE: becareful the use of list and tuple in this module.
#      String formatting with %s requires tuple or str but not list.
#      Addtionally, both list() and tuple() will divide a str into letters.

class MySqlHelper:
    def __init__(self, host='localhost', port=3306, user='root', password=None, **sqlargs):
        """A connection to the database should be setted during initialization"""
        if password == None:
            raise ValueError("Password must be given!")
        self.conn = pymysql.connect(host=host, port=3306, user=user, password=password, **sqlargs)
        self.cursor = self.conn.cursor()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def __enter__(self):
        return self
    def __exit__(self, *args):
        self.close()

    def _execute_(self, sql, params=None):
        """Execute a command which alter the database."""
        self.cursor.execute(sql, params or ())
        self.conn.commit()

    def _query_(self, sql, params=None):
        """Execute a command which returns specific data from the database."""
        self.cursor.execute(sql, params or ())
        result = self.cursor.fetchall()
        return result
    
    def create_database(self, db_name):
        self._execute_(
            'create database if not exists %s default charset utf8' % db_name,
                       )
        
    def use_database(self, db_name):
        self.conn.select_db(db_name)

    def show_tables(self):
        return self._query_('show tables')

    def table_info(self, tbl_name):
        return self._query_('desc %s' % tbl_name )
    
    @classmethod
    def Type_Transform(cls, type_list, setting_apd=None):
        type_comm = [''] * len(type_list)
        if not setting_apd:
            setting_apd = [''] * len(type_list)

        for i,typ in enumerate(type_list):
            if typ == str:
                type_comm[i] = 'varchar'
            elif typ == int:
                type_comm[i] = 'int'
            elif typ == float:
                type_comm[i] = 'float'
            elif isinstance(typ, str):
                type_comm[i] = typ
        
        for i,apd in enumerate(setting_apd):
            if isinstance(apd,str):
                if len(apd) > 0 and (not apd[0]=='('):
                    setting_apd[i] = ' ' + apd
            else:
                setting_apd[i] = ''
        
        return list(map(lambda x,y: x+y, type_comm, setting_apd))

    def create_table(self, table_name, column_setting, add_id_col=False, id_name='id'):
        """Create a table in the database.
        
        Args:
            table_name: str
                The name of the table to be created.
            column_setting: dict
                The keys are the names of the columns, the values are the attributes
                of the corresponding columns (should be written in SQL gramma: 
                <datatype> [not null] [default %value] [primary key] [auto_increment]).
            add_id_col: bool, default false
                If true, a column of int would be addtionaly created, setted as 
                a primary key and has auto_increment attribute.
            id_name: str, default 'id'
                The name of the id column when 'add_id_col' is true.
        """
        if not isinstance(column_setting, dict):
            raise ValueError("'column_setting' must be a dictionary")
        
        comm = 'create table if not exists %s (' % table_name

        column_describe = '`%s` int unsigned not null' \
                            ' primary key auto_increment, ' % id_name\
                            if add_id_col else ''
        for name, attr in column_setting.items():
            column_describe += ('`%s` %s, ' % (name, attr))
        column_describe = column_describe[:-2] # remove the ', ' in the end
        
        comm = comm + column_describe + ') default charset=utf8'
        print('Execute command: '+comm)
        self._execute_(comm)

    def delete_table(self, table_name):
        self._execute_('drop table if exists %s' % table_name )

    def insert(self, table_name, column_name, attribute):
        self._execute_('alter table %s add `%s` %s' %
                       (table_name, column_name, attribute))
        
    def drop_column(self, table_name, column_name):
        self._execute_('alter table %s drop column `%s`' % (table_name, column_name))

    def modify_column(self, table_name, column_name, attribute):
        self._execute_('alter table %s modify column `%s` %s' % (table_name, column_name, attribute))

    def append(self, table_name, col_dat_dict=None, column_names=None, values=None):
        """Insert data rows into the specified table.
        
        Args:
            table_name: str
                Name of the table to be manipulated.
            col_dat_dict: dict
                Dictionary of data to be inserted. If used, column_names and values
                would be ignored. Keys are column names, and the values would be 
                inserted into the corresponding column.
            column_names: str or list of str
                Names of columns to be inserted, string for one column, list of string
                for multiple columns. Choose all of the columns by default. Usable
                only if col_dat_dict is None.
            values: list or list of lists
                Values of one ROW (if list) or multiple ROWS (if list of lists) to be 
                inserted. Usable only if col_dat_dict is None.
        """
        # Parameters and command of columns
        if isinstance(col_dat_dict, dict):
            col = tuple(col_dat_dict.keys())
            use_dict = True
        elif column_names == None:
            col = []
            use_dict = False
        elif isinstance(column_names, (list,tuple,str)):
            col = tuple(column_names)
            use_dict = False
        else:
            raise ValueError("Invalid input! Check 'col_dat_dict' or c'olumn_names'.")
        if len(col)>0:
            col_comm = ( '(' + ','.join(['%s']*len(col)) + ')' ) % col
        else:
            col_comm = ''
        
        # Parameters of data values
        if use_dict:
            val_list = list(col_dat_dict.values())
            if all(isinstance(x, (list,tuple)) for x in val_list): # Multiple rows
                vals = tuple(zip(*val_list))
            else: # Single row
                vals = val_list
        else:
            if values == None:
                raise ValueError("Please input 'values' for insert.")
            else:
                vals = values

        if all(isinstance(x, (list,tuple)) for x in vals): # Multiple rows
            val_comm = ','.join(['(' + ','.join(['%s']*len(col)) + ')']*len(vals))
            val_param = tuple(item for sublist in vals for item in sublist)
            num_val_check = all(len(x)==len(col) for x in vals)
        else: # Single row
            val_comm = '(' + ','.join(['%s']*len(col)) + ')'
            val_param = tuple(vals)
            num_val_check = len(vals) == len(col)
        if not num_val_check:
            raise ValueError("Number of data in the rows are not equal to the number of columns.")
        
        comm = ('insert into %s') % table_name + col_comm + ' values ' + val_comm
        self._execute_(comm, val_param)

    def drop_row(self, table_name, where, where_params=()):
        # Condition of row selection
        cond_comm = '' if where=='all' else ' where ' + where

        self._execute_('delete from %s %s' % (table_name, cond_comm), where_params)

    def modify_row_data(self, table_name, col_val_dict, where, where_params=() ):
        """
        Can only set constatnt values here!
        TO DO?: set values by calculation of SQL functions
        """
        # Columns of modification
        set_comm = ','.join(['%s=%s' % (col, '%s') for col in col_val_dict.keys()])
        val_params = tuple(col_val_dict.values())
        # Condition of row selection
        cond_comm = '' if where=='all' else ' where ' + where

        self._execute_(('update %s set ' % table_name)+set_comm+cond_comm
                       , val_params + where_params)

    def get_row_num(self, table_name):
        res =  self._query_('select count(*) from %s' % table_name )
        return res[0][0]
    
    def get_col_num(self, table_name):
        res =  self._query_('show columns from %s' % table_name )
        return len(res)
        
    def select(self, table_name, column_names='*', where='all', where_params = ()
               ,sort_col=None, asc_sort=None, iloc_range=(None,None)):
        """
        Select and return specific part of the table.
        
        TO DO?: group by, join, union, partition by
        Formatting?: where, case when, as

        Args:
            table_name: str
                Name of the table for selection.
            column_names: str or list of str
                Names of columns to be inserted, string for one column, list of string
                for multiple columns. Choose all of the columns by default. ('case...
                when' and 'as' commands could be used here.)
            where: str
                String which contains SQL command of the condition descriptions for
                choosing specific rows.
            sort_col: None (default), str or list of str
                Name of the columns for sorting, applicable when rows of the tables
                need to be sorted. Order of the names represent piority in sorting.
                No sorting command would be applied by default.
            asc_sort: None (default), bool or list of bool
                Whether use ascending order when sorting, applicable when rows of the 
                tables need to be sorted. Only usable when 'sort_col' are setted
                correctly. True for ascending order, False for descending order. Each
                value is corresponding to the name of column in 'sort_col'.
            iloc_range: tuple with 2 elements of int
                Range of the rows selected in the table. Please input in the form of
                (start index, end index). Indexing rules follow those of 'iloc' method
                in Pandas. No truncation by default.

        Returns:
            res: tuple of tulples
                Selected part of table gathered as a tuple, in which each row is
                packed as a tuple.
            columns: list of str
                Name of each column.
        """
        # Parameterization        
        # Columns of selection
        if isinstance(column_names, str):
            column_names = [column_names]
        column_names = tuple(column_names)
        col_comm = ','.join(['%s']*len(column_names)) % column_names
        # Condition of selection
        cond_comm = '' if where=='all' else ' where ' + where
        # Sorting criteria
        if sort_col == None or len(sort_col) == 0:
            sort_comm = ''
            sort_param = []
        elif isinstance(sort_col,(list,tuple)):
            # asc_sort should also be a list/tuple of the same length
            sort_comm = []
            sort_param = []
            for col, is_asc in zip(sort_col, asc_sort):
                sort_comm.append('%s ' + 'asc' if is_asc else 'desc')
                sort_param.append(col)
            sort_comm = ' order by ' + ','.join(sort_comm)
            sort_comm = sort_comm % tuple(sort_param)
        elif isinstance(sort_col,str) and isinstance(asc_sort,bool):
            sort_comm = ' order by %s ' % tuple(sort_col)
            sort_comm += 'asc' if asc_sort else 'desc'
        else:
            raise ValueError("Please use valid input of 'sort_col' or 'asc_sort'.")
        # Truncation of table
        if isinstance(iloc_range, (list,tuple)) and len(iloc_range) == 2:
            # Parameter has been checked, therefore no parameterization of this segment when execute SQL command
            if all(isinstance(x,int) for x in iloc_range) and iloc_range[1]>iloc_range[0]:
                trunc_param = [iloc_range[1]-iloc_range[0],iloc_range[0]]
                trunc_comm = ' limit %s offset %s' % tuple(trunc_param)
            else:
                trunc_comm = ''
                print("Table will not be truncated according to the 'iloc_range' input.")

        comm = 'select '+col_comm+(' from %s ' % table_name) \
                           +cond_comm+sort_comm+trunc_comm
        print('Execute command: '+comm)
        res = self._query_(comm,
                            where_params)
        
        return res, [i[0] for i in self.cursor.description]


if __name__ == '__main__':
    # Test of MySqlHelper
    print("Build up a connection and cursor.")
    dial = MySqlHelper(user='root', password='root')
    print("Create a database 'people', use this database.")
    dial.create_database('people')
    dial.use_database('people')


    print("Table in this database now: ",dial.show_tables())
    print("Create a table 'student':")
    dial.create_table('student',
                  {'name':'varchar(16) not null',
                   'height':'decimal(3,2)'},
                  add_id_col=True)
    print("Column information:",*(dial.table_info('student')), sep='\n')
    print("Table in this database now: ",dial.show_tables())


    print("Insert a new column 'age'.")
    dial.insert('student','age','int')
    print("Column information:",*(dial.table_info('student')), sep='\n')

    print("Delete the column 'age'.")
    dial.drop_column('student','age')
    print("Column information:",*(dial.table_info('student')), sep='\n')

    print("Modify data type of column 'height'.")
    dial.modify_column('student','height','decimal(5,2)')
    print("Column information:",*(dial.table_info('student')), sep='\n')


    print("Insert data to the table.")
    dial.append('student',
            column_names=['name','height'],
            values=[
                ('Jason',172),
                ('Alice',158),
                ('Bob',175.1),
                ('Nick',182),
                ('Mary',173.5),
                ('Tina',167)
            ])
    dat, col = dial.select('student')
    print(col, *dat, sep='\n')

    print("Delete data with height>=180.")
    dial.drop_row('student', where='height >= %s', where_params=(180,))
    dat, col = dial.select('student')
    print(col, *dat, sep='\n')

    print("Modify height of Richard to 180.")
    dial.modify_row_data('student',{'height':180},where='name = %s',where_params=('Richard',))
    dat, col = dial.select('student')
    print(col, *dat, sep='\n')

    print("Get rows of data with height<173, order by height.")
    dat, col = dial.select('student',('name','height'),
                       where='height<%s',where_params=(173,),
                       sort_col='height',asc_sort=True)
    print(col, *dat, sep='\n')


    print("Delete the table 'student'.")
    dial.delete_table('student')
    print("Table in this database now: ",dial.show_tables())

    print("Close the cursor and connection.")
    dial.close()