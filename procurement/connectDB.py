import datetime
import pymysql.cursors   

def getConnection(): 
    # You can change the connection arguments according to the pc configs.
    connection = pymysql.connect(host='127.0.0.1',port=3306,
                             user='root',
                             password='password',                             
                             db='procurement',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    return connection


def savedb(sql):

    print(sql)
    connection = getConnection() 
    cursor=connection.cursor()
    cursor.execute(sql)
    connection.commit()
    



def updatedb(sql):

    connection = getConnection() 
    cursor=connection.cursor()
    cursor.execute(sql)
    connection.commit()



def deletedb(sql):

    connection = getConnection() 
    cursor=connection.cursor()
    cursor.execute(sql)
    connection.commit()



def retrievedb(sql):

    mydata=[]
    conn=getConnection().cursor()
    conn.execute(sql)
    for row in conn:
        mydata.append(row)
    getConnection().close()

    return mydata


