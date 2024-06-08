import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import pandas as pd
import numpy as np
import re 
import io
import mysql.connector

def image_to_text(path):
    input_img=Image.open(path)
    #input_img

    # converting image to array format
    image_array=np.array(input_img)
    #image_array

    reader=easyocr.Reader(['en']) # to recognise english language
    text=reader.readtext(image_array,detail=0) # to hide array and show only text data as list

    return text,input_img

def extracted_text(texts):
    extracted_dict={
        "Name":[],
        "Designation":[],
        "Company_Name":[],
        "Contact":[],
        "Email":[],
        "Website":[],
        "Address":[],
        "Pincode":[]
    }

    extracted_dict["Name"].append(texts[0])
    extracted_dict["Designation"].append(texts[1])

    for i in range(2,len(texts)):   # 0-name , 1-designation rest of info starts from 2nd index
        
        if texts[i].startswith("+")or(texts[i].replace("-","").isdigit() and '-' in texts[i]):
            extracted_dict['Contact'].append(texts[i])

        elif "@" in texts[i] and ".com" in texts[i]:
                extracted_dict["Email"].append(texts[i])

        elif "www" in texts[i] or  "WWW" in texts[i]   or "WWw" in texts[i] or "WwW" in texts[i] or "wwW" in texts[i] or "Www" in texts[i] or "wWw" in texts[i]:
            small=texts[i].lower()
            extracted_dict["Website"].append(small) 

        elif "Tamil Nadu" in texts[i] or "TamilNadu" in texts[i] or texts[i].isdigit() :
             extracted_dict["Pincode"].append(texts[i])    

        elif re.match(r'^[A-Za-z]',texts[i]):
             extracted_dict["Company_Name"].append(texts[i])

        else:
             remove_colon=re.sub(r'[,;]','',texts[i])     
             extracted_dict["Address"].append(remove_colon)

    
    for key,value in extracted_dict.items():
         #print(key,":",value,len(value))
         if len(value)>0:
              concatenate=" ".join(value)
              extracted_dict[key]=[concatenate]

         else:
              value="NA"
              extracted_dict[key]=value     

    return extracted_dict



# streamlit part

st.set_page_config(layout='wide')
st.title("Extracting Business Card Data with 'OCR'")

with st.sidebar:
    select=option_menu("Main Menu",["Home", "Upload & Modifying","Delete"])

if select == "Home" :
    st.markdown("### :blue[**Technologies Used :**] Python,easy OCR, Streamlit, SQL, Pandas")

    st.write(
                "### :green[**About :**] Bizcard is a Python application designed to extract information from business cards.")
    st.write(
                '### The main purpose of Bizcard is to automate the process of extracting key details from business card images, such as the name, designation, company, contact information, and other relevant data. By leveraging the power of OCR (Optical Character Recognition) provided by EasyOCR, Bizcard is able to extract text from the images.')

elif select == "Upload & Modifying":
    img=st.file_uploader("Upload the Image",type=["png","jpg","jpeg"]) 

    if img is not None:
         st.image(img, width= 300)

         text_image,input_img=image_to_text(img)

         text_dict=extracted_text(text_image)
         if text_dict:
              st.success("Text is Extracted Successfully")

         df=pd.DataFrame(text_dict)

         #st.dataframe(df)

         # converting image to bytes

         Image_bytes=io.BytesIO()
         input_img.save(Image_bytes, format="PNG")

         image_data=Image_bytes.getvalue()

        # creating dictionary
         data={"Image":[image_data]}

         df_1=pd.DataFrame(data)

         concat_df=pd.concat([df,df_1],axis=1) # axis=1 -> to concatenate column wise
         st.dataframe(concat_df)

         button1=st.button("Save",use_container_width=True)

         if button1:
            mycon = mysql.connector.connect(

                host = "localhost",
                user = "root",
                password = 'Mageswari@123',
                database='bizcard'
                
            )
            mycon


            mycursor=mycon.cursor()

            create_table_query=""" create table if not exists Bizcardx(Name varchar(255),
                                                                        Designation varchar(255),
                                                                        Company_name varchar(255),
                                                                        Contact varchar(255),
                                                                        Email varchar(255),
                                                                        Website text,
                                                                        Address text,
                                                                        Pincode varchar(255),
                                                                        Image text) """

            mycursor.execute(create_table_query)
            mycon.commit()

            alter_query=""" ALTER TABLE Bizcardx MODIFY COLUMN Image LONGBLOB """
            mycursor.execute(alter_query)


            insert_query = """ 
                    INSERT INTO Bizcardx(
                        Name, Designation, Company_name, Contact, Email, Website, Address, Pincode, Image
                    ) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) 
                """

            datas = concat_df.values.tolist()

            # Use executemany for batch insert
            mycursor.executemany(insert_query, datas)
            mycon.commit()
            st.success("Saved Successfully")

    method=st.radio("Select the method",["None","Preview","Modify"])     

    if method=="None":
         st.write("")

    if method=="Preview":
         
         mycon = mysql.connector.connect(

                host = "localhost",
                user = "root",
                password = 'Mageswari@123',
                database='bizcard'
                
            )
         mycon


         mycursor=mycon.cursor()


         select_query="select * from bizcardx"

         mycursor.execute(select_query)
         table=mycursor.fetchall()
         mycon.commit()

         table_df=pd.DataFrame(table,columns=("Name","Designation","Company_name", "Contact", "Email", "Website", "Address", "Pincode", "Image"))
         st.dataframe(table_df)

    elif method=="Modify":
          mycon = mysql.connector.connect(

                host = "localhost",
                user = "root",
                password = 'Mageswari@123',
                database='bizcard'
                
            )
          mycon


          mycursor=mycon.cursor()


          select_query="select * from bizcardx"

          mycursor.execute(select_query)
          table=mycursor.fetchall()
          mycon.commit()

          table_df=pd.DataFrame(table,columns=("Name","Designation","Company_name", "Contact", "Email", "Website", "Address", "Pincode", "Image"))

          col1,col2=st.columns(2)
          with col1:
               select_name=st.selectbox("Select the name",table_df["Name"])

          df2=table_df[table_df["Name"]==select_name] 
          #st.dataframe(df2)

          df3=df2.copy()  
          #st.dataframe(df3) 
         
          col1,col2=st.columns(2)
          with col1:
               modify_name=st.text_input("Name",df2["Name"].unique()[0])  
               modify_designation=st.text_input("Designation",df2["Designation"].unique()[0]) 
               modify_company=st.text_input("Company_name",df2["Company_name"].unique()[0]) 
               modify_contact=st.text_input("Contact",df2["Contact"].unique()[0]) 
               modify_email=st.text_input("Email",df2["Email"].unique()[0])  

               df3["Name"].iloc[0] = modify_name
               df3["Designation"].iloc[0] = modify_designation
               df3["Company_name"].iloc[0] = modify_company
               df3["Contact"].iloc[0] = modify_contact
               df3["Email"].iloc[0] = modify_email


          with col2:
               modify_website=st.text_input("Website",df2["Website"].unique()[0])  
               modify_address=st.text_input("Address",df2["Address"].unique()[0]) 
               modify_Pincode=st.text_input("Pincode",df2["Pincode"].unique()[0]) 
               modify_image=st.text_input("Image",df2["Image"].unique()[0]) 

               df3["Website"].iloc[0]=modify_website
               df3["Address"].iloc[0]=modify_address
               df3["Pincode"].iloc[0]=modify_Pincode
               df3["Image"].iloc[0]=modify_image
               
               st.dataframe(df3)

               col1,col2=st.columns(2)
               with col1:
                    button3=st.button("Modify",use_container_width=True)


               if button3:
                     mycon = mysql.connector.connect(

                        host = "localhost",
                        user = "root",
                        password = 'Mageswari@123',
                        database='bizcard'
                        
                        )
                     mycon


                     mycursor=mycon.cursor()

                     mycursor.execute(f"Delete from bizcardx where Name='{select_name}'")
                     mycon.commit()

                     insert_query = """ 
                                INSERT INTO Bizcardx(
                                    Name, Designation, Company_name, Contact, Email, Website, Address, Pincode, Image
                                ) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) 
                            """

                     datas = df3.values.tolist()[0]

                     mycursor.execute(insert_query, datas)
                     mycon.commit()
                     st.success("Modified Successfully")


elif select == "Delete":
    mycon = mysql.connector.connect(

                host = "localhost",
                user = "root",
                password = 'Mageswari@123',
                database='bizcard'
                
            )
    mycon


    mycursor=mycon.cursor()

    col1,col2=st.columns(2)
    with col1:
        select_query="select Name from bizcardx"

        mycursor.execute(select_query)
        table=mycursor.fetchall()
        mycon.commit()

        names=[]

        for i in table:
            names.append(i[0])

        name_select=st.selectbox("Select the Name",names)

    with col2:
        select_query1=f"select Designation from bizcardx where Name='{name_select}'"

        mycursor.execute(select_query1)
        table1=mycursor.fetchall()
        mycon.commit()

        Designations=[]

        for j in table1:
            Designations.append(j[0])

        designation_select=st.selectbox("Select the Designation",Designations)      

    if name_select and designation_select:
        col1,col2,col3=st.columns(3)

        with col1:
            st.write(f"Selected name : {name_select}")
            st.write("")
            st.write("")
            st.write("")
            

        with col2:
            st.write(f"Selected Designation : {designation_select}")
            st.write("")
            st.write("")
            st.write("")

        remove=st.button("Delete",use_container_width=True)

        if remove:
            mycursor.execute(f"Delete from bizcardx where Name='{name_select}'and Designation='{designation_select}'")
            mycon.commit()

            st.warning("Record Deleted")
            


