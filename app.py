import streamlit as st
import pandas as pd
from langchain_core.messages import HumanMessage, AIMessage

# استيراد كافة الـ Modules من ملفاتك الجانبية
from data_cleaner import clean_dataset
from ai_agent import ask_ai_agent, generate_ai_insights, generate_sales_recommendations
from charts_builder import calculate_text_metric, generate_plotly_chart

st.set_page_config(page_title="Advanced AI Data Agent", layout="wide")
st.title("🤖 📊 Advanced AI Data Analytics Chatbot")

# إدارة حالة الذاكرة والتحكم في الأزرار في الـ Session State
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "display_messages" not in st.session_state:
    st.session_state.display_messages = []
if "show_recommendations" not in st.session_state:
    st.session_state.show_recommendations = {}  # لحفظ حالة أزرار النصائح بشكل دائم

# رفع الملف
uploaded_file = st.file_uploader("اختر ملف البيانات (CSV أو Excel)", type=["csv", "xlsx"])

if uploaded_file is not None:
    if "df" not in st.session_state:
        raw_df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        st.session_state.df = clean_dataset(raw_df)
        st.success("تم رفع وتنظيف البيانات بنجاح!")

    df = st.session_state.df
    
    with st.expander("📋 معاينة البيانات المتوفرة"):
        st.dataframe(df.head(5))
        
    st.write("---")
    
    # 1. عرض المحادثات السابقة والرسومات والأزرار (معدل لضمان بقاء الأزرار حية دائماً في الواجهة)
    for idx, msg in enumerate(st.session_state.display_messages):
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if "chart" in msg and msg["chart"] is not None:
                st.plotly_chart(msg["chart"], use_container_width=True, key=f"history_chart_{idx}")
            
            # 🚀 نقل كود الزرار إلى هنا لضمان عمله وثباته في الواجهة دائماً
            if msg["role"] == "assistant" and "target_col" in msg and "group_col" in msg:
                target_col = msg["target_col"]
                group_col = msg["group_col"]
                
                # التحقق إذا كان العمود يخص المبيعات
                if any(keyword in target_col.lower() for keyword in ["price", "sales", "revenue", "amount"]):
                    st.write("---")
                    st.info("💡 **هل ترغب في الحصول على استراتيجية مخصصة لزيادة مبيعاتك بناءً على هذه الأرقام؟**")
                    
                    btn_key = f"rec_btn_{idx}"
                    
                    # 🎯 --- تعديل التوسيط المطور هنا ---
                    # إنشاء 3 أعمدة: يمين ويسار كفراغات (نسبة 3:2:3 تعطي توازناً ممتازاً)
                    col1, col2, col3 = st.columns([3, 2, 3])
                    
                    with col2: # وضع الزرار في العمود الأوسط ليظهر بالمنتصف تماماً
                        if st.button("🚀 توليد نصائح استراتيجية لزيادة المبيعات", key=btn_key, use_container_width=True):
                            st.session_state.show_recommendations[btn_key] = True
                    # -----------------------------------
                    
                    # عرض النصائح لو كانت الحالة True (تظهر بكامل عرض الصفحة عادي تحت الزر)
                    if st.session_state.show_recommendations.get(btn_key, False):
                        if "recommendations_text" not in msg:
                            with st.spinner("📊 جاري دراسة سلوك البيانات وتوليد الاستراتيجيات..."):
                                try:
                                    msg["recommendations_text"] = generate_sales_recommendations(df, target_col, group_col)
                                except Exception as e:
                                    msg["recommendations_text"] = f"تعذر استدعاء النصائح بسبب خطأ الكوتا أو الاتصال: {e}"
                        
                        st.markdown("### 🎯 نصائح الـ AI الاستراتيجية لنمو مبيعاتك:")
                        st.markdown(msg["recommendations_text"])
    # استقبال مدخلات الشات التفاعلي الجديد
    if user_query := st.chat_input("اطلب أي تحليل، رسمة بيانية (Bar, Pie, Area...)"):
        
        with st.chat_message("user"):
            st.write(user_query)
        st.session_state.display_messages.append({"role": "user", "content": user_query})
        
        with st.chat_message("assistant"):
            with st.spinner("جاري التفكير وتحليل البيانات..."):
                
                try:
                    ai_decision = ask_ai_agent(user_query, df.columns, st.session_state.chat_history)
                    
                    if ai_decision:
                        operation = ai_decision.get("operation")
                        target_col = ai_decision.get("target_column")
                        group_col = ai_decision.get("group_by_column")
                        
                        result = calculate_text_metric(df, ai_decision)
                        response_text = ""
                        fig = None
                        
                        if result is not None:
                            if ai_decision["type"] == "chart" or ai_decision["chart_type"] != "none":
                                if isinstance(result, pd.DataFrame):
                                    fig = generate_plotly_chart(result, ai_decision)
                                    if fig:
                                        msg_id = len(st.session_state.display_messages)
                                        chart_key = f"live_chart_{target_col}_{group_col}_{ai_decision['chart_type']}_{msg_id}"
                                        st.plotly_chart(fig, use_container_width=True, key=chart_key)
                                        
                                        insights = generate_ai_insights(result, operation, target_col, group_col)
                                        response_text = f"إليك الرسم البياني المطلوب لعلاقة `{target_col}` بـ `{group_col}`.\n\n**📝 التحليل الذكي للبيانات:**\n{insights}"
                                        st.write(response_text)
                                else:
                                    response_text = "لعرض رسم بياني، يرجى طلب التجميع بناءً على فئة معينة."
                                    st.write(response_text)
                            else:
                                if isinstance(result, pd.DataFrame):
                                    st.dataframe(result)
                                    insights = generate_ai_insights(result, operation, target_col, group_col)
                                    response_text = f"إليك البيانات المطلوبة مجمعة:\n\n**📝 التحليل الذكي للبيانات:**\n{insights}"
                                    st.write(response_text)
                                else:
                                    response_text = f"النتيجة لـ {operation} للعمود {target_col} هي: **{result:,}**"
                                    st.write(response_text)
                        else:
                            response_text = "لم أفهم العملية المطلوبة تماماً، يرجى تحديد هل تريد المجموع (Sum) أم العدد (Count) لعمود معين."
                            st.write(response_text)
                            
                        # حفظ البيانات والـ Meta-data في الرسالة لتمريرها للـ Loop الثابت
                        st.session_state.chat_history.append(HumanMessage(content=user_query))
                        st.session_state.chat_history.append(AIMessage(content=response_text))
                        st.session_state.display_messages.append({
                            "role": "assistant", 
                            "content": response_text, 
                            "chart": fig,
                            "target_col": target_col,
                            "group_col": group_col
                        })
                        
                        # عمل Rerun صغير لتثبيت الزرار في مكانه الجديد فورا بعد الاستجابة
                        st.rerun()
                    else:
                        st.write("تعذر تحليل السؤال، يرجى المحاولة مرة أخرى.")
                        
                except Exception as e:
                    if "RESOURCE_EXHAUSTED" in str(e):
                        st.error("⚠️ **لقد نفدت الحصة المجانية (Quota) الخاصة بمفتاح الـ API لـ Gemini اليوم (20 طلب فقط).**")
                        st.info("💡 **الحل الفوري:** يرجى إنشاء مفتاح API جديد من حساب Gmail آخر ووضعه في متغير `GEMINI_API_KEY` داخل ملف `ai_agent.py` لتستطيع إكمال تجربتك فوراً!")
                    else:
                        st.error(f"حدث خطأ غير متوقع أثناء معالجة طلبك: {e}")