import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(layout="wide", page_title="Dashboard _ Hệ thống BI _ Báo cáo HTVH TCT")

sheet_url = "https://docs.google.com/spreadsheets/d/1Ex_aUYeS-6fvfvpuGZPKQbMbaRmFpqjoYevJZedvnWA/export?format=csv&gid=0"

@st.cache_data
def load_data():
    df = pd.read_csv(sheet_url)
    new_header = df.iloc[1].astype(str).tolist()
    df = df[2:].copy()
    df.columns = new_header
    df.rename(columns={df.columns[0]: "HT"}, inplace=True)
    df["HT"] = df["HT"].astype(str)
    for col in df.columns[1:]:
        if col and isinstance(df[col], pd.Series):
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

df = load_data()

colors = {
    "Đã xử lý - SLA": "#87CEFA",
    "Đã xử lý - Không SLA": "#003F88",
    "Chưa xử lý - SLA": "#FFCC99",
    "Chưa xử lý - Không SLA": "#FF9933"
}

st.markdown("""
    <style>
    .stDataFrame thead tr th {
        background-color: #003F88;
        color: white;
    }
    .stDataFrame tbody tr:nth-child(even) {
        background-color: #E6F0FA;
    }
    .block-container {
        padding-top: 2rem;
    }
    .centered-title {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 800;
        color: #003F88;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='centered-title'>Dashboard _ Hệ thống BI _ Báo cáo HTVH TCT</div>", unsafe_allow_html=True)

categories = [
    ("Tổng yêu cầu phát sinh", [0, 2, 3, 4, 5]),
    ("Lỗi phần mềm", [0, 6, 7, 8, 9]),
    ("Yêu cầu hỗ trợ", [0, 10, 11, 12, 13]),
    ("Yêu cầu hiệu chỉnh/thêm chức năng", [0, 14, 15, 16, 17])
]

for cat, cols in categories:
    st.subheader(cat)

    sub_df = df.iloc[:, cols].copy()
    sub_df.columns = ["HT", "Đã xử lý SL", "Đã xử lý SLA", "Chưa xử lý SL", "Chưa xử lý SLA"]
    sub_df = sub_df[sub_df["HT"].str.lower() != "tổng cộng"]

    for col in sub_df.columns[1:]:
        sub_df[col] = pd.to_numeric(sub_df[col], errors="coerce")

    sub_df["Đã xử lý Không SLA"] = sub_df["Đã xử lý SL"] - sub_df["Đã xử lý SLA"]
    sub_df["Chưa xử lý Không SLA"] = sub_df["Chưa xử lý SL"] - sub_df["Chưa xử lý SLA"]

    # Thêm dòng tổng cộng
    total_row = pd.DataFrame(sub_df.iloc[:, 1:].sum()).T
    total_row.insert(0, "HT", "Tổng cộng")
    sub_df = pd.concat([sub_df, total_row], ignore_index=True)

    ht_short = sub_df["HT"].str.split("-").str[0].str.strip().tolist()
    x = np.arange(len(ht_short))
    bar_width = 0.35

    values = [
        sub_df["Đã xử lý SLA"].sum(),
        sub_df["Đã xử lý Không SLA"].sum(),
        sub_df["Chưa xử lý SLA"].sum(),
        sub_df["Chưa xử lý Không SLA"].sum()
    ]

    pie = go.Figure(data=[go.Pie(
        labels=list(colors.keys()),
        values=values,
        marker=dict(colors=list(colors.values())),
        textinfo='percent',
        hoverinfo='label+value+percent',
        showlegend=False
    )])

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        st.dataframe(sub_df, use_container_width=True, height=450)

    with col2:
        st.plotly_chart(pie, use_container_width=True)

    with col3:
        da_total = sub_df["Đã xử lý SL"].copy()
        chua_total = sub_df["Chưa xử lý SL"].copy()
        da_total[da_total == 0] = 1
        chua_total[chua_total == 0] = 1

        da_sla_pct = sub_df["Đã xử lý SLA"] / da_total * 100
        da_khong_sla_pct = sub_df["Đã xử lý Không SLA"] / da_total * 100
        chua_sla_pct = sub_df["Chưa xử lý SLA"] / chua_total * 100
        chua_khong_sla_pct = sub_df["Chưa xử lý Không SLA"] / chua_total * 100

        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(x=x - bar_width/2, y=chua_sla_pct,
                                 marker_color=colors["Chưa xử lý - SLA"], width=bar_width,
                                 customdata=sub_df["Chưa xử lý SLA"],
                                 hovertemplate="%{y:.2f}%<br>Số lượng: %{customdata}<extra></extra>",
                                 showlegend=False))

        fig_bar.add_trace(go.Bar(x=x - bar_width/2, y=chua_khong_sla_pct, base=chua_sla_pct,
                                 marker_color=colors["Chưa xử lý - Không SLA"],
                                 width=bar_width, customdata=sub_df["Chưa xử lý Không SLA"],
                                 hovertemplate="%{y:.2f}%<br>Số lượng: %{customdata}<extra></extra>",
                                 showlegend=False))

        fig_bar.add_trace(go.Bar(x=x + bar_width/2, y=da_sla_pct,
                                 marker_color=colors["Đã xử lý - SLA"], width=bar_width,
                                 customdata=sub_df["Đã xử lý SLA"],
                                 hovertemplate="%{y:.2f}%<br>Số lượng: %{customdata}<extra></extra>",
                                 showlegend=False))

        fig_bar.add_trace(go.Bar(x=x + bar_width/2, y=da_khong_sla_pct, base=da_sla_pct,
                                 marker_color=colors["Đã xử lý - Không SLA"],
                                 width=bar_width, customdata=sub_df["Đã xử lý Không SLA"],
                                 hovertemplate="%{y:.2f}%<br>Số lượng: %{customdata}<extra></extra>",
                                 showlegend=False))

        fig_bar.update_layout(
            barmode="stack",
            xaxis=dict(tickmode='array', tickvals=x, ticktext=ht_short, title="Hệ thống phần mềm"),
            yaxis_title="Tỷ lệ phần trăm (%)",
            height=500,
            yaxis=dict(range=[0, 100])
        )

        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("""
        <div style="display: flex; justify-content: center; flex-wrap: wrap; margin-top: 10px; font-size: 13px;">
            <div style="background-color: #003F88; color: white; padding: 4px 10px; margin: 2px; border-radius: 4px;">Đã xử lý - Không SLA</div>
            <div style="background-color: #87CEFA; color: black; padding: 4px 10px; margin: 2px; border-radius: 4px;">Đã xử lý - SLA</div>
            <div style="background-color: #FF9933; color: black; padding: 4px 10px; margin: 2px; border-radius: 4px;">Chưa xử lý - Không SLA</div>
            <div style="background-color: #FFCC99; color: black; padding: 4px 10px; margin: 2px; border-radius: 4px;">Chưa xử lý - SLA</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
