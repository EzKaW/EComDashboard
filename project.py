import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

all_df = pd.read_csv("all_data.csv")

datetime_column = ["order_purchase_timestamp"]
for column in datetime_column:
    all_df[column] = pd.to_datetime(all_df[column])

st.header('E-Commerce Public Dashboard :shopping_bags:')

st.subheader("Best & Worst Product Revenue")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sum_order_items_df_desc = all_df.groupby("product_category_name_english").price.sum().sort_values(ascending=False).reset_index()
sum_order_items_df_asc = all_df.groupby("product_category_name_english").price.sum().sort_values(ascending=True).reset_index()

sns.barplot(x="price", y="product_category_name_english", data=sum_order_items_df_desc.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Revenue", fontsize=30)
ax[0].set_title("Best Performing Product", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)
ax[0].xaxis.set_major_formatter(ticker.EngFormatter())

sns.barplot(x="price", y="product_category_name_english", data=sum_order_items_df_asc.head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Revenue", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
ax[1].xaxis.set_major_formatter(ticker.EngFormatter())

st.pyplot(fig)

st.write("\n")

st.subheader("Transaction Volumes by City & State")

customer_city_late = all_df['order_status'].value_counts().reset_index()
result = customer_city_late[customer_city_late['order_status'] == "On Time"]
result2 = customer_city_late[customer_city_late['order_status'] == "Late"]


col1, col2 = st.columns(2)

with col1:
    count_value_OT = result['count'].values[0]
    st.metric("Total Order On Time", value=count_value_OT)

with col2:
    count_value_L = result2['count'].values[0]
    st.metric("Total Order Late", value=count_value_L)

customer_city_counts = all_df['customer_city'].value_counts().reset_index()
customer_city_counts.columns = ['City', 'Count']

fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(
    x="Count",
    y="City",
    data=customer_city_counts.head(5),
    palette=colors,
    ax=ax
)

ax.set_title("Top 5 Customer Counts by City", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

st.write("\n")

customer_city_counts = all_df['customer_state'].value_counts().reset_index()
customer_city_counts.columns = ['State', 'Count']

fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(
    x="Count",
    y="State",
    data=customer_city_counts.head(5),
    palette=colors,
    ax=ax
)

ax.set_title("Top 5 Customer Counts by State", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

st.write("\n")

st.subheader("Best Customer Based on RFM Parameters")

def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max", #mengambil tanggal order terakhir
        "order_id": "nunique",
        "price": "sum"
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]

    datetime_column = ["max_order_timestamp"]
    for column in datetime_column:
        rfm_df[column] = pd.to_datetime(rfm_df[column])
    
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df

rfm_df = create_rfm_df(all_df)

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "BRL", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)

def abbreviate_customer_id(customer_id):
    return customer_id[:4]  

rfm_df['abbreviated_customer_id'] = all_df['customer_id'].apply(abbreviate_customer_id)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

sns.barplot(y="recency", x="abbreviated_customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id (abr)", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)

sns.barplot(y="frequency", x="abbreviated_customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id (abr)", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)

sns.barplot(y="monetary", x="abbreviated_customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id (abr)", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)

st.pyplot(fig)

st.caption('Copyright (c) EKW 2023')