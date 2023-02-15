from flask import Flask,render_template,request,redirect,url_for
from flask_cors import CORS,cross_origin
import logging
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import json
import pdfkit
import msql_db
import mongo_db


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
streamHandler = logging.StreamHandler()
format = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s',datefmt='%d-%b-%y %H:%M:%S')
streamHandler.setFormatter(format)
logger.addHandler(streamHandler)



application = Flask(__name__)
app = application

try:
    searchstring = 'courses'

    ineuron_url = "https://ineuron.ai/"+searchstring
    logger.info('creating url for the courses in ineuron website : {}'.format(ineuron_url))

    uclient = uReq(ineuron_url)
    ineuron_page = uclient.read()
    uclient.close()
    beutify_course_html = bs(ineuron_page,"html.parser")

    divs = beutify_course_html.find('script',{'id':'__NEXT_DATA__'})
    content = divs.contents
    dict_data = "".join(content)
    cleaned_data = json.loads(dict_data)
    i_neuron_courses = cleaned_data['props']['pageProps']['initialState']['init']['coursesWithOneNeuron']

    logger.info('courses data cleaned successfully.')
except Exception as e:
    logger.error(e)    
@app.route('/',methods=['GET'])
def home():
    try:
        logger.info('viewing all courses in home page')
        return render_template('home.html',i_neuron_courses=i_neuron_courses)
    
    except Exception as e:
        logger.error('unable to load home page : {}'.format(e))
        return e
    
@app.route('/details/<section>',methods=['GET'])
def course_details(section):
    try:
        logger.info('creating details of the course : {}'.format(section))
        section = request.view_args['section']
        desc_json = i_neuron_courses[section]
        description = desc_json['description']
        createdAt = desc_json['createdAt'].replace('T',',  Time: ')
        meta_data = desc_json['courseMeta'][0]['overview']
        overview = meta_data['learn']
        requirements = meta_data['requirements']
        features = meta_data['features']
        language = meta_data['language']
        pricing = desc_json['pricing']
        rupee = pricing['IN']
        dollar = pricing['US']
        discount = pricing['discount']
    
        context = {'description':description,'createdAt':createdAt,'overview':overview,
                'requirements':requirements,'features':features,'language':language,'section':section,
                'rupee':rupee,'dollar':dollar,'discount':discount}
        logger.info('details created successfully.')
        return render_template('course_details.html',context=context,)
    except Exception as e:
        logger.error('error in creating details of the course {} : {}'.format(section,e))
        return e


@app.route('/create_pdf',methods=['POST'])
def create_pdf():
    logger.info('inside create_pdf function')
    try:
        if request.method=='POST':
            logger.info('creating pdf')
            host = request.form['host'].strip()
            course = request.form['course'].strip()
            if course not in i_neuron_courses:
                logger.warn('course is not availabe right now')
                return '<h1 style="text-align:center;margin-top:500px">{} is not availabe, try for different course!! </h1>'.format(course)
            
            path = '/details/'
            course_url = host+path+course.replace(' ','%20')
            
            pdfkit.from_url(course_url, "{}.pdf".format(course), verbose=True)
            
            logger.info('pdf created successfully')
            return '<h1 style="text-align:center;margin-top:500px">pdf file for course "{}" has created successfully!! </h1>'.format(course)
        else:
            logger.error('request body is incorrect')
            return redirect(url_for('/'))
        
    except Exception as e:
        logger.error('unable to create pdf for {} : {}'.format(host,e))
        return e   
    
    
@app.route('/db_credentials',methods=['GET'])
def db_credentials():
    return render_template('db_credentials.html')   
     
@app.route('/store_in_mysql_db',methods=['POST','GET']) 
def data_storing_in_mysql():
    try:
        if request.method == 'POST':
            user = request.form['user'].strip()
            passwd = request.form['passwd'].strip()
            host = request.form['localhost'].strip()
            
            
            db_operations = msql_db.DbOperation(user=user,passwd=passwd,host=host)
        
            
            db_operations.create_database()
            db_operations.create_table()
            
            for i in i_neuron_courses:
                db_operations.insert_data(i,i_neuron_courses[i]['description'])
            logger.debug('all the couses and their description stored in MySQL database')
            
            return '<h1 style="text-align:center;margin-top:500px">all courses and their details stored in MySQL database successfully</h1>'
    
        else:
            logger.error('method must be POST')  
            return redirect('db_credentials.html')  
        
    except Exception as e:
        logger.error('unable to enter data into database : {}'.format(e))
        return e   
    
@app.route('/mongodb_operation',methods=['GET'])
def mongodb_operations():
    return render_template('mongodb_creds.html') 
     
@app.route('/mongodb',methods=['POST','GET'])   
def data_storing_in_mongodb():
    try:
        if request.method=='POST':
            
            url = request.form['url'].strip()
            
            logger.info('creating mongodb connection')
            mongo = mongo_db.MongodbConnection(url)
            logger.info('mongodb connection stablished successfully')
            mongo.database_collection() 
            logger.info('database and collection created successfully') 
            
            logger.info('inserting data into collection it will take 3 to 4 min to insert all data into database')
            for i in i_neuron_courses:
                dict = {'name':i,'description':i_neuron_courses[i]['description']}
                mongo.insert_data(dict)
            logger.info('All the data inserted into collection successfully')    
            return '<h1 style="text-align:center;margin-top:500px">all courses and their details stored in Mongodb database successfully</h1>'        
    
    except Exception as e:
        logger.error('Exception while creating connection and adding data into database : {}'.format(e))
        return e
        


if __name__ == '__main__':
    application.run(host='0.0.0.0',port='4000')
    