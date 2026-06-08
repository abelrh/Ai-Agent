import pandas as pd

def clean_dataset(df):
    cleaned_df = df.copy()
    
    # 1. إزالة الأعمدة والصفوف الفارغة تماماً
    cleaned_df.dropna(how='all', axis=1, inplace=True)
    cleaned_df.dropna(how='all', axis=0, inplace=True)
    
    # 2. تنظيف البيانات بناءً على نوع كل عمود
    for col in cleaned_df.columns:
        if cleaned_df[col].dtype == 'object':
            cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
            
            # محاولة تحويل النصوص الرقمية (مثل الأسعار المخزنة كنص) إلى أرقام
            converted_col = pd.to_numeric(cleaned_df[col].str.replace(r'[^\d\.]', '', regex=True), errors='ignore')
            if converted_col.dtype in ['int64', 'float64']:
                cleaned_df[col] = converted_col
            else:
                cleaned_df[col].fillna('Unknown', inplace=True)
                
        elif cleaned_df[col].dtype in ['int64', 'float64']:
            cleaned_df[col].fillna(0, inplace=True)
            
    return cleaned_df