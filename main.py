import requests
from bs4 import BeautifulSoup

import pdfplumber
import os
import pandas as pd
import csv


url="https://www.banking.gov.tw/ch/home.jsp?id=192&parentpath=0,4&mcustomize=multimessage_view.jsp&dataserno=21207&aplistdn=ou=disclosure,ou=multisite,ou=chinese,ou=ap_root,o=fsc,c=tw&toolsflag=Y&dtable=Disclosure"
req=requests.get(url)
soup=BeautifulSoup(req.content,"lxml")
table=soup.find('table')

header=["金融機構名稱", "流通卡數", "有效卡數", "當月發卡數", "當月停卡數", "循環信用餘額", "未到期分期付款餘額", "當月簽帳金額", 
    "當月預借現金金額", "逾期三個月以上帳款占應收帳款餘額(含催收款)之比率(%)", "逾期六個月以上帳款占應收帳款餘額(含催收款)之比率(%)", 
    "備抵呆帳提足率(%)", "當月轉銷呆帳金額", "當年度轉銷呆帳金額累計至資料月份"]

header_old=["金融機構名稱", "流通卡數", "有效卡數", "當月發卡數", "當月停卡數", "循環信用餘額", "當月簽帳金額", 
    "當月預借現金金額", "逾期三個月以上帳款占應收帳款餘額(含催收款)之比率(%)", "逾期六個月以上帳款占應收帳款餘額(含催收款)之比率(%)", 
    "備抵呆帳提足率(%)", "當月轉銷呆帳金額", "當年度轉銷呆帳金額累計至資料月份"]

href=list()
tt=list()
data=pd.DataFrame()
for a in table.find_all('a'):
    url = a.get("href")
    if (type(url) == str) and ('.zip' not in url):
        if url[:3]=="www": url="http://"+url

        n=str(url).find("file")
        t=url[n+5:n+5+6]
        
        if t[:3]=="/複本":
            n=n+3
            t=url[n+5:n+5+6]
        if t[:3]=="/更新":
            n=n+3
            t=url[n+5:n+5+6]
        if t=="/file/":
            n=str(url).find("file/")
            t=url[n+5:n+5+6]
        
        t=t.replace(" ","")
        t=t.replace("/","")
        t=t.replace("_","")
        t=t.replace("信","")
        
        if t=="104年5月": t="10405"

        if(os.path.exists("./data_pdf/"+t+".pdf")): 
            print(t+".pdf exists")
        else:
            re=requests.get(url)
            pdf=open("./data_pdf/"+t+".pdf", 'wb')
            pdf.write(re.content)
            pdf.close()
            print(t+".pdf download")

        if(os.path.exists("./data_csv/"+t+".csv")): 
            print(t+".csv exists")
        else:
            pdf=pdfplumber.open("./data_pdf/"+t+".pdf")
            page=pdf.pages[0]
            table=page.extract_table()
            if len(table[0])==13:
                table=pd.DataFrame(table, columns=header_old)
            else:
                table=pd.DataFrame(table, columns=header)

            table.drop(0, inplace=True)
            table['yyymm']=t
            table.to_csv("./data_csv/"+t+".csv", index=False)
            print(t+".csv download")

        with open("./data_csv/"+t+".csv", 'r') as file:
            data1=pd.read_csv(file)
            data=pd.concat([data, data1])

        tt.append(t)
        href.append(url)

data.to_csv("data.csv", index=True)
print(data.head())

"""
        with open("./data_csv/"+t+".csv", 'r') as file:
            file_csv=csv.reader(file)
            data1=pd.read_csv(file, names=header)
            data1.drop(['index'], axis=1, inplace=True)
            data1.drop([0, 1], inplace=True)
            data1['yyymm']=t
"""

