import ast
import functools
from flask import Flask,request,render_template,redirect,url_for,flash,session,send_file,send_from_directory
import datetime
from flask_mail import Mail,Message
import random
import string
import os
import connectDB as db
import uuid

# FLASK_RUN_PORT=8080
# FLASK_RUN_HOST=0.0.0.0
# pip install -r requirement.txt

# print(secrets.token_urlsafe())


def create_app():
    app=Flask(__name__)
    app.secret_key='oBQ4GBTlzpSwE2OCGzRCGcXVANO9bsYZL_Cf3CSEXPs'

    app.config['MAIL_SERVER']='smtp-mail.outlook.com'
    app.config['MAIL_PORT']=587
    app.config['MAIL_USERNAME']='cerclesportif@outlook.com'
    app.config['MAIL_PASSWORD']='sport483!'
    app.config['MAIL_USE_TLS']=True
    app.config['MAIL_USE_SSL']=False
    mail=Mail(app)

    


    def login_required(route):
        @functools. wraps(route)
        def route_wrapper(*args, **kwargs):
            if not session.get('user'):
                return redirect(url_for("home"))
            return route(*args, **kwargs)
        return route_wrapper



    @app.route('/home')
    @app.route('/')
    def home():
        return render_template('home.html')



    @app.route('/companyLogin',methods=['POST','GET'])
    def companyLogin():
        email=''

        if session.get('user') and session.get('status')=='company':
            return redirect(url_for('companyDashboard'))

        if request.method=='POST':
            email=request.form.get('email')
            password=request.form.get('pass')
            sql="select * from company where email='{}'".format(email)

            for company in db.retrievedb(sql):
                if company.get('password')==password:
                    comp=company.copy()
                    comp.pop('password')
                    session['user']=comp
                    session['status']='company'
                    session.permanent = True
                    app.permanent_session_lifetime = datetime.timedelta(minutes=60)
                    return redirect(url_for('companyDashboard'))
            flash('Incorrect email or password')
        return render_template('companylogin.html',email=email)



    @app.route('/companyRegister',methods=['POST','GET'])
    def companyRegister():
        company=''
        if request.method=='POST':
            email=request.form.get('email')
            password=request.form.get('pass1')
            pass2=request.form.get('pass2')
            cname=request.form.get('cname')
            phone=request.form.get('phone')
            tin=request.form.get('tin')
            c_status=request.form.get('c_status')
            
            companyDict={'email':email,'cname':cname,'phone':phone,'tin':tin,'password':password,'c_status':c_status}

            if pass2 != password:
                flash('passwords typed are different')
                return render_template('companyRegister.html',company=companyDict)
            
            sql1="select * from company where email='{}'".format(email)
            sql2="select * from company where cname='{}'".format(cname)
            
            if  db.retrievedb(sql1):
                flash('email has been taken')
                return render_template('companyRegister.html',company=companyDict)
            elif db.retrievedb(sql2):
                flash('company name has been taken')
                return render_template('companyRegister.html',company=companyDict)

            sql3="insert into company values('{}','{}','{}','{}','{}','{}')".format(email,cname,phone,tin,password,c_status)
            db.savedb(sql3)  
            session.clear()
            flash('account is successful registered')
            print(companyDict)
            return redirect(url_for('companyLogin'))

        return render_template('companyRegister.html',company=company)



    @app.route('/supplierLogin',methods=['POST','GET'])
    def supplierLogin():
        email=''

        if session.get('user') and session.get('status')=='supplier':
            return redirect(url_for('supplierDashboard'))

        if request.method=='POST':
            email=request.form.get('email')
            password=request.form.get('pass')

            sql="select * from supplier where email='{}'".format(email)

            for supplier in db.retrievedb(sql):
                if supplier.get('password')==password:
                    supp=supplier.copy()
                    supp.pop('password')
                    session['user']=supp
                    session['status']='supplier'
                    session.permanent = True
                    app.permanent_session_lifetime = datetime.timedelta(minutes=60)
                    return redirect(url_for('supplierDashboard'))

            flash('Incorrect email or password')
        return render_template('supplierlogin.html',email=email)



    @app.route('/supplierRegister',methods=['POST','GET'])
    def supplierRegister():
        supplier=''
        if request.method=='POST':
            email=request.form.get('email')
            password=request.form.get('pass1')
            pass2=request.form.get('pass2')
            fname=request.form.get('fname')
            lname=request.form.get('lname')
            phone=request.form.get('phone')
            tin=request.form.get('tin')
            status=request.form.get('status')
            
            supplierDict={'email':email,'fname':fname,'lname':lname,'phone':phone,'tin':tin,'password':password,'status':status}

            if pass2 != password:
                flash('password used are different')
                return render_template('supplierRegister.html',supplier=supplierDict)

            sql1="select * from supplier where email='{}'".format(email)
            if db.retrievedb(sql1):
                flash('email has been taken')
                return render_template('supplierRegister.html',supplier=supplierDict)

            sql2="insert into supplier values('{}','{}','{}','{}','{}','{}','{}')".format(email,fname,lname,phone,tin,password,status)
            db.savedb(sql2)
            print(supplierDict)
            session.clear()
            flash('account is successful registered')
            return redirect(url_for('supplierLogin'))

        return render_template('supplierRegister.html',supplier=supplier)



    @app.route('/recoveryPassword/<status>',methods=['POST','GET'])
    def recoveryPass(status):
        if request.method=='POST':
            status=request.form.get('status')
            usermail=request.form.get('email')

            if 'company' in status:
                sql1="select * from company where email='{}'".format(usermail)
                for cmpny in db.retrievedb(sql1):
                    if cmpny.get('email') == usermail:
                        
                        randomCode = ''.join(random.choice(string.printable) for i in range(8))
                        print(f'the mail is ====>>>>>> {usermail} and type is ====>>>> {type(usermail)}')
                        msg=Message('Verification Code',sender='cerclesportif@outlook.com',recipients=['{}'.format(usermail)])
                        msg.body=f'Verification code below:\n{randomCode}'
                        mail.send(msg)
                        print(randomCode)
                        session['verifC']=randomCode
                        session['verifE']=usermail
                        flash('check your email! There is a code that we sent you')
                        return redirect(url_for('validateSentMail',status='company'))
                flash("The email entered doesn't found")
            elif 'supplier' in status:
                sql2="select * from supplier where email='{}'".format(usermail)
                for supp in db.retrievedb(sql2):
                    if supp.get('email')== usermail:
                        randomCode = ''.join(random.choice(string.printable) for i in range(8))
                        print(f'the mail is ====>>>>>> {usermail} and type is ====>>>> {type(usermail)}')
                        msg=Message('Verification Code',sender='cerclesportif@outlook.com',recipients=['{}'.format(usermail)])
                        msg.body=f'Verification code below:\n{randomCode}'
                        mail.send(msg)
                        print(randomCode)
                        session['verifC']=randomCode
                        session['verifE']=usermail
                        flash('check your email! There is a code that we sent you')
                        return redirect(url_for('validateSentMail',status='supplier'))
                flash("The email entered doesn't found")
            

        return render_template('recoveryForget.html',status=status)



    @app.route('/validateSentMail/<status>',methods=['POST','GET'])
    def validateSentMail(status):
        if request.method=='POST':
            status=request.form.get('status')
            codes=request.form.get('codes')
            pass1=request.form.get('pass1')

            if codes==session.get('verifC'):
                if 'company' in status:
                    
                    sql1="update company set password='{}' where email='{}'".format(pass1,session.get('verifE'))
                    db.updatedb(sql1)
                    session.clear()
                    flash('password is successful changed')
                    return redirect(url_for('companyLogin'))
                elif 'supplier' in status:

                    sql2="update supplier set password='{}' where email='{}'".format(pass1,session.get('verifE'))
                    db.updatedb(sql2)
                    session.clear()
                    flash('password is successful changed')
                    return redirect(url_for('supplierLogin'))
            else:
                flash('invalid codes')
                print(f'{session.get("verifC")}   and    {codes}')
                    

        return render_template('validateSentMesg.html',status=status)



    @app.errorhandler(404)
    def pageNoFound(error):
        return render_template('404page.html'), 404



    @app.route('/supplierDashboard/')
    @login_required
    def supplierDashboard():

        approvedMarket=0
        rejectedMarket=0
        pendingMarket=0 
        sql1="select * from bid where s_email='{}'".format(session.get('user').get('email'))
        for bid in db.retrievedb(sql1):
            if bid.get('b_status')=='approved':
                approvedMarket+=1
            elif bid.get('b_status')=='pending':
                pendingMarket+=1
            elif bid.get('b_status')=='rejected':
                rejectedMarket+=1

        totalMarket=approvedMarket+rejectedMarket+pendingMarket
        bidings={'totalMarket':totalMarket,'approvedMarket':approvedMarket,'rejectedMarket':rejectedMarket,'pendingMarket':pendingMarket}
        
        markets=[]
        sql2="select * from market where m_status='available'"
        for market in db.retrievedb(sql2):
            sql3="select * from company where email='{}'".format(market.get('cemail'))
            for company in db.retrievedb(sql3):
                
                a=company.copy()
                a.pop('password')
                a.pop('email')
                a.update(market)
                markets.append(a)
                break
        
        sql3="select * from notification where status='pending' and receiver='{}'".format(session.get('user')['email'])
        notifications=db.retrievedb(sql3)

        sql4="select * from message where status='pending' and receiver='{}'".format(session.get('user')['email'])
        messages=db.retrievedb(sql4)
        

        return render_template('supplierDashboard.html',supplier=session.get('user'),markets=markets,bidings=bidings,notifications=notifications,messages=messages)



    @app.route('/supplierApplyPublication/<data>',methods=['POST','GET'])
    @login_required
    def supplierApplyPublication(data):
        
        marketInfo=eval(data)

        if request.method=='POST':
            b_type=request.form.get('b_type')
            b_title=request.form.get('b_title')
            b_descr=request.form.get('b_descr')
            b_status=request.form.get('b_status')
            m_id=request.form.get('m_id')
            s_email=request.form.get('s_email')
            cemail=request.form.get('cemail')
            b_date=datetime.datetime.today()
            fl=request.files.get('file')
            thename=f'{s_email}-{uuid.uuid4().hex}.pdf'

            sql1="insert into bid (b_title,b_type,b_descr,b_status,b_date,m_id,s_email,doc_name) values('{}','{}', '{}', '{}', '{}','{}','{}','{}')".format(b_title,b_type,b_descr,b_status,b_date,m_id,s_email,thename)
            db.savedb(sql1)
            sql2="insert into notification (sender,sendername,senderstatus,receiver,message,status) values('{}','{}','{}','{}','{}','{}')".format(session.get("user")["email"],session.get("user")["fname"],'SUPPLIER',cemail,'Bidded on Your market','pending')
            db.savedb(sql2)
            fl.save(os.path.join('../supplierFile',thename))

            flash('your bid is successfully submitted')
            return render_template('supplierApplyPub.html',supplier=session.get('user'),market='')
            
        return render_template('supplierApplyPub.html',supplier=session.get('user'),market=marketInfo,)



    @app.route('/companyDashboard/')
    @login_required
    def companyDashboard():

        availableMarket=0
        closedMarket=0 
    
        markets=[]
        sql1="select * from market where cemail='{}'".format(session.get('user').get('email'))
        for market in db.retrievedb(sql1):

            a=session.get('user').copy()
            a.pop('email')
            a.update(market)
            markets.append(a)
            if market.get('m_status')=='available':
                availableMarket+=1
            
            elif market.get('m_status')=='closed':
                closedMarket+=1

        totalMarket=availableMarket+closedMarket
        allCompanyMarket={'totalMarket':totalMarket,'availableMarket':availableMarket,'closedMarket':closedMarket}


        sql3="select * from notification where status='pending' and receiver='{}'".format(session.get('user')['email'])
        notifications=db.retrievedb(sql3)

        sql4="select * from message where status='pending' and receiver='{}'".format(session.get('user')['email'])
        messages=db.retrievedb(sql4)
                

        return render_template('companyDashboard.html',company=session.get('user'),markets=markets,all_market=allCompanyMarket,notifications=notifications,messages=messages)



    @app.route('/companyListofApplicant/<data>')
    @login_required
    def companyListApplicant(data):
        
        supplierBiddedList=[]

        sql1="select * from bid where m_id='{}'".format(data)
        for bid in db.retrievedb(sql1):
            sql2="select * from supplier where email='{}'".format(bid.get('s_email'))
            for supp in db.retrievedb(sql2):
                
                a=supp.copy()
                a.pop('password')
                a['b_date']=bid.get('b_date')
                a['b_id']=bid.get('b_id')
                a['b_status']=bid.get('b_status')
                supplierBiddedList.append(a)

        return render_template('companyListApplicant.html',company=session.get('user'),suppliers=supplierBiddedList)



    @app.route('/companyCheckApplicant/<data>')
    @login_required
    def companyCheckApplicant(data):

        sql1="select * from bid where b_id='{}'".format(data)
        for bid in db.retrievedb(sql1):
            sql2="select * from supplier where email='{}'".format(bid.get('s_email'))
            for supp in db.retrievedb(sql2):
                
                a=supp.copy()
                a.pop('password')
                suppInfo=a
                break
            bidInfo=bid
            break
        suppInfo.update(bidInfo)
        session['downE']=suppInfo.get('email')
        session['downId']=suppInfo.get('doc_name')
        
        return render_template('companyCheckApplicant.html',company=session.get('user'),supplier=suppInfo)



    @app.route('/updateBidStatus/<data>')
    @login_required
    def updateBidStatus(data):

        bidupdt=eval(data)
        sql1="update bid set b_status='{}' where b_id='{}'".format(bidupdt.get('status'), bidupdt.get('b_id'))
        sql2="select *from bid where b_id='{}'".format( bidupdt.get('b_id'))
        db.updatedb(sql1)
        for bid in db.retrievedb(sql2):
            if bid.get('s_email'):
                break
        
        sql2="insert into notification (sender,sendername,senderstatus,receiver,message,status) values('{}','{}','{}','{}','{}','{}')".format(session.get("user")["email"],session.get("user")["cname"],'COMPANY',bid.get("s_email"),f'Bid is {bidupdt.get("status")}','pending')
        db.savedb(sql2)

        flash(f"The bidding is successful {bidupdt.get('status')}")
        return redirect(url_for('companyCheckApplicant',data=bidupdt.get('b_id')))



    @app.route('/publishMarket',methods=['POST','GET'])
    @login_required
    def companyPublishMarket():
        if request.method=='POST':
            m_title=request.form.get('m_title')
            m_type=request.form.get('m_type')
            details=request.form.get('details')
            cemail=request.form.get('cemail')
            m_status=request.form.get('m_status')
            pub_date=datetime.datetime.today()

            sql1="insert into market (m_title,m_type,details,pub_date,m_status,cemail) values('{}','{}', '{}', '{}', '{}','{}')".format(m_title,m_type,details,pub_date,m_status,cemail)
            db.savedb(sql1)
            flash('the market is successfully published')
        return render_template('companyPublishingForm.html',company=session.get('user'))



    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('home'))



    @app.route('/adminLogin',methods=['POST','GET'])
    def adminLogin():

        email=''

        if session.get('user') and session.get('status')=='admin':
            return redirect(url_for('adminDashboard'))

        if request.method=='POST':
            email=request.form.get('email')
            password=request.form.get('pass')
            
            sql1="select * from admin where email='{}'".format(email)
            for admin in db.retrievedb(sql1):
    
                if admin.get('password')==password:
                
                    admn= admin.copy()
                    admn.pop('password')
                    session['user']=admn
                    session['status']='admin'
                    session.permanent=True
                    app.permanent_session_lifetime = datetime.timedelta(minutes=60)
                    
                    return redirect(url_for('adminDashboard'))

            flash('Incorrect email or password')
        return render_template('adminLogin.html')



    @app.route('/adminDashboard')
    @login_required
    def adminDashboard():
    
        sql1="select * from supplier where status='deactivated'"
        suppliers=db.retrievedb(sql1)
        
        sql2="select * from company where c_status='deactivated'"
        companies=db.retrievedb(sql2)
        
        sql3="select * from notification where status='pending' and receiver='{}'".format(session.get('user')['email'])
        notifications=db.retrievedb(sql3)

        sql4="select * from message where status='pending' and receiver='{}'".format(session.get('user')['email'])
        messages=db.retrievedb(sql4)
        
        return render_template('adminDashboard.html',admin=session.get('user'),suppliers=suppliers,notifications=notifications,messages=messages,companies=companies)



    @app.route('/admitSupplier/<data>',methods=['POST','GET'])
    @login_required
    def admitSupplier(data):

        sql1="update supplier set status='activated' where email='{}'".format(data)
        db.updatedb(sql1)
       
        return redirect(url_for('adminDashboard'))



    @app.route('/admitCompany/<data>', methods=['GET','POST'])
    @login_required
    def admitCompany(data):

        sql1="update company set c_status='activated' where email='{}'".format(data)
        db.updatedb(sql1)
        
        return redirect(url_for('adminDashboard'))



    @app.route('/supplierNotification')
    @login_required
    def supplierNotification():

        sql1="update notification set status='read' where status='pending' and receiver='{}'".format(session.get('user')['email'])
        db.updatedb(sql1)

        return redirect(url_for('supplierDashboard'))



    @app.route('/companyNotification')
    @login_required
    def companyNotification():
        sql1="update notification set status='read' where status='pending' and receiver='{}'".format(session.get('user')['email'])
        db.updatedb(sql1)
        return redirect(url_for('companyDashboard'))



    @app.route('/unreadMessage/<data>', methods=['GET','POST'])
    @login_required
    def unreadMessage(data):
        sql1="update message set status='read' where msg_id='{}'".format(data)
        sql2="select * from message where msg_id='{}'".format(data)
        db.updatedb(sql1)
        for mssgs in db.retrievedb(sql2):
            if mssgs.get('msg_id'):
                break
        
        return redirect(url_for('readingMessage',data=mssgs))



    @app.route('/readingMessage/<data>', methods=['GET','POST'])
    @login_required
    def readingMessage(data):
        datas=eval(data)
        return render_template('readMessage.html', data=datas,status=session.get('status'),theUser=session.get('user'))



    @app.route('/checkingMessage')
    @login_required
    def checkingMessage():

        sql1="select * from message where receiver='{}'".format(session.get('user')['email'])
        messages=db.retrievedb(sql1)

        return render_template('messagesList.html',status=session.get('status'),theUser=session.get('user'),messages=messages) 



    @app.route('/writeMessage',methods=['POST','GET'])
    @login_required
    def writeMessage():
        data=request.args.get('data')

        if request.method == 'POST':
            data=request.form.get('email')
            mesg=request.form.get('mesg')
            stats=request.form.get('stats')

            if stats=='admin':
                sql1="select * from admin where email='{}'".format(data)
                for admin in db.retrievedb(sql1):
                    
                    if session.get('status') == 'company':
                        sql2="insert into message (sender,sendername,receiver,message,status,sent_date) values('{}','{}', '{}', '{}', '{}','{}')".format(session.get("user")["email"],session.get("user").get("cname"),data,mesg,'pending',datetime.datetime.today())
                        db.savedb(sql2)
                    else:
                        sql2="insert into message (sender,sendername,receiver,message,status,sent_date) values('{}','{}', '{}', '{}', '{}','{}')".format(session.get("user")["email"],f'{session.get("user").get("fname")} {session.get("user").get("lname")}',data,mesg,'pending',datetime.datetime.today())
                        db.savedb(sql2) 
                    flash(f'Message is successfully sent to {data}')
                    return render_template('writeMessage.html',data=data,status=session.get('status'),theUser=session.get('user'))

            elif stats=='company':
                sql1="select * from company where email='{}'".format(data)
                for company in db.retrievedb(sql1):
                    
                    if session.get('status') == 'company':
                        sql2="insert into message (sender,sendername,receiver,message,status,sent_date) values('{}','{}', '{}', '{}', '{}','{}')".format(session.get("user")["email"],session.get("user").get("cname"),data,mesg,'pending',datetime.datetime.today())
                        db.savedb(sql2)
                    else:
                        sql2="insert into message (sender,sendername,receiver,message,status,sent_date) values('{}','{}', '{}', '{}', '{}','{}')".format(session.get("user")["email"],f'{session.get("user").get("fname")} {session.get("user").get("lname")}',data,mesg,'pending',datetime.datetime.today())
                        db.savedb(sql2) 
                    flash(f'Message is successfully sent to {data}')
                    
                    return render_template('writeMessage.html',data=data,status=session.get('status'),theUser=session.get('user'))
            
            elif stats=='supplier':
                sql1="select * from supplier where email='{}'".format(data)
                for supplier in db.retrievedb(sql1):
                    
                    if session.get('status') == 'company':
                        sql2="insert into message (sender,sendername,receiver,message,status,sent_date) values('{}','{}', '{}', '{}', '{}','{}')".format(session.get("user")["email"],session.get("user").get("cname"),data,mesg,'pending',datetime.datetime.today())
                        db.savedb(sql2)
                    else:
                        sql2="insert into message (sender,sendername,receiver,message,status,sent_date) values('{}','{}', '{}', '{}', '{}','{}')".format(session.get("user")["email"],f'{session.get("user").get("fname")} {session.get("user").get("lname")}',data,mesg,'pending',datetime.datetime.today())
                        db.savedb(sql2) 
                    flash(f'Message is successfully sent to {data}')
                    return render_template('writeMessage.html',data=data,status=session.get('status'),theUser=session.get('user'))

            flash("Sorry, we can't find email address. Please try again.")

        return render_template('writeMessage.html',data=data,status=session.get('status'),theUser=session.get('user')) 



    @app.route('/filedownload')
    @login_required
    def file_download():
        
        return send_from_directory('../supplierFile',f'{session.get("downId")}',as_attachment=True,download_name=f'{session.get("downE")}.pdf')



    @app.route('/supplierCheckMarket/<data>', methods=['GET','POST'])
    @login_required
    def supplierCheckMarket(data):
        
        sql1="select * from bid where s_email='{}' and b_status='{}'".format(session.get('user').get('email'),data)
        biddings=db.retrievedb(sql1)
        
        return render_template('supplierCheckMarket.html',data=data,biddings =biddings,supplier=session.get('user'))



    @app.route('/companyCheckMarket/<data>', methods=['GET','POST'])
    @login_required
    def companyCheckMarket(data):

        sql1="select * from market where cemail='{}' and m_status='{}'".format(session.get('user').get('email'),data)
        markets=db.retrievedb(sql1)

        return render_template('companyCheckMarket.html',data=data,markets =markets,company=session.get('user'))



    @app.route('/companyCloseMarket/<data>')
    @login_required
    def companyCloseMarket(data):

        sql1="update market set m_status='closed' where m_id='{}'".format(data)
        db.updatedb(sql1)
        
        return redirect(url_for('companyCheckMarket',data='available'))

    return app
