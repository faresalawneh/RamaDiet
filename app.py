import streamlit as st
import pandas as pd
import google.generativeai as genai
import json

# ==========================================
# 1. إعداد الواجهة والذاكرة
# ==========================================
st.set_page_config(page_title="RamaDiet", page_icon="🌙", layout="wide")
st.title("🌙 Jordanian RamaDiet")
st.markdown("فصّل وجبتك بالملّي! غيّر الأوزان حسب هدفك، والعدادات بتعطيك الصافي فوراً.")

if 'plan' not in st.session_state:
    st.session_state.plan = None

# ==========================================
# 2. إعداد المفتاح والنموذج
# ==========================================
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel(
    'gemini-2.5-flash', 
    generation_config={"response_mime_type": "application/json"}
)

# ==========================================
# 3. قراءة البيانات
# ==========================================
@st.cache_data
def load_data():
    return pd.read_csv("ramadan_100g.csv")

df = load_data()

# ==========================================
# 4. الشريط الجانبي (بيانات المستخدم)
# ==========================================
st.sidebar.header("📝 بياناتك الشخصية")
age = st.sidebar.number_input("العمر", min_value=10, max_value=100, value=25)
weight = st.sidebar.number_input("الوزن (كغ)", min_value=30.0, max_value=200.0, value=75.0)
height = st.sidebar.number_input("الطول (سم)", min_value=100.0, max_value=250.0, value=175.0)
activity_level = st.sidebar.selectbox("مستوى النشاط", ["خفيف (لا يوجد تمارين)", "متوسط (تمرين خفيف/مشي)", "عالي (تمارين مقاومة/حديد)"])
goal = st.sidebar.selectbox("الهدف في رمضان", ["المحافظة على الوزن", "خسارة الدهون", "بناء العضلات"])

st.sidebar.markdown("---")
# 🔥 الإضافة الجديدة: الحالة الصحية
st.sidebar.header("🏥 الحالة الطبية (إن وجدت)")
health_condition = st.sidebar.text_input("هل تعاني من أي حالة صحية؟ (مثال: السكري، الضغط، حساسية الجلوتين)", "لا يوجد")

st.sidebar.markdown("---")
st.sidebar.header("💡 التبديل الذكي (Smart Swap)")
craving = st.sidebar.text_input("شو الأكلة اللي بتشتهيها؟ (مثال: قطايف، مقالي)", "")

# حساب الترطيب
water_base = weight * 0.033
if "عالي" in activity_level: water_base += 1.0
elif "متوسط" in activity_level: water_base += 0.5
water_cups = int((water_base * 1000) / 250) 

# ==========================================
# 5. زر توليد الخطة والاتصال بالذكاء الاصطناعي
# ==========================================
if st.button("🚀 اضرب يا كابتن"):
    with st.spinner("جاري تحضير المنيو الأردني الشامل ومراعاة حالتك الصحية..."):
        
        suhoor_pool = df[(df['meal_type'].str.contains('Suhoor', na=False, case=False)) | (df['ramadan_role'] == 'Slow-Release Energy')]
        iftar_pool = df[(df['meal_type'].str.contains('Main Course', na=False, case=False)) | (df['ramadan_role'] == 'Lean Protein / Muscle Recovery')]
        
        # أرسلنا عمود السكر والصوديوم عشان النموذج يشوفهم ويقدر يقرر للمرضى
        suhoor_context = suhoor_pool[['food', 'calories', 'protein_g', 'carbs_g', 'sugars_g', 'sodium_mg']].to_string(index=False)
        iftar_context = iftar_pool[['food', 'calories', 'protein_g', 'carbs_g', 'sugars_g', 'sodium_mg']].to_string(index=False)

        # 🔥 البرومبت المعدل يشمل الحالة الصحية كأولوية قصوى
        prompt = f"""
        أنت خبير تغذية رياضي وطاهٍ أردني محترف، ولديك خبرة طبية في التغذية العلاجية. 
        صمم وجبات رمضانية مخصصة بناءً على احتياجات المستخدم الفعلية: 
        - الوزن: {weight} كغ
        - الهدف: {goal}
        - النشاط: {activity_level}
        - الحالة الصحية: {health_condition}
        - المشتهيات: {craving if craving else 'لا يوجد'}
        
        استخدم هذه القوائم فقط:
        قائمة السحور: {suhoor_context}
        قائمة الإفطار: {iftar_context}

        التعليمات الصارمة:
        1. القيود الطبية (أولوية قصوى ومطلقة): بما أن حالة المستخدم هي ({health_condition})، يُمنع منعاً باتاً اختيار أي مكونات تضر بهذه الحالة. 
           - إذا كان يعاني من "السكري"، استبعد تماماً الأطعمة ذات السكر العالي (انظر لعمود sugars_g) والكربوهيدرات البسيطة.
           - إذا كان يعاني من "الضغط"، استبعد الأطعمة ذات الصوديوم العالي (انظر لعمود sodium_mg).
           - اذكر كيف راعيت مرضه في حقل "السبب".
        2. التخصيص حسب الهدف: قم بتقدير احتياج المستخدم من الأوزان (إذا كان الهدف بناء عضلات، أعطه أوزان كبيرة، وإذا خسارة دهون أعطه أوزان أقل).
        3. الروح الأردنية المألوفة (مقلوبة صحية، مجدرة، قلاية بندورة...).
        4. قسم الوجبة لمكونات منفصلة. أعطِ لكل مكون وزناً *يتناسب مع هدف المستخدم* بالغرامات واسم الحصة.
        
        قم بإرجاع هذا الهيكل (JSON) فقط:
        {{
            "smart_swap_advice": "نصيحة أردنية للبديل الصحي تراعي مرضه (إن وجدت)",
            "suhoor": {{
                "meal_name": "اسم الوجبة", "reason": "السبب للرياضي (مع ذكر كيف تلائم حالته الصحية)",
                "ingredients": [
                    {{"name": "جبنة قريش/بيض (الحصة)", "default_weight_g": 150, "calories": 150, "protein": 20, "carbs": 5}}
                ]
            }},
            "iftar": {{
                "meal_name": "اسم الوجبة", "reason": "السبب للرياضي (مع ذكر كيف تلائم حالته الصحية)",
                "ingredients": [
                    {{"name": "دجاج أو لحم (الحصة)", "default_weight_g": 300, "calories": 495, "protein": 75, "carbs": 0}}
                ]
            }},
            "grocery_list": ["غرض 1", "غرض 2"]
        }}
        """
        try:
            response = model.generate_content(prompt)
            st.session_state.plan = json.loads(response.text)
            st.rerun() 
        except Exception as e:
            st.error(f"حدث خطأ أثناء الاتصال بالذكاء الاصطناعي: {e}")

# ==========================================
# 6. عرض الخطة التفاعلية
# ==========================================
if st.session_state.plan:
    plan = st.session_state.plan
    
    st.success("تم تجهيز خطتك بنجاح! 🎛️ **تقدر هسه تعدل أوزان الأكل تحت وتشوف السعرات بتتغير لحالها**")
    
    if craving and plan.get("smart_swap_advice"):
        st.info(f"🔄 **بديلك الذكي لـ ({craving}):** {plan['smart_swap_advice']}")

    st.markdown("### 📊 ملخص القيم الغذائية اليومية (يتحدث تلقائياً)")
    metrics_placeholder = st.empty()

    st.progress(1.0)
    st.markdown(f"**💡 خطة الترطيب:** افطر على كاستين مي، ووزع **{water_cups - 4} كاسات** بين الفطور والسحور، وكاستين عالسحور.")

    total_calories = 0
    total_protein = 0
    total_carbs = 0

    st.markdown("### 🍽️ تفاصيل الوجبات الأردنية المخصصة لك (عدّل الجرامات براحتك)")

    # --- السحور ---
    with st.expander("🌙 وجبة السحور", expanded=True):
        st.subheader(plan['suhoor']['meal_name'])
        suhoor_weight = 0
        
        for i, item in enumerate(plan['suhoor']['ingredients']):
            col1, col2 = st.columns([3, 1])
            with col1:
                new_w = st.number_input(item['name'], min_value=0, value=int(item['default_weight_g']), step=10, key=f"s_{i}")
            
            ratio = new_w / item['default_weight_g'] if item['default_weight_g'] > 0 else 0
            new_cal = item['calories'] * ratio
            new_prot = item['protein'] * ratio
            new_carbs = item['carbs'] * ratio
            
            with col2:
                st.markdown(f"<div style='margin-top: 32px;'>🔥 {int(new_cal)} kcal | 🥩 {int(new_prot)}g</div>", unsafe_allow_html=True)
            
            total_calories += new_cal
            total_protein += new_prot
            total_carbs += new_carbs
            suhoor_weight += new_w
            
        st.markdown("---")
        st.markdown(f"⚖️ **وزن الوجبة الكلي:** {suhoor_weight} غرام")
        st.caption(f"ليش اخترناها؟ {plan['suhoor']['reason']}")

    # --- الإفطار ---
    with st.expander("🍲 وجبة الإفطار", expanded=True):
        st.subheader(plan['iftar']['meal_name'])
        iftar_weight = 0
        
        for i, item in enumerate(plan['iftar']['ingredients']):
            col1, col2 = st.columns([3, 1])
            with col1:
                new_w = st.number_input(item['name'], min_value=0, value=int(item['default_weight_g']), step=10, key=f"i_{i}")
            
            ratio = new_w / item['default_weight_g'] if item['default_weight_g'] > 0 else 0
            new_cal = item['calories'] * ratio
            new_prot = item['protein'] * ratio
            new_carbs = item['carbs'] * ratio
            
            with col2:
                st.markdown(f"<div style='margin-top: 32px;'>🔥 {int(new_cal)} kcal | 🥩 {int(new_prot)}g</div>", unsafe_allow_html=True)
            
            total_calories += new_cal
            total_protein += new_prot
            total_carbs += new_carbs
            iftar_weight += new_w
            
        st.markdown("---")
        st.markdown(f"⚖️ **وزن الوجبة الكلي:** {iftar_weight} غرام")
        st.caption(f"ليش اخترناها؟ {plan['iftar']['reason']}")

    # تحديث العدادات العلوية
    with metrics_placeholder.container():
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🔥 السعرات الكلية", f"{int(total_calories)} kcal")
        c2.metric("🥩 البروتين الكلي", f"{int(total_protein)} g")
        c3.metric("🍞 الكارب الكلي", f"{int(total_carbs)} g")
        c4.metric("💧 الماء", f"{round(water_base, 1)} لتر")

    # --- ورقة المقاضي ---
    st.markdown("### 🛒 ورقة المقاضي (Grocery List)")
    grocery_text = "قائمة مشتريات رمضان:\n\n"
    for item in plan['grocery_list']:
        st.write(f"✅ {item}")
        grocery_text += f"- {item}\n"
        
    st.download_button(label="📥 تحميل ورقة المقاضي", data=grocery_text, file_name="ramadan_grocery_list.txt", mime="text/plain")


# ==========================================
# 7. الشات بوت التغذوي
# ==========================================
st.markdown("---")
st.markdown("### 🤖 اسأل مساعدك التغذوي")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# عرض المحادثة السابقة
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# مربع الإدخال
if user_input := st.chat_input("اسألني عن وجبتك، بدائل، أو نصايح رمضانية..."):
    # أضف رسالة المستخدم
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # بناء السياق
    plan_context = ""
    if st.session_state.plan:
        plan_context = f"""
الخطة الغذائية الحالية للمستخدم:
- السحور: {st.session_state.plan['suhoor']['meal_name']} - {st.session_state.plan['suhoor']['reason']}
- الإفطار: {st.session_state.plan['iftar']['meal_name']} - {st.session_state.plan['iftar']['reason']}
- قائمة المشتريات: {', '.join(st.session_state.plan['grocery_list'])}
"""
    else:
        plan_context = "المستخدم لم يولّد خطة بعد."

    system_context = f"""أنت مساعد تغذية رمضاني أردني ودّي وخبير.
بيانات المستخدم:
- الوزن: {weight} كغ | العمر: {age} | الطول: {height} سم
- الهدف: {goal} | النشاط: {activity_level}
- الحالة الصحية: {health_condition}
{plan_context}
أجب بشكل مختصر وودّي باللهجة الأردنية أو العربية الفصحى حسب سؤاله.
راعِ دايماً حالته الصحية في كل نصيحة."""

    # بناء تاريخ المحادثة لـ Gemini
    gemini_history = []
    for msg in st.session_state.chat_history[:-1]:  # كل شيء ما عدا الرسالة الأخيرة
        gemini_history.append({
            "role": "user" if msg["role"] == "user" else "model",
            "parts": [msg["content"]]
        })

    with st.chat_message("assistant"):
        with st.spinner("يفكر..."):
            try:
                chat_model = genai.GenerativeModel(
                    'gemini-2.5-flash',
                    system_instruction=system_context
                )
                chat = chat_model.start_chat(history=gemini_history)
                response = chat.send_message(user_input)
                reply = response.text
            except Exception as e:
                reply = f"صارت مشكلة: {e}"

        st.markdown(reply)

    st.session_state.chat_history.append({"role": "assistant", "content": reply})

# زر مسح المحادثة
if st.session_state.chat_history:
    if st.button("🗑️ مسح المحادثة"):
        st.session_state.chat_history = []
        st.rerun()