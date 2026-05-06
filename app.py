
import sqlite3
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Sales & Customer Insights Dashboard Pro", page_icon="📊", layout="wide")
DATA_PATH = Path("data/sales_customer_data.csv")
DB_PATH = Path("data/sales_dashboard.db")
REQUIRED_COLUMNS = {"Order_ID","Order_Date","Customer_ID","Customer_Name","Region","State","City","Product_Category","Product_Name","Quantity","Unit_Price","Discount","Sales","Cost","Profit","Payment_Mode"}

def clean_data(df):
    df=df.copy(); df.columns=[c.strip().replace(' ','_') for c in df.columns]
    if 'Order_Date' in df.columns: df['Order_Date']=pd.to_datetime(df['Order_Date'],errors='coerce')
    for col in ['Quantity','Unit_Price','Discount','Sales','Cost','Profit']:
        if col in df.columns: df[col]=pd.to_numeric(df[col],errors='coerce').fillna(0)
    return df.dropna(subset=['Order_Date']) if 'Order_Date' in df.columns else df

def load_default_data(): return clean_data(pd.read_csv(DATA_PATH))
def save_to_sqlite(df):
    conn=sqlite3.connect(DB_PATH); df.to_sql('sales_orders',conn,if_exists='replace',index=False); conn.close()
def load_from_sqlite():
    if not DB_PATH.exists(): save_to_sqlite(load_default_data())
    conn=sqlite3.connect(DB_PATH); df=pd.read_sql_query('SELECT * FROM sales_orders',conn); conn.close(); return clean_data(df)
def validate_columns(df): return REQUIRED_COLUMNS - set(df.columns)
def format_currency(v): return f"₹{v:,.0f}"

def get_business_recommendations(df):
    rec=[]; total_sales=df['Sales'].sum(); total_profit=df['Profit'].sum(); margin=(total_profit/total_sales*100) if total_sales else 0
    region_sales=df.groupby('Region')['Sales'].sum().sort_values(ascending=False)
    cat_profit=df.groupby('Product_Category')['Profit'].sum().sort_values(ascending=False)
    pay_sales=df.groupby('Payment_Mode')['Sales'].sum().sort_values(ascending=False)
    rec.append(f"Focus on {region_sales.index[0]} region because it contributes the highest revenue of {format_currency(region_sales.iloc[0])}.")
    rec.append(f"Improve marketing and offers in {region_sales.index[-1]} region because it currently has the lowest revenue of {format_currency(region_sales.iloc[-1])}.")
    rec.append(f"{cat_profit.index[0]} is the most profitable category with {format_currency(cat_profit.iloc[0])} profit. Maintain stock availability for this category.")
    rec.append(f"Review pricing, promotions, or inventory for {cat_profit.index[-1]}, as it is the lowest profit contributor.")
    rec.append(f"{pay_sales.index[0]} is the highest payment mode by sales value. Checkout flow can be optimized around this mode.")
    if margin < 15: rec.append('Overall profit margin is below 15%, so discounting and product-level cost should be reviewed.')
    elif margin < 25: rec.append('Profit margin is healthy, but low-margin categories should still be monitored.')
    else: rec.append('Profit margin is strong. The business can consider scaling top-performing products and regions.')
    monthly=df.groupby(df['Order_Date'].dt.to_period('M'))['Sales'].sum().reset_index(); monthly['Order_Date']=monthly['Order_Date'].astype(str)
    if len(monthly)>=2:
        last,prev=monthly.iloc[-1]['Sales'],monthly.iloc[-2]['Sales']; growth=((last-prev)/prev*100) if prev else 0
        rec.append(f"Sales {'increased' if growth>=0 else 'declined'} by {abs(growth):.1f}% compared with the previous month. {'Continue the current sales strategy.' if growth>=0 else 'Investigate region/category-level drop.'}")
    return rec

def generate_powerbi_export(df):
    Path('exports').mkdir(exist_ok=True)
    df.to_csv('exports/powerbi_sales_customer_clean.csv',index=False)
    pd.DataFrame({'Total_Sales':[df['Sales'].sum()],'Total_Profit':[df['Profit'].sum()],'Total_Orders':[df['Order_ID'].nunique()],'Average_Order_Value':[df['Sales'].sum()/max(df['Order_ID'].nunique(),1)],'Profit_Margin_Percentage':[(df['Profit'].sum()/df['Sales'].sum()*100) if df['Sales'].sum() else 0]}).to_csv('exports/powerbi_kpi_summary.csv',index=False)
    df.groupby('Region',as_index=False)[['Sales','Profit']].sum().to_csv('exports/powerbi_region_summary.csv',index=False)
    df.groupby('Product_Category',as_index=False)[['Sales','Profit']].sum().to_csv('exports/powerbi_category_summary.csv',index=False)

st.title('📊 Sales & Customer Insights Dashboard Pro')
st.write('Business Analyst project with CSV/Excel upload, SQLite database option, Power BI export, and AI-style business recommendations.')
with st.sidebar:
    st.header('Data Source')
    data_source=st.radio('Choose data source',['Default Sample Data','Upload CSV/Excel','SQLite Database'])
    uploaded_file = st.file_uploader('Upload sales data', type=['csv','xlsx']) if data_source=='Upload CSV/Excel' else None

if data_source=='Upload CSV/Excel' and uploaded_file is not None:
    df=clean_data(pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file))
elif data_source=='SQLite Database': df=load_from_sqlite()
else: df=load_default_data()
missing=validate_columns(df)
if missing: st.error(f"Missing required columns: {', '.join(sorted(missing))}"); st.stop()
save_to_sqlite(df); generate_powerbi_export(df)
with st.sidebar:
    st.header('Filters')
    regions=st.multiselect('Select Region',sorted(df['Region'].unique()),default=sorted(df['Region'].unique()))
    cats=st.multiselect('Select Product Category',sorted(df['Product_Category'].unique()),default=sorted(df['Product_Category'].unique()))
    pays=st.multiselect('Select Payment Mode',sorted(df['Payment_Mode'].unique()),default=sorted(df['Payment_Mode'].unique()))
filtered=df[df['Region'].isin(regions)&df['Product_Category'].isin(cats)&df['Payment_Mode'].isin(pays)]
if filtered.empty: st.warning('No data available for selected filters.'); st.stop()
total_sales=filtered['Sales'].sum(); total_profit=filtered['Profit'].sum(); total_orders=filtered['Order_ID'].nunique(); avg=total_sales/max(total_orders,1); margin=(total_profit/total_sales*100) if total_sales else 0
c1,c2,c3,c4,c5=st.columns(5); c1.metric('Total Sales',format_currency(total_sales)); c2.metric('Total Profit',format_currency(total_profit)); c3.metric('Total Orders',f'{total_orders:,}'); c4.metric('Avg Order Value',format_currency(avg)); c5.metric('Profit Margin',f'{margin:.2f}%')
st.divider()
monthly=filtered.groupby(filtered['Order_Date'].dt.to_period('M'))['Sales'].sum().reset_index(); monthly['Order_Date']=monthly['Order_Date'].astype(str)
col1,col2=st.columns(2)
with col1: st.subheader('Monthly Sales Trend'); st.plotly_chart(px.line(monthly,x='Order_Date',y='Sales',markers=True),use_container_width=True)
with col2: st.subheader('Profit by Product Category'); st.plotly_chart(px.bar(filtered.groupby('Product_Category',as_index=False)[['Sales','Profit']].sum(),x='Product_Category',y='Profit',text_auto=True),use_container_width=True)
col3,col4=st.columns(2)
with col3: st.subheader('Regional Sales Share'); st.plotly_chart(px.pie(filtered.groupby('Region',as_index=False)['Sales'].sum(),names='Region',values='Sales',hole=.35),use_container_width=True)
with col4: st.subheader('Sales by Payment Mode'); st.plotly_chart(px.bar(filtered.groupby('Payment_Mode',as_index=False)['Sales'].sum().sort_values('Sales',ascending=False),x='Payment_Mode',y='Sales',text_auto=True),use_container_width=True)
col5,col6=st.columns(2)
with col5: st.subheader('Top 10 Products by Sales'); st.plotly_chart(px.bar(filtered.groupby('Product_Name',as_index=False)['Sales'].sum().sort_values('Sales',ascending=False).head(10),x='Sales',y='Product_Name',orientation='h',text_auto=True),use_container_width=True)
with col6: st.subheader('Top 10 Customers by Sales'); st.plotly_chart(px.bar(filtered.groupby('Customer_Name',as_index=False)['Sales'].sum().sort_values('Sales',ascending=False).head(10),x='Sales',y='Customer_Name',orientation='h',text_auto=True),use_container_width=True)
st.divider(); st.header('AI-Style Business Recommendations')
for rec in get_business_recommendations(filtered): st.success(rec)
st.divider(); st.header('Power BI Export'); st.write('The app automatically creates Power BI-ready CSV files inside the `exports` folder.')
st.download_button('Download Clean Power BI Dataset', filtered.to_csv(index=False).encode('utf-8'), 'powerbi_sales_customer_clean.csv', 'text/csv')
st.divider(); st.header('Filtered Dataset'); st.dataframe(filtered,use_container_width=True)
st.download_button('Download Filtered Report CSV', filtered.to_csv(index=False).encode('utf-8'), 'filtered_sales_report.csv','text/csv')
