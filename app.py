import os
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(
    page_title="HairCare Assistant",
    page_icon="💇",
    layout="wide",
)

# -------------------- KNOWLEDGE BASE --------------------
HAIRCARE_MANUAL = """
You are HairCare Assistant, a friendly, professional virtual haircare advisor.
Use simple English. Give practical, cautious, personalized general haircare guidance.
Do not diagnose medical conditions, prescribe medication, or guarantee hair growth
or prevention of hair loss. Consider allergies and sensitivities. Ask the user to
patch-test new products and follow product labels.

HAIR TYPES
- Straight: often benefits from lightweight products; apply conditioner mainly to lengths.
- Wavy: use lightweight moisture and avoid heavy products that flatten waves.
- Curly: use moisturizing shampoo/conditioner, detangle gently while conditioned,
  and consider leave-in conditioner or curl cream.
- Coily: prioritize gentle cleansing, regular conditioning, careful detangling,
  and protective styles that are not tight.

SCALP TYPES
- Oily: wash as often as needed for comfort; use lightweight products and keep
  heavy oils away from the scalp if they worsen buildup.
- Dry: use a gentle shampoo and avoid very hot water; persistent flaking or itching
  should be assessed professionally.
- Normal: use a gentle routine suited to activity and styling habits.
- Combination: treat the scalp and hair lengths differently; cleanse the scalp
  and condition the lengths.

COMMON CONCERNS
Hair fall:
Possible contributors include genetics, stress, illness, nutritional deficiencies,
hormonal changes, medications, and tight hairstyles. Use gentle handling and avoid
traction. Sudden, patchy, severe, or persistent shedding needs medical assessment.
Do not promise regrowth.

Dandruff:
May be associated with scalp conditions such as seborrheic dermatitis. An
anti-dandruff shampoo with an ingredient such as ketoconazole, selenium sulfide,
or zinc pyrithione (where available and permitted) may help. Follow label directions.
Seek professional advice if severe, painful, inflamed, or persistent.

Dry hair:
Try a gentle shampoo, conditioner after washing, and a moisturizing mask when
needed. Reduce heat and chemical processing. Ingredients such as glycerin,
dimethicone, and conditioning agents may help hair feel smoother.

Frizzy hair:
Condition regularly, use a leave-in conditioner or serum if suitable, dry gently,
and limit high heat. Humidity and hair damage can contribute.

Oily scalp:
Cleanse according to oiliness and activity. Avoid applying heavy oils to the scalp
if they increase greasiness or irritation. Conditioner can be focused on lengths.

Split ends:
Split ends cannot be permanently repaired by products; trimming removes them.
Conditioning products can temporarily improve feel and reduce friction. Limit heat
and rough brushing.

Damaged hair:
Reduce bleaching, chemical treatments, and high-heat styling. Use conditioner,
leave-in products, and gentle detangling. Breakage that is extensive or unexplained
may need professional assessment.

Slow hair growth:
Hair growth rate is influenced by genetics and health. Adequate nutrition and
addressing underlying health issues matter more than miracle products. Recommend
medical advice for noticeable changes, thinning, or persistent concerns.

Itchy scalp:
Possible triggers include irritation, dryness, dandruff, allergy, or skin conditions.
Stop a recently introduced product if irritation follows its use. Severe itching,
sores, swelling, pain, or persistent symptoms require professional advice.

PRODUCT CATEGORIES
- Shampoo: choose according to scalp needs; gentle formulas for frequent washing.
- Conditioner: apply mainly to mid-lengths and ends unless product directions differ.
- Hair oil: optional for lengths/ends; avoid if it irritates or worsens scalp buildup.
- Serum: may reduce friction/frizz; use a small amount on lengths.
- Hair mask: occasional conditioning step for dry or damaged lengths.
- Anti-dandruff shampoo: select an appropriate active ingredient and follow its label.
- Leave-in conditioner: useful for dry, curly, coily, or easily tangled hair.

ROUTINE GUIDANCE
Daily: detangle gently as appropriate, protect hair from excessive heat, and avoid
tight hairstyles that pull on the roots.
Wash days: cleanse the scalp, rinse thoroughly, condition the lengths, and detangle
gently. Washing frequency depends on scalp oiliness, activity, and preference.
Weekly: use a conditioning mask if hair is dry or damaged; clean brushes and combs.
Monthly: review whether products are causing buildup or irritation; trim split ends
as desired (frequency depends on hair and styling needs).

SAFETY
Do not diagnose. Do not recommend supplements or medication as a treatment.
Do not suggest harsh DIY remedies such as undiluted essential oils, lemon juice,
baking soda, or irritating scalp mixtures. Ask about allergies before suggesting
ingredients. Seek urgent medical care for severe allergic reaction or facial/throat
swelling. Refer severe, sudden, patchy, painful, inflamed, or persistent symptoms
to a dermatologist or qualified clinician.
"""

SYSTEM_INSTRUCTION = """
You are HairCare Assistant, a personal haircare advisor for teenagers, college
students, and adults. Be warm, supportive, clear, and concise. Use the supplied
haircare knowledge base as your primary reference. Personalize advice using the
user profile when relevant. If important information is missing, ask one focused
follow-up question. Explain uncertainty and avoid making unsupported claims.
Never diagnose, prescribe, promise results, or replace professional medical advice.
For red flags or persistent symptoms, recommend a dermatologist.
"""

FAQS = [
    ("How often should I wash my hair?", "Wash according to your scalp's oiliness, activity, and comfort. Oily scalps may need more frequent washing; dry or textured hair may need less frequent washing. There is no single schedule for everyone."),
    ("Should I oil my hair before shampooing?", "Pre-wash oil on the lengths may help some people reduce dryness or friction. Avoid it if it irritates your scalp or worsens buildup."),
    ("Does shampoo cause hair fall?", "Normal washing can release hairs that were already shedding. Harsh handling or an irritating product may contribute to breakage or irritation. Sudden or persistent hair loss should be assessed."),
    ("How can I choose a shampoo?", "Choose based mainly on scalp needs. Consider a gentle shampoo for routine cleansing and a suitable anti-dandruff shampoo if dandruff is a concern."),
    ("Should I condition my hair every time I shampoo?", "Conditioner after shampooing is useful for most hair types. Apply mainly to the mid-lengths and ends, adjusting the amount to your hair."),
    ("Can split ends be repaired?", "Products can temporarily smooth split ends, but trimming is the only way to remove them."),
    ("How can I reduce frizz?", "Condition regularly, use a leave-in product if suitable, dry gently, and reduce excessive heat styling."),
    ("Is dandruff caused by poor hygiene?", "Not necessarily. Dandruff can be linked to scalp conditions and individual sensitivity. Use an appropriate anti-dandruff product according to its label."),
    ("Does trimming make hair grow faster?", "No. Trimming removes damaged ends but does not change the rate of growth from the scalp."),
    ("Can I use hair oil on an oily scalp?", "You can choose to use a small amount on hair lengths, but heavy scalp oiling may worsen greasiness or buildup for some people."),
    ("What helps dry hair?", "A gentle shampoo, regular conditioner, occasional hair mask, and reduced heat styling can improve how dry hair feels."),
    ("Is heat styling damaging?", "Frequent high heat can contribute to dryness and breakage. Use lower temperatures, limit frequency, and use a heat protectant."),
    ("How do I detangle curly hair?", "Detangle gently, often when damp and coated with conditioner, using fingers or a wide-tooth comb. Work from ends upward."),
    ("What should I do about an itchy scalp?", "Consider whether a new product is irritating your scalp and stop it if symptoms began after use. Persistent, severe, painful, or inflamed itching needs professional advice."),
    ("Do hair growth oils guarantee growth?", "No product can guarantee hair growth. Persistent thinning or unusual shedding should be discussed with a dermatologist."),
]

# -------------------- SIDEBAR PROFILE --------------------
st.title("💇 HairCare Assistant")
st.caption("Your personal haircare companion — practical guidance for healthier hair habits.")

with st.sidebar:
    st.header("Your hair profile")
    name = st.text_input("Your name", placeholder="Enter your name")
    age_group = st.selectbox("Age group", ["Prefer not to say", "Under 18", "18–24", "25–34", "35–44", "45+"])
    hair_type = st.selectbox("Hair type", ["Not sure", "Straight", "Wavy", "Curly", "Coily"])
    scalp_type = st.selectbox("Scalp type", ["Not sure", "Oily", "Dry", "Normal", "Combination"])
    concern = st.selectbox(
        "Main hair concern",
        ["Not selected", "Hair fall", "Dandruff", "Dry hair", "Frizzy hair",
         "Oily scalp", "Split ends", "Damaged hair", "Slow hair growth", "Itchy scalp"]
    )
    goals = st.text_area("Haircare goals", placeholder="e.g. reduce frizz, build a simple routine")
    allergies = st.text_input("Known allergies or sensitivities (optional)")
    st.caption("Your profile is used to personalize answers during this session.")

profile = f"""
USER PROFILE
Name: {name or 'Not provided'}
Age group: {age_group}
Hair type: {hair_type}
Scalp type: {scalp_type}
Main concern: {concern}
Goals: {goals or 'Not provided'}
Known allergies/sensitivities: {allergies or 'Not provided'}
"""

# -------------------- GEMINI CLIENT --------------------
api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))

if not api_key:
    st.warning("Add your Gemini API key to continue. In Streamlit, use Settings → Secrets or set the GEMINI_API_KEY environment variable.")
    st.code('GEMINI_API_KEY = "your_api_key_here"', language="toml")
    st.stop()

try:
    client = genai.Client(api_key=api_key)
except Exception as exc:
    st.error(f"Could not initialize Gemini: {exc}")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                f"Hello {name}! " if name else "Hello! "
            ) + "I'm your HairCare Assistant. Tell me what you'd like help with — "
                "your hair routine, a concern, or choosing suitable product types."
        )
    ]

# If profile changes, the latest profile is used for new replies.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("✨ Create my haircare routine", use_container_width=True):
        st.session_state.pending_prompt = (
            "Create a practical daily, weekly, and monthly haircare routine for me "
            "using my profile. Keep it realistic and explain product categories."
        )
with col2:
    if st.button("🧴 Suggest product types", use_container_width=True):
        st.session_state.pending_prompt = (
            "Suggest suitable product categories and ingredients to look for based "
            "on my profile. Do not recommend specific brands."
        )

with st.expander("Frequently asked questions"):
    for question, answer in FAQS:
        st.markdown(f"**{question}**  \n{answer}")

prompt = st.chat_input("Ask a haircare question...")
if "pending_prompt" in st.session_state:
    prompt = st.session_state.pop("pending_prompt")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    conversation = []
    for item in st.session_state.messages[-12:]:
        conversation.append(f"{item['role'].upper()}: {item['content']}")

    full_prompt = f"""
HAIRCARE KNOWLEDGE BASE:
{HAIRCARE_MANUAL}

{profile}

CONVERSATION:
{chr(10).join(conversation)}

Respond to the latest user message. Keep the answer organized and practical.
"""
    with st.chat_message("assistant"):
        with st.spinner("Preparing your haircare advice..."):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.4,
                        max_output_tokens=900,
                    ),
                )
                answer = response.text or "I couldn't generate a response. Please try asking in a different way."
            except Exception as exc:
                answer = (
                    "I couldn't connect to Gemini right now. Please check your API key "
                    f"and internet connection, then try again. Details: {exc}"
                )
            st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})

st.divider()
st.caption("Disclaimer: This chatbot provides general haircare information only. It does not diagnose or treat medical conditions. Consult a dermatologist for severe, sudden, or persistent symptoms.")
