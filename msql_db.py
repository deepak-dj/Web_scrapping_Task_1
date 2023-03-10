import mysqlconnection as msql
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
streamHandler = logging.StreamHandler()
format = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s',datefmt='%d-%b-%y %H:%M:%S')
streamHandler.setFormatter(format)
logger.addHandler(streamHandler)


class DbOperation():
    def __init__(self,user,passwd,host='localhost',port='3306'):
        self.user = user
        self.passwd= passwd
        self.host=host
        self.port = port
        self.connectr = msql.Mysqlconnecter(self.user,self.passwd,self.host,self.port)
        self.mysql = self.connectr.connector()
        self.cursor = self.mysql.cursor()

    def create_database(self):
        try:
            self.cursor.execute('show databases')
            logger.info('showing databases')
            databases = self.cursor.fetchall()
            dbs_collection = [i[0] for i in databases]
            if not 'ineuron_courses' in dbs_collection:
                logger.info('database doesnot exits, so creating the database "ineuronCourses"') 
                self.cursor.execute('create database ineuronCourses')
            logger.debug('database "ineuronCourses" created successfully')    
            return databases 
        except Exception as e:
            logger.error('unable to create database : {}'.format(e))
            return e
            

    def create_table(self):
        try:
            self.cursor.execute('use ineuronCourses')
            self.cursor.execute('show tables')
            tables = self.cursor.fetchall()
            logger.info('showing tables inside database : {}'.format(tables))
            if len(tables)==0:
                logger.info('no table present inside database, creating "courses" table.')
                self.cursor.execute('''create table ineuronCourses.courses 
                            (name VARCHAR(255) NOT NULL,
                                description  TEXT NOT NULL )'''
                                )
            elif 'courses' not in tables:
                logger.info('"courses" table doesnot exits inside database, creating "courses" table ')
                self.cursor.execute('''create table ineuronCourses.courses 
                            (name VARCHAR(255) NOT NULL,
                            description  TEXT NOT NULL )'''
                            )
                
            logger.debug('table "courses" created successfully.')    
            return tables
        except Exception as e:
            logger.error('unable to create table courses : {}'.format(e))
            return e

    def insert_data(self,name,description):
        try:
            logger.info('inserting data inside database')
            self.cursor.execute('''insert into ineuronCourses.courses values("{}","{}")'''.format(name,description.replace('"',"'")))
            logger.debug('inserted data successfully inside "courses" table')
            return self.mysql.commit()
        except Exception as e:
            logger.error('unable to insert data inside table "courses" : {}'.format(e))
    
    
    def get_data(self):
        self.cursor.execute('''select * from ineuronCourses.courses''')
        data = self.cursor.fetchall()
        return data
    
    def drop_table(self):
        try:
          self.cursor.execute('drop table ineuronCourses.courses') 
          return self.mysql.commit()
        except Exception as e:
            logger.error('unable to drop data {}'.format(e))
            return e
        
        

