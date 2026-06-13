import pandas as pd
import plotly.express as px

# دالة الحسابات الرقمية والتجميع
def calculate_text_metric(df, ai_response):
    operation = ai_response.get("operation")
    target_col = ai_response.get("target_column")
    group_col = ai_response.get("group_by_column")
    
    if target_col not in df.columns:
        return None
        
    if operation == "sum":
        if group_col and group_col in df.columns:
            return df.groupby(group_col)[target_col].sum().reset_index()
        return df[target_col].sum()
            
    elif operation == "count":
        if group_col and group_col in df.columns:
            return df.groupby(group_col)[target_col].count().reset_index()
        return df[target_col].count()
            
    return None

# دالة رسم المخططات البيانية الاحترافية مع تفعيل الأرقام والألوان والـ Area
def generate_plotly_chart(plot_df, ai_response):
    chart_type = ai_response.get("chart_type")
    operation = ai_response.get("operation")
    target_col = ai_response.get("target_column")
    group_col = ai_response.get("group_by_column")
    
    title_text = f"{operation.capitalize()} of {target_col} by {group_col}"
    color_palette = px.colors.qualitative.Prism

    # 1. Bar Chart
    if chart_type == "bar": 
        fig = px.bar(plot_df, x=group_col, y=target_col, title=title_text, color=group_col, color_discrete_sequence=color_palette, text=target_col)
        fig.update_traces(textposition='outside', texttemplate='%{text:,.0f}')
        return fig
        
    # 2. Pie Chart
    elif chart_type == "pie": 
        fig = px.pie(plot_df, names=group_col, values=target_col, title=title_text, color_discrete_sequence=color_palette)
        fig.update_traces(textinfo='percent+label+value', texttemplate='%{label}: %{value:,.0f} (%{percent})')
        return fig
        
    # 3. Line Chart
    elif chart_type == "line": 
        fig = px.line(plot_df, x=group_col, y=target_col, title=title_text, markers=True, text=target_col)
        fig.update_traces(textposition='top center', texttemplate='%{text:,.0f}')
        return fig

    # 4. Area Chart (المضافة حديثاً)
    elif chart_type == "area":
        fig = px.area(plot_df, x=group_col, y=target_col, title=title_text, markers=True, text=target_col)
        fig.update_traces(textposition='top center', texttemplate='%{text:,.0f}')
        return fig
        
    # 5. Funnel Chart
    elif chart_type == "funnel": 
        fig = px.funnel(plot_df, x=target_col, y=group_col, title=title_text, color=group_col, color_discrete_sequence=color_palette)
        fig.update_traces(textinfo='value+percent initial')
        return fig
        
    # 6. Treemap
    elif chart_type == "treemap": 
        fig = px.treemap(plot_df, path=[group_col], values=target_col, title=title_text, color=group_col, color_discrete_sequence=color_palette)
        fig.update_traces(textinfo="label+value")
        return fig
        
    return None
