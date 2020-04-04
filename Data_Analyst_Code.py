# -*- coding: utf-8 -*-
"""
Telepass Pay

Data Analyst Test Source Code.
"""

# Importing the libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Importing the datasets
contracts = pd.read_csv('contracts.csv', sep=';', skipinitialspace=True)
customers = pd.read_csv('customers.csv', sep=';', skipinitialspace=True)
fuel_trans = pd.read_csv('fuel transactions.csv', sep=';')
road_parking_trans = pd.read_csv('road parking transactions.csv', sep=';')

# Handling the leading and trailing spaces
contracts['Product'] = contracts['Product'].str.replace(" ","")
contracts['Contract status'] = contracts['Contract status'].str.replace(" ","")
customers['Residence Region'] = customers['Residence Region'].str.replace(" ","")
customers['Residence Province'] = customers['Residence Province'].str.replace(" ","")

# Task 1 - SocioDemographic analysis for BlueStripes Street Parking Service

# Wrangling Amount and Date columns, Preping for analysis
road_parking_trans['Transaction Amount (Euro)'] = road_parking_trans['Transaction Amount (Euro)'].str.replace(",",".")
road_parking_trans['Parking Starting Date'] = pd.to_datetime(road_parking_trans['Parking Starting Date'] + ' ' + road_parking_trans['Parking Starting Date Timestamp'])
road_parking_trans['Parking Exit Date'] = pd.to_datetime(road_parking_trans['Parking Exit Date'] + ' ' + road_parking_trans['Parking Exit Date Timestamp'])
road_parking_trans['Year'] = road_parking_trans['Parking Starting Date'].dt.year


# Filtering the records for only the year 2019
Blue_Stripes_Street_Data = road_parking_trans[road_parking_trans['Year'] == 2019]
Blue_Stripes_Street_Data['Year'].unique()

# Dropping the redundant columns and working on further wrangling needed for analysis
Blue_Stripes_Street_Data.drop(['Contract Id', 'Parking Starting Date Timestamp', 'Parking Exit Date Timestamp'], axis = 1, inplace = True)
Blue_Stripes_Street_Data.dtypes
Blue_Stripes_Street_Data['Transaction Amount (Euro)'] = Blue_Stripes_Street_Data['Transaction Amount (Euro)'].astype(float)
Blue_Stripes_Customer_Data = Blue_Stripes_Street_Data.groupby(['Customer Id','Year'],as_index=False).agg({'Transaction Amount (Euro)': "sum"})
Customer_Data = Blue_Stripes_Customer_Data.sort_values('Transaction Amount (Euro)',ascending=False)

# Joining the resultant table with the customers table to extract the sociodemographic information
Target_Customers= pd.merge(Customer_Data, customers, on='Customer Id', how='inner')
Target_Customers['Customer Id'] = Target_Customers['Customer Id'].astype(object)

# Filtering the records for non-zero transaction amount values
Target_Customers = Target_Customers[Target_Customers['Transaction Amount (Euro)'] != 0]
#Target_Customers = Target_Customers[Target_Customers['Transaction Amount (Euro)'] > 100] 
summary = Target_Customers.describe(include='all')

# Visulalizing the SocioDemographic customer data to find the target group
df = Target_Customers[['Gender','Age Range','Transaction Amount (Euro)']].groupby(['Gender','Age Range']).sum().reset_index()
sns.catplot(x='Gender', y='Transaction Amount (Euro)', hue='Age Range', height=4, data=df, kind="bar")
plt.title('SocioDemographic Analysis - Part-1', fontsize=20)

df1 = Target_Customers[['Gender','Residence Region','Transaction Amount (Euro)']].groupby(['Gender','Residence Region']).sum().reset_index()
sns.catplot(x='Gender', y='Transaction Amount (Euro)', hue='Residence Region', height=4, data=df1, kind="bar")
plt.title('SocioDemographic Analysis - Part-2', fontsize=20)

df2 = Target_Customers[['Gender','Residence Province','Transaction Amount (Euro)']].groupby(['Gender','Residence Province']).sum().reset_index()
df3 = df2.nlargest(10, ['Transaction Amount (Euro)'])
sns.catplot(x='Gender', y='Transaction Amount (Euro)', hue='Residence Province', height=4, data=df3, kind="bar")
plt.title('SocioDemographic Analysis - Part-3', fontsize=20)

Target_Customers.dtypes
Privileged_Customers = Target_Customers[Target_Customers['Transaction Amount (Euro)'] > 1500]
sns.catplot(x='Customer Id', y='Transaction Amount (Euro)', height=4, data=Privileged_Customers, kind="bar")
plt.title('Privileged Customers', fontsize=20)

# Exporting the dataframe to a csv file on the current working directory
Privileged_Customers.to_excel("Privileged_Customers.xlsx",index=False)


# Task 2 - Monthly Customer Acquisition Rate from Oct 2018 - Oct 2019

contracts.dtypes
Product_Family = contracts[contracts['Product'] == 'FAMILY'] 
Product_Active = Product_Family[Product_Family['Contract status'] == 'ACTIVE']
Product_Active['Contract Starting Date'] = pd.to_datetime(Product_Active['Contract Starting Date'])
Product_Active['Year'] = Product_Active['Contract Starting Date'].dt.year
Product_Active = Product_Active[Product_Active['Year'].isin([2018,2019])]
Product_Active['Year_Month'] = Product_Active['Contract Starting Date'].dt.to_period('M')
Term = ['2018-09','2018-10','2018-11','2018-12','2019-01','2019-02','2019-03','2019-04','2019-05','2019-06',
        '2019-07','2019-08','2019-09', '2019-10']
Term1 = ['2018-09','2018-10','2018-11','2018-12','2019-01','2019-02','2019-03','2019-04','2019-05','2019-06',
        '2019-07','2019-08','2019-09']
Term2 = ['2018-10','2018-11','2018-12','2019-01','2019-02','2019-03','2019-04','2019-05','2019-06',
        '2019-07','2019-08','2019-09','2019-10']

Product_Active['Year_Month'] = Product_Active['Year_Month'].astype(str)

Product_Active = Product_Active[Product_Active['Year_Month'].isin(Term)]
New_Customer = pd.DataFrame()
for i in enumerate(Term1):
    for j in enumerate(Term2): 
       a = Product_Active[Product_Active['Year_Month'].isin(i)]
       b = Product_Active[Product_Active['Year_Month'].isin(j)]
       x = a['Customer Id'].unique()
       y = b['Customer Id'].unique()
       New = b[b['Customer Id'].isin(a['Customer Id'])].drop_duplicates()
       New_Customer = New_Customer.append(New, ignore_index = True)
       
New_Cust = New_Customer.iloc[:,[0,7]]
New_Cust['Year_Month'].astype(str)
Cust_Count = New_Cust.groupby(['Year_Month'],as_index=False).agg({'Customer Id': "count"})

Pivot_Result = pd.pivot_table(Product_Active,index=['Year_Month'],values=['Customer Id'],aggfunc=['count']).reset_index()
Pivot_Result.to_csv("Pivot_Result.csv",index=False)

New_Customer = New_Customer.sort_values('Year_Month',ascending=True).reset_index()

New_Customer = New_Customer.iloc[:,1:5]

Customer_Unique = pd.DataFrame()

MCAR = pd.DataFrame()

Customer_Unique = Customer_Unique.assign(MCAR = lambda x: Cust_Count['Customer Id'] 
                               / Pivot_Result[('count', 'Customer Id')])

Customer_Unique = Customer_Unique.iloc[0:13,:]

Customer_Unique['Year_Month'] = Term2

Customer_Unique = Customer_Unique.reindex(columns=['Year_Month','MCAR'])

plt.plot(Customer_Unique['Year_Month'],Customer_Unique['MCAR'], color = 'orange', linestyle='dashed', marker='o', linewidth=2, markerfacecolor='red', markersize=12)
plt.xlabel("Timespan",fontsize=15)
plt.ylabel("MCAR",fontsize=15)
plt.title("Monthly Customer Aquisition Ratio from Oct-2018 to Oct-2019",fontsize=20)
plt.show()

# Task 3 - Finding the best KPI's for extending the fuel gas stations 

fuel_trans['Transaction Amount (Euro)'] = fuel_trans['Transaction Amount (Euro)'].str.replace(",",".")
fuel_trans['Transaction Quantity'] = fuel_trans['Transaction Quantity'].str.replace(",",".")
summary = fuel_trans.describe(include='all')

fuel_trans['Gasoline Tipology'].unique()
fuel_trans['Gasoline Tipology'].nunique()

fuel_trans['Gasoline Tipology'] = fuel_trans['Gasoline Tipology'].str.replace("DIESEL","Diesel")
fuel_trans['Transaction Amount (Euro)'] = fuel_trans['Transaction Amount (Euro)'].astype(float)
fuel_trans['Transaction Quantity'] = fuel_trans['Transaction Quantity'].astype(float)

fuel_trans_Gasoline_Performance = fuel_trans.groupby(['Gasoline Tipology'],as_index=False).agg({'Transaction Quantity': "sum"})

Gasoline_Dispensed_Litres = fuel_trans_Gasoline_Performance.sort_values('Transaction Quantity', ascending = False)

fuel_trans_Gasoline_Cost = fuel_trans.groupby(['Gasoline Tipology'],as_index=False).agg({'Transaction Amount (Euro)': "sum"})

Gasoline_Cost = fuel_trans_Gasoline_Cost.sort_values('Transaction Amount (Euro)', ascending = False)

Target_Tipology = pd.merge(Gasoline_Dispensed_Litres, Gasoline_Cost, on='Gasoline Tipology', how='inner')
       
Target_Tipology = Target_Tipology.assign(AQ_Ratio = lambda x: Target_Tipology['Transaction Amount (Euro)'] 
                               / Target_Tipology['Transaction Quantity'])

fuel_trans['Transaction Date'] = pd.to_datetime(fuel_trans['Transaction Date'] + ' ' + fuel_trans['Transaction Date Timestamp'])

fuel_trans['Year'] = fuel_trans['Transaction Date'].dt.year

fuel_trans['Month'] = fuel_trans['Transaction Date'].dt.month

fuel_trans['Transaction Date'].dt.month.value_counts()

fuel_trans_Nov = fuel_trans[fuel_trans['Month'].isin([11])]
       
fuel_trans = fuel_trans.sort_values('Transaction Date', ascending = True)  

fuel_trans_Geo = fuel_trans_Nov.groupby(['Gas Station Zip Code'],as_index=False).agg({'Gasoline Tipology': "count", 'Transaction Amount (Euro)': "sum", 'Transaction Quantity': "sum", 'Transaction Date': "count", 'Customer Id': "nunique" })

fuel_trans_Geo_Target = fuel_trans_Geo.sort_values('Transaction Amount (Euro)', ascending = False).reset_index()

fuel_trans_Geo_Target.drop(['index'], axis = 1, inplace = True)

fuel_trans_Geo_Target = fuel_trans_Geo_Target.rename(columns={"Gasoline Tipology": "Gasoline Tipology Count", "Transaction Amount (Euro)": "Transaction Amount (Euro) Sum","Transaction Quantity": "Transaction Quantity Sum","Transaction Date": "No of Transactions","Customer Id": "No of Unique Customers" })

fuel_trans_Geo_Target = fuel_trans_Geo_Target[fuel_trans_Geo_Target['Transaction Amount (Euro) Sum'] > 5000]

sns.catplot(x='Gas Station Zip Code', y='Transaction Amount (Euro) Sum', height=4, data=fuel_trans_Geo_Target, kind="bar", order=fuel_trans_Geo_Target['Gas Station Zip Code'])
plt.title('Target Geo Locations', fontsize=20)

df4 = fuel_trans_Geo_Target.sort_values('No of Unique Customers', ascending = False).reset_index()
sns.catplot(x='Gas Station Zip Code', y='No of Unique Customers', height=4, data=df4, kind="bar", order=df4['Gas Station Zip Code'])
plt.title('Target Geo Locations-1', fontsize=20)

fuel_trans_Geo_Target.to_csv("fuel_trans_Geo_Target.csv",index=False)



      
       
       