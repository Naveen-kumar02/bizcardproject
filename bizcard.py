import streamlit as st
import pandas as pd
import numpy as np
import pymysql
import easyocr
from streamlit_option_menu import option_menu
from PIL import Image
import cv2
import os
import io
import matplotlib.pyplot as plt
import re
import base64


#set page congiguration
st.set_page_config(page_title= "BizCardX: Extracting Business Card Data with OCR | By Akash C",
                   #page_icon= icon,
                   layout= "wide",
                   initial_sidebar_state= "expanded",
                   menu_items={'About': """# This OCR app is created by *Akash C*!"""})
st.markdown("<h1 style='text-align: center; color: white;'>BizCardX: Extracting Business Card Data with OCR</h1>", unsafe_allow_html=True)

# CREATING OPTION MENU
selected = option_menu(None, ["Home","Upload & Extract","Database"], 
                       icons=["house","cloud-upload","pencil-square"],
                       default_index=0,
                       orientation="horizontal",
                       styles={"nav-link": {"font-size": "25px", "text-align": "centre", "margin": "0px", "--hover-color": "#6495ED"},
                               "icon": {"font-size": "25px"},
                               "container" : {"max-width": "6000px"},
                               "nav-link-selected": {"background-color": "#6495ED"}})


#sql connectivity
myconnection=pymysql.connect(host='127.0.0.1',
                             user='root',
                             password='Naveenk02',
                             database='bizcard')
cur=myconnection.cursor()

#create table  to store data
cur.execute('''create table if not exists card_data
            (name text,
             designation text,
             mobile_number varchar(20),
             alternative_number varchar(20),
             email text,
             website text,
             street text,
             city text,
             state text,
             pincode varchar(10),
             company_name text,
             image longblob
            )''')

def image_to_text():
    reader=easyocr.Reader(['en'])
    result=reader.readtext(image_path)
    details=[]
    for i in range(len(result)):
        details.append(result[i][1])
    name=[]
    designation=[]
    phone_number=[]
    email=[]
    website=[]
    street=[]
    city=[]
    state=[]
    pincode=[]
    company_name=[]

    for i in range(len(details)):
        match1= re.findall('([0-9]+ [A-Z]+ [A-Za-z]+)., ([a-zA-Z]+). ([a-zA-Z]+)',details[i])
        match2 = re.findall('([0-9]+ [A-Z]+ [A-Za-z]+)., ([a-zA-Z]+)', details[i])
        match3 = re.findall('^[E].+[a-z]',details[i])
        match4 = re.findall('([A-Za-z]+) ([0-9]+)',details[i])
        match5 = re.findall('([0-9]+ [a-zA-z]+)',details[i])    
        match6 = re.findall('.com$' , details[i])
        match7 = re.findall('([0-9]+)',details[i])
        if details[i]==details[0]:
            name.append(details[i])
        elif details[i]==details[1]:
            designation.append(details[i])
        elif '-' in details[i]:
            phone_number.append(details[i])
        elif '@' in details[i]:
            email.append(details[i])
        elif 'www ' in details[i].lower() or 'www.' in details[i].lower():
            website.append(details[i])
        elif 'WWW' in details[i]:
            website.append(details[i]+"."+ details[i+1])
        elif match6:
            pass
        elif match1:
            street.append(match1[0][0])
            city.append(match1[0][1])
            state.append(match1[0][2])
        elif match2:
            street.append(match2[0][0])
            city.append(match2[0][1])
        elif match3:
            city.append(match3[0])
        elif match4:
            state.append(match4[0][0])
            pincode.append(match4[0][1])
        elif match5:
            street.append(match5[0]+" St, ")
        elif match7:
            pincode.append(match7[0])
        else:
            company_name.append(details[i])
    if len(company_name)>1:
        comp=company_name[0]+" "+company_name[1]
        print(comp)
    else:
        comp=company_name[0]
    if len(phone_number)>1:
        number=phone_number[0]
        alternative_number=phone_number[1]
    else:
        number=phone_number[0]
        alternative_number=None
    
    with open(image_path,'rb') as image_file:
        image_data=image_file.read()

    #convert the binary image data to a base64 encoded string
    encoded_image=base64.b64encode(image_data).decode('utf-8')

    image_details={'name':name[0],
                   'designation':designation[0],
                   'phone_number':number,
                   'alternative_number':alternative_number,
                   'email':email[0],
                   'website':website[0],
                   'street':street[0],
                   'city':city[0],
                   'state':state[0],
                   'pincode':pincode[0],
                   'company_name':comp,
                   'image':encoded_image}
    
    return image_details




if selected=='Home':
    st.markdown("## :green[**Technologies Used :**] Python,easy OCR, Streamlit, SQL, Pandas")
    st.markdown("## :green[**Overview :**] In this streamlit web app you can upload an image of a business card and extract relevant information from it using easyOCR. You can view, modify or delete the extracted data in this app. This app would also allow users to save the extracted information into a database along with the uploaded business card image. The database would be able to store multiple entries, each with its own business card image and extracted information.")

if selected=='Upload & Extract':
    reader=easyocr.Reader(['en'])
    st.markdown("### :green[Upload a Business Card:]")
    uploaded_card = st.file_uploader("upload here",label_visibility="collapsed",type=["png","jpeg","jpg"])
    extract=st.button('Extract and upload')
    col1,col2=st.columns([2,2])

    with col1:
        path=False
        if uploaded_card is not None:
            image_path=os.getcwd()+"\\" + "pic" + "\\"+ uploaded_card.name
            image=Image.open(image_path)
            st.write(" ")
            st.write(" ")
            st.subheader(":green[Uploaded image:]")
            col1.image(image)
            path=True
    with col2:
        if path:
            image_details=image_to_text()
            if extract:
                img=cv2.imread(image_path)
                reader=easyocr.Reader(['en'])
                result=reader.readtext(image_path)
                for detection in result:
                    top_left=tuple([int(val) for val in detection[0][0]])
                    bottom_right=tuple([int(val) for val in detection[0][0]])
                    text=detection[1]
                    font=cv2.FONT_HERSHEY_SIMPLEX
                    #img=cv2.rectangle(img,top_left,bottom_right,(0,255,0),2)
                    img=cv2.putText(img,text,top_left,font,1,(255,0,0),1,cv2.LINE_AA)
                    plt.figure(figsize=(20,20))
                #plt.rcParams['figure.figsize']=(10,10)
                #plt.imshow(image)

                st.write("")
                st.write("")
                st.subheader(":green[Extracted Text:]")
                st.image(img)
            
    with col1:
        if extract:
            st.subheader(":green[Extracted data]")
            st.write("**Name**:", image_details['name'])
            st.write("**Designation**:", image_details['designation'])
            st.write("**Contact Number**:",image_details['phone_number'])
            st.write("**Alternative Number:**",image_details['alternative_number'])
            st.write("**E-mail**:", image_details['email'])
            st.write("**Website**:", image_details['website'])
            st.write("**Street**:", image_details['street'])
            st.write("**City**:", image_details['city'])
            st.write("**State**:", image_details['state'])
            st.write("**Pincode**:", image_details['pincode'])
            st.write("**Company Name**:", image_details['company_name'])
            
        
            try:
                sql=f"select email from card_data where email= '{image_details['email']}';"
                cur.execute(sql)
                myconnection.commit()
                df=pd.DataFrame(cur.fetchall(),columns=[desc[0] for desc in cur.description])
                x=df.values.tolist()
                k=x[0][0]
                if image_details['email']==k:
                    st.warning("Duplicate Data, Data already exists" , icon="⚠")
                else:
                    pass
            except:
                df=pd.DataFrame(image_details,index=np.arange(1))
                li=df.values.tolist()
                query="insert into card_data values(%s, %s, %s, %s ,%s ,%s ,%s ,%s ,%s ,%s ,%s, %s)"
                cur.executemany(query,li)
                myconnection.commit()
                st.success('Data uploaded into MySql',icon='✅')

if selected =='Database':
    sql="select * from card_data"
    cur.execute(sql)
    myconnection.commit()
    df=pd.DataFrame(cur.fetchall(),columns=[desc[0] for desc in cur.description])
    st.header('Database')
    st.dataframe(df)
    st.button('show changes')

    add_selectedbox=st.selectbox(":green[**choose**]",
    ("Modify","Delete"))
    if add_selectedbox=='Modify':
        cur.execute('select name from card_data')
        result=cur.fetchall()
        name_list=[]
        for name in result:
            name_list.append(name[0])
        selected_name=st.selectbox('**:green[Select card holder name to modify the data]**',options=name_list)

        query1="select * from card_data where name = %s"
        cur.execute(query1, (selected_name))
        result1 = cur.fetchone()
        Name = st.text_input("**:green[Names]**",result1[0])
        Designation = st.text_input("**:green[designation]**",result1[1])
        Mobile_number = st.text_input("**:green[mobile_number]**",result1[2])
        Alternative_number = st.text_input("**:green[alternative_number]**",result1[3])
        Email = st.text_input("**:green[email]**",result1[4])
        Website = st.text_input("**:green[website]**",result1[5])
        Street = st.text_input("**:green[street]**",result1[6])
        City = st.text_input("**:green[city]**",result1[7])
        State = st.text_input("**:green[state]**",result1[8])
        Pincode = st.text_input("**:green[pincode]**",result1[9])
        Company_name = st.text_input("**:green[company name]**",result1[10])

        if st.button("update"):
            update_query="update card_data set name=%s, designation=%s ,mobile_number=%s, alternative_number=%s, email=%s, website=%s, street=%s, city=%s, state=%s, pincode=%s, company_name=%s where name=%s" 
            cur.execute(update_query,(Name,Designation,Mobile_number,Alternative_number,Email,Website,Street,City,State,Pincode,Company_name,selected_name))  
            myconnection.commit()
            st.success("Business card updataed successfully",icon="✅")


    if add_selectedbox=='Delete':
        cur.execute('select name from card_data')
        result=cur.fetchall()
        name_list=[]
        for name in result:
            name_list.append(name[0])
        selected_name=st.selectbox('**:green[Select card holder name to delete the data from database]**',options=name_list)

        #st.write("**Name:**",selected_name)
        st.write(":green[Note:] If you want to delete the ",selected_name,"click delete button")
        if st.button("DELETE"):
            cur.execute("Delete from card_data where name=%s",(selected_name))
            myconnection.commit()
            st.success("Data deleted from the database",icon="✅")


        


        
                



        
            
    