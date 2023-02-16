import mysql.connector as conn
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
streamHandler = logging.StreamHandler()
format = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s',datefmt='%d-%b-%y %H:%M:%S')
streamHandler.setFormatter(format)
logger.addHandler(streamHandler)


class Mysqlconnecter():
    def __init__(self,user,passwd,host='localhost',port='3306'):
        self.user = user
        self.passwd = passwd
        self.host = host
        self.port = port
        
    def connector(self): 
        try:   
            logger.info('creating connector')
            mysql = conn.connect(host=self.host,user=self.user,passwd=self.passwd,port=self.port)
            logger.debug('created connection successfully : {}'.format(mysql))
            return mysql
        except Exception as e:
            logger.error('connection failed : {}'.format(e))
            return e
