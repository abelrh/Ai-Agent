
import json
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq


# GEMINI_API_KEY = "AQ.Ab8RN6K4SdIAAgqjL0fFNTQRqLvj_5hDfN28IqLp8t5WzboFqg" 

# دالة تحليل السؤال وتحويله لقرار منظم عبر JSON
def ask_ai_agent(user_query, df_columns, chat_history):
    # llm = ChatGoogleGenerativeAI(api_key=GEMINI_API_KEY, model="gemini-2.5-flash", temperature=0)
    llm = ChatGroq(api_key="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",model_name="llama-3.3-70b-versatile",temperature=0.3)
    system_prompt = """
    You are an expert Data Analysis AI Agent. You are having a conversation with a user about their dataset.
    Available columns in the dataset: {columns}
    
    Analyze the user's latest query considering the chat history. They might say "change it to a pie chart" or "what is the sum of it?", so use the history to understand context.
    
    Return ONLY a JSON object with the following keys. Do not include markdown like ```json ... ```, just the raw JSON string.
    
    JSON Structure:
    {{
        "type": "chart" or "text",
        "operation": "sum" or "count" or "none",
        "target_column": "the column name to calculate sum/count on",
        "group_by_column": "the column name to group by (if applicable, else null)",
        "chart_type": "bar" or "pie" or "line" or "area" or "funnel" or "treemap" or "none"
    }}
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{query}")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"columns": list(df_columns), "query": user_query, "chat_history": chat_history})
    
    try:
        cleaned_content = response.content.strip().replace("```json", "").replace("```", "")
        return json.loads(cleaned_content)
    except Exception:
        return None

# دالة التفسير التلقائي المباشر للرسم البياني
def generate_ai_insights(df_summary, operation, target_col, group_col):
    # llm = ChatGoogleGenerativeAI(api_key=GEMINI_API_KEY, model="gemini-2.5-flash", temperature=0.7)
    llm = ChatGroq(api_key="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",model_name="llama-3.3-70b-versatile",temperature=0.7)
    data_str = df_summary.head(10).to_string()
    
    prompt = f"""
    You are a Senior Data Analyst. Write a brief, professional executive summary (2-3 sentences max) in Arabic based on this data summary.
    The operation performed was '{operation}' on column '{target_col}' grouped by '{group_col}'.
    Data:
    {data_str}
    
    Highlight the highest/lowest points or any interesting trend. Keep it business-oriented and helpful.
    """
    response = llm.invoke(prompt)
    return response.content

# دالة توليد نصائح استراتيجية ومخصصة لزيادة المبيعات
def generate_sales_recommendations(df, target_col, group_col):
    # llm = ChatGoogleGenerativeAI(api_key=GEMINI_API_KEY, model="gemini-2.5-flash", temperature=0.7)
    llm = ChatGroq(api_key="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",model_name="llama-3.3-70b-versatile",temperature=0.7)
    
    summary_df = df.groupby(group_col)[target_col].sum().reset_index()
    top_performer = summary_df.loc[summary_df[target_col].idxmax()]
    lowest_performer = summary_df.loc[summary_df[target_col].idxmin()]
    
    data_context = f"""
    - الفئة الأعلى مبيعاً هي '{top_performer[group_col]}' بإجمالي {top_performer[target_col]:,.0f}.
    - الفئة الأقل مبيعاً هي '{lowest_performer[group_col]}' بإجمالي {lowest_performer[target_col]:,.0f}.
    """
    
    prompt = f"""
    You are an expert Business Consultant. Based on the following actual sales data summary, provide 12 actionable, specific recommendations in Arabic to boost sales.
    Data Context:
    {data_context}
    
    Do not give generic advice. Mention the specific categories from the data and tell the user exactly what to do (e.g., cross-selling, dynamic pricing, or promotional campaigns).
    Format the output with clear bullet points.
    """
    response = llm.invoke(prompt)
    return response.content