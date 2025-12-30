import streamlit as st
import random
import re
import numpy as np

# --- 1. DATA SETUP ---
# Pre-define all data structures so we don't recreate them on every run

# Case 2/3
L_FRAC_RARAS = ['1/6', '5/6', '1/8', '3/8', '5/8', '7/8']
# Case 4/5
LT_FRAC_TODAS = [f'{x}/{y}' for y in range(2,10) for x in range(1,y) if y!= 7]

# Case 6
L22_SQUARES = {x: x**2 for x in range(2, 101)} 
BASES_SQUARES = list(L22_SQUARES.keys())

# Case 7
L3_CUBES = {x: x**3 for x in range(2, 101)} 
BASES_CUBES = list(L3_CUBES.keys())

# Case 8/9
L2_POWERS = {x: 2**x for x in range(2, 21)}
EXPONENTS_L2 = list(L2_POWERS.keys())

# Case 10/11
L3_POWERS = {x: 3**x for x in range(2, 16)}
EXPONENTS_L3 = list(L3_POWERS.keys())

# Case 12
PRIMES_LIST = [
    [2, 3, 5, 7], [11, 13, 17, 19], [23, 29], [31, 37],
    [41, 43, 47], [53, 59], [61, 67], [71, 73, 79],
    [83, 89], [97]
]
TUTORIAL_PRIME_QUESTION = "Primes in the 0s: ?"
TUTORIAL_PRIME_ANSWER = set([2, 3, 5, 7])

# Case 13
PRIMES_SET = set([2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97])
ODD_NUMS = set([num for num in range(1, 101, 2)])
IS_PRIME_NUMS = list(ODD_NUMS.union(PRIMES_SET))

# Merged sections from user request
ALL_SECTION_NAMES = {
    0: 'Home', # --- NEW: Added Home section ---
    1: 'Multiplication',
    2: 'Fractions to Decimal', # Merged (Old 2 & 4)
    3: 'Decimal to Fractions', # Merged (Old 3 & 5)
    6: 'Squares', # Renamed
    7: 'Cubes', # Renamed
    8: 'Powers of 2', # Merged (Old 8 & 9)
    10: 'Powers of 3', # Merged (Old 10 & 11)
    12: 'Prime Numbers', # Merged (Old 12 & 13)
    14: 'Combined Practice',
    15: 'Combined Practice (Shortcut)'
}

# --- Definitive list of all practice modes for Combined Practice ---
PRACTICE_MODES = {
    # key: "Label for checkbox"
    "mult": "Multiplication",
    "frac_dec_u": "Fractions to Decimal (Uncommon)",
    "frac_dec_a": "Fractions to Decimal (All)",
    "dec_frac_u": "Decimal to Fractions (Uncommon)",
    "dec_frac_a": "Decimal to Fractions (All)",
    "squares": "Squares",
    "cubes": "Cubes",
    "pow2_p": "Powers of 2 (Give Power)",
    "pow2_a": "Powers of 2 (Give Answer)",
    "pow3_p": "Powers of 3 (Give Power)",
    "pow3_a": "Powers of 3 (Give Answer)",
    "prime_i": "Prime Numbers (Is This Prime?)",
    "prime_s": "Prime Numbers (Sectioned Primes)",
}
# --- Lookups for Combined Practice ---
PRACTICE_MODE_KEYS = list(PRACTICE_MODES.keys())
PRACTICE_MODE_LABELS = list(PRACTICE_MODES.values())
PRACTICE_LABEL_TO_KEY = {v: k for k, v in PRACTICE_MODES.items()}


# --- 2. SESSION STATE INITIALIZATION ---
if 'question' not in st.session_state:
    st.session_state.question = None
if 'answer' not in st.session_state:
    st.session_state.answer = None
if 'current_section' not in st.session_state:
    st.session_state.current_section = 0 # --- MODIFIED: Default to Home ---
if 'combined_sections' not in st.session_state:
    st.session_state.combined_sections = [] 
if 'practice_started' not in st.session_state:
    st.session_state.practice_started = False
if 'section_type' not in st.session_state:
    st.session_state.section_type = 0 # --- MODIFIED: Default to Home ---
if 'user_answer_input' not in st.session_state:
    st.session_state.user_answer_input = ""

# Multiplication options
if 'mult_min' not in st.session_state:
    st.session_state.mult_min = 2
if 'mult_max' not in st.session_state:
    st.session_state.mult_max = 15
if 'mult_exclude_squares' not in st.session_state:
    st.session_state.mult_exclude_squares = False

# Merged section modes
if 'frac_to_dec_mode' not in st.session_state:
    st.session_state.frac_to_dec_mode = "Uncommon"
if 'dec_to_frac_mode' not in st.session_state:
    st.session_state.dec_to_frac_mode = "Uncommon"
if 'pow2_mode' not in st.session_state:
    st.session_state.pow2_mode = "Give Power"
if 'pow3_mode' not in st.session_state:
    st.session_state.pow3_mode = "Give Power"

# Squares options
if 'squares_min' not in st.session_state:
    st.session_state.squares_min = 2
if 'squares_max' not in st.session_state:
    st.session_state.squares_max = 20

# Cubes options
if 'cubes_min' not in st.session_state:
    st.session_state.cubes_min = 2
if 'cubes_max' not in st.session_state:
    st.session_state.cubes_max = 12

# Powers of 2 Options
if 'pow2_min' not in st.session_state:
    st.session_state.pow2_min = 2
if 'pow2_max' not in st.session_state:
    st.session_state.pow2_max = 12

# Powers of 3 Options
if 'pow3_min' not in st.session_state:
    st.session_state.pow3_min = 2
if 'pow3_max' not in st.session_state:
    st.session_state.pow3_max = 6

# Primes options
if 'prime_mode' not in st.session_state:
    st.session_state.prime_mode = "Is This Prime?"
if 'sectioned_primes_tutorial_done' not in st.session_state:
    st.session_state.sectioned_primes_tutorial_done = False


# --- 3. QUESTION GENERATOR FUNCTIONS ---

def generate_combined_question(mode_key):
    """
    Generates a single question for combined practice based on the mode_key.
    Crucially, it sets st.session_state.section_type so the answer
    checker (handle_submission) knows how to validate the answer.
    """
    st.session_state.question = None
    st.session_state.answer = None

    match mode_key:
        case "mult":
            st.session_state.section_type = 1
            min_val = st.session_state.mult_min
            max_val = st.session_state.mult_max
            exclude_squares = st.session_state.mult_exclude_squares
            if min_val > max_val: min_val = max_val
            a = random.randint(min_val, max_val)
            b = random.randint(min_val, max_val)
            if exclude_squares and min_val != max_val:
                while a == b:
                    b = random.randint(min_val, max_val)
            st.session_state.question = f'{a} x {b} = ?'
            st.session_state.answer = str(a * b)
        
        case "frac_dec_u":
            st.session_state.section_type = 2
            frac = random.choice(L_FRAC_RARAS)
            st.session_state.question = f'{frac} = ?'
            st.session_state.answer = round(float(eval(frac)), 5)
        
        case "frac_dec_a":
            st.session_state.section_type = 2
            frac = random.choice(LT_FRAC_TODAS)
            st.session_state.question = f'{frac} = ?'
            st.session_state.answer = round(float(eval(frac)), 5)
        
        case "dec_frac_u":
            st.session_state.section_type = 3
            frac = random.choice(L_FRAC_RARAS)
            val = round(float(eval(frac)), 5)
            st.session_state.question = f'{val} = ?'
            st.session_state.answer = frac
        
        case "dec_frac_a":
            st.session_state.section_type = 3
            frac = random.choice(LT_FRAC_TODAS)
            val = round(float(eval(frac)), 5)
            st.session_state.question = f'{val} = ?'
            st.session_state.answer = frac

        case "squares":
            st.session_state.section_type = 6
            min_val = st.session_state.squares_min
            max_val = st.session_state.squares_max
            if min_val > max_val: min_val = max_val
            valid_bases = [b for b in BASES_SQUARES if min_val <= b <= max_val]
            if not valid_bases: valid_bases = BASES_SQUARES # Failsafe
            base = random.choice(valid_bases)
            st.session_state.question = f'{base}^2 = ?'
            st.session_state.answer = str(L22_SQUARES[base])

        case "cubes":
            st.session_state.section_type = 7
            min_val = st.session_state.cubes_min
            max_val = st.session_state.cubes_max
            if min_val > max_val: min_val = max_val
            valid_bases = [b for b in BASES_CUBES if min_val <= b <= max_val]
            if not valid_bases: valid_bases = BASES_CUBES # Failsafe
            base = random.choice(valid_bases)
            st.session_state.question = f'{base}^3 = ?'
            st.session_state.answer = str(L3_CUBES[base])
        
        case "pow2_p":
            st.session_state.section_type = 8
            min_val = st.session_state.pow2_min
            max_val = st.session_state.pow2_max
            if min_val > max_val: min_val = max_val
            valid_exponents = [e for e in EXPONENTS_L2 if min_val <= e <= max_val]
            if not valid_exponents: valid_exponents = EXPONENTS_L2 # Failsafe
            exp = random.choice(valid_exponents)
            val = L2_POWERS[exp]
            st.session_state.question = f'{val} = 2^?'
            st.session_state.answer = str(exp)
        
        case "pow2_a":
            st.session_state.section_type = 8
            min_val = st.session_state.pow2_min
            max_val = st.session_state.pow2_max
            if min_val > max_val: min_val = max_val
            valid_exponents = [e for e in EXPONENTS_L2 if min_val <= e <= max_val]
            if not valid_exponents: valid_exponents = EXPONENTS_L2 # Failsafe
            exp = random.choice(valid_exponents)
            st.session_state.question = f'2^{exp} = ?'
            st.session_state.answer = str(L2_POWERS[exp])

        case "pow3_p":
            st.session_state.section_type = 10
            min_val = st.session_state.pow3_min
            max_val = st.session_state.pow3_max
            if min_val > max_val: min_val = max_val
            valid_exponents = [e for e in EXPONENTS_L3 if min_val <= e <= max_val]
            if not valid_exponents: valid_exponents = EXPONENTS_L3 # Failsafe
            exp = random.choice(valid_exponents)
            val = L3_POWERS[exp]
            st.session_state.question = f'{val} = 3^?'
            st.session_state.answer = str(exp)
        
        case "pow3_a":
            st.session_state.section_type = 10
            min_val = st.session_state.pow3_min
            max_val = st.session_state.pow3_max
            if min_val > max_val: min_val = max_val
            valid_exponents = [e for e in EXPONENTS_L3 if min_val <= e <= max_val]
            if not valid_exponents: valid_exponents = EXPONENTS_L3 # Failsafe
            exp = random.choice(valid_exponents)
            st.session_state.question = f'3^{exp} = ?'
            st.session_state.answer = str(L3_POWERS[exp])

        case "prime_i":
            st.session_state.section_type = 12
            num = random.choice(IS_PRIME_NUMS)
            st.session_state.question = f'Is {num} prime? (1=Y, 0=N)'
            st.session_state.answer = "1" if num in PRIMES_SET else "0"
        
        case "prime_s":
            st.session_state.section_type = 12
            p = random.randint(0,9)
            st.session_state.question = f'Primes in the {p*10}s: ?'
            st.session_state.answer = set(PRIMES_LIST[p])


def new_question(section_id):
    """
    Generates a question for a normal section (1, 2, 3, 6, 7, 8, 10, 12)
    or handles the setup for combined practice (14, 15).
    """
    st.session_state.question = None
    st.session_state.answer = None
    st.session_state.section_type = section_id

    match section_id:
        case 0:
            pass # Home screen, no question to generate
        case 1:
            min_val = st.session_state.mult_min
            max_val = st.session_state.mult_max
            exclude_squares = st.session_state.mult_exclude_squares
            if min_val > max_val:
                st.error("Min number cannot be greater than max number. Fix in sidebar.")
                st.session_state.question = "Error: Fix options in sidebar"
                st.session_state.answer = ""
                return
            a = random.randint(min_val, max_val)
            b = random.randint(min_val, max_val)
            if exclude_squares and min_val != max_val:
                while a == b:
                    b = random.randint(min_val, max_val)
            st.session_state.question = f'{a} x {b} = ?'
            st.session_state.answer = str(a * b)
        
        case 2:
            mode = st.session_state.frac_to_dec_mode
            frac = random.choice(L_FRAC_RARAS if mode == "Uncommon" else LT_FRAC_TODAS)
            st.session_state.question = f'{frac} = ?'
            st.session_state.answer = round(float(eval(frac)), 5)
        
        case 3:
            mode = st.session_state.dec_to_frac_mode
            frac = random.choice(L_FRAC_RARAS if mode == "Uncommon" else LT_FRAC_TODAS)
            val = round(float(eval(frac)), 5)
            st.session_state.question = f'{val} = ?'
            st.session_state.answer = frac
        
        case 6:
            min_val = st.session_state.squares_min
            max_val = st.session_state.squares_max
            if min_val > max_val:
                st.error("Min number cannot be greater than max number. Fix in sidebar.")
                st.session_state.question = "Error: Fix options in sidebar"
                st.session_state.answer = ""
                return
            valid_bases = [b for b in BASES_SQUARES if min_val <= b <= max_val]
            if not valid_bases:
                st.error("No valid bases in the selected range. Fix in sidebar.")
                st.session_state.question = "Error: Fix options in sidebar"
                st.session_state.answer = ""
                return
            base = random.choice(valid_bases)
            st.session_state.question = f'{base}^2 = ?'
            st.session_state.answer = str(L22_SQUARES[base])
        
        case 7:
            min_val = st.session_state.cubes_min
            max_val = st.session_state.cubes_max
            if min_val > max_val:
                st.error("Min number cannot be greater than max number. Fix in sidebar.")
                st.session_state.question = "Error: Fix options in sidebar"
                st.session_state.answer = ""
                return
            valid_bases = [b for b in BASES_CUBES if min_val <= b <= max_val]
            if not valid_bases:
                st.error("No valid bases in the selected range. Fix in sidebar.")
                st.session_state.question = "Error: Fix options in sidebar"
                st.session_state.answer = ""
                return
            base = random.choice(valid_bases)
            st.session_state.question = f'{base}^3 = ?'
            st.session_state.answer = str(L3_CUBES[base])
        
        case 8:
            mode = st.session_state.pow2_mode
            min_val = st.session_state.pow2_min
            max_val = st.session_state.pow2_max
            if min_val > max_val:
                st.error("Min exponent cannot be greater than max. Fix in sidebar.")
                st.session_state.question = "Error: Fix options in sidebar"
                st.session_state.answer = ""
                return
            valid_exponents = [e for e in EXPONENTS_L2 if min_val <= e <= max_val]
            if not valid_exponents:
                st.error("No valid exponents in the selected range. Fix in sidebar.")
                st.session_state.question = "Error: Fix options in sidebar"
                st.session_state.answer = ""
                return
            exp = random.choice(valid_exponents)
            
            if mode == "Give Power":
                val = L2_POWERS[exp]
                st.session_state.question = f'{val} = 2^?'
                st.session_state.answer = str(exp)
            elif mode == "Give Answer":
                st.session_state.question = f'2^{exp} = ?'
                st.session_state.answer = str(L2_POWERS[exp])
        
        case 10:
            mode = st.session_state.pow3_mode
            min_val = st.session_state.pow3_min
            max_val = st.session_state.pow3_max
            if min_val > max_val:
                st.error("Min exponent cannot be greater than max. Fix in sidebar.")
                st.session_state.question = "Error: Fix options in sidebar"
                st.session_state.answer = ""
                return
            valid_exponents = [e for e in EXPONENTS_L3 if min_val <= e <= max_val]
            if not valid_exponents:
                st.error("No valid exponents in the selected range. Fix in sidebar.")
                st.session_state.question = "Error: Fix options in sidebar"
                st.session_state.answer = ""
                return
            exp = random.choice(valid_exponents)

            if mode == "Give Power":
                val = L3_POWERS[exp]
                st.session_state.question = f'{val} = 3^?'
                st.session_state.answer = str(exp)
            elif mode == "Give Answer":
                st.session_state.question = f'3^{exp} = ?'
                st.session_state.answer = str(L3_POWERS[exp])
        
        case 12:
            mode = st.session_state.prime_mode
            if mode == "Is This Prime?":
                num = random.choice(IS_PRIME_NUMS)
                st.session_state.question = f'Is {num} prime? (1=Y, 0=N)'
                st.session_state.answer = "1" if num in PRIMES_SET else "0"
            elif mode == "Sectioned Primes":
                p = random.randint(0,9)
                st.session_state.question = f'Primes in the {p*10}s: ?'
                st.session_state.answer = set(PRIMES_LIST[p])
        
        case 14 | 15: 
            if not st.session_state.combined_sections:
                st.error("No sections selected for combined practice!")
                st.session_state.practice_started = False
                return
            
            chosen_mode_key = random.choice(st.session_state.combined_sections)
            generate_combined_question(chosen_mode_key)


# --- 4. SPEED-RUN SUBMISSION HANDLER ---
def handle_submission():
    """Handles the answer submission and state logic."""
    user_input = st.session_state.user_answer_input
    section = st.session_state.section_type
    
    if not user_input and section != 12: 
        st.warning("Please enter an answer.")
        return

    correct = False
    correct_answer_str = str(st.session_state.answer)

    try:
        if section in [1, 6, 7, 8, 10]:
            correct = (user_input.strip() == correct_answer_str)
        
        elif section == 2: 
            val = st.session_state.answer
            correct = (abs(float(user_input) - val) < 0.001)
        
        elif section == 3: 
            correct = (abs(eval(user_input) - eval(correct_answer_str)) < 0.001)

        elif section == 12:
            if st.session_state.question.startswith("Is"):
                correct = (user_input.strip()[-1] == correct_answer_str)
                correct_answer_str = "Yes, Prime" if correct_answer_str == "1" else "No"
            else: 
                ans_nums = re.findall(r'\d+', user_input)
                ans_set = set(int(num) for num in ans_nums)
                correct = (ans_set == st.session_state.answer)
                correct_answer_str = ", ".join(map(str, sorted(list(st.session_state.answer))))
            
    except Exception as e:
        st.error(f"Invalid input format. Error: {e}")
        return

    if correct:
        st.toast("CORRECT! 🎉", icon="✅")
        new_question(st.session_state.current_section)
        st.session_state.user_answer_input = "" 
    else:
        st.toast(f"WRONG... {correct_answer_str}", icon="❌")
        st.session_state.user_answer_input = ""


# --- Tutorial Submission Handler ---
def handle_tutorial_submission():
    """Handles the submission for the Sectioned Primes tutorial."""
    user_input = st.session_state.user_answer_input
    ans_nums = re.findall(r'\d+', user_input)
    ans_set = set(int(num) for num in ans_nums)
    
    if ans_set == TUTORIAL_PRIME_ANSWER:
        st.toast("Correct! Starting practice.", icon="✅")
        st.session_state.sectioned_primes_tutorial_done = True
        st.session_state.user_answer_input = ""
        new_question(12) 
    else:
        st.toast("Try again! e.g., '2 3 5 7'", icon="❌")
        st.session_state.user_answer_input = ""


# --- 5. UI LAYOUT ---

# --- Callbacks for option changes ---
def on_mult_option_change():
    if st.session_state.current_section == 1: new_question(1)
def on_frac_to_dec_mode_change():
    if st.session_state.current_section == 2: new_question(2)
def on_dec_to_frac_mode_change():
    if st.session_state.current_section == 3: new_question(3)
def on_squares_option_change():
    if st.session_state.current_section == 6: new_question(6)
def on_cubes_option_change():
    if st.session_state.current_section == 7: new_question(7)
def on_pow2_option_change():
    if st.session_state.current_section == 8: new_question(8)
def on_pow3_option_change():
    if st.session_state.current_section == 10: new_question(10)
def on_prime_mode_change():
    if st.session_state.current_section == 12: new_question(12)


st.set_page_config(layout="wide")
st.title("🧠 GMATttt Mental Math Practice")

# --- Sidebar for Navigation ---
st.sidebar.title("Menu")
section_name = st.sidebar.radio(
    "Select a section:",
    options=ALL_SECTION_NAMES.values(),
    key="menu_selection",
    index=list(ALL_SECTION_NAMES.keys()).index(st.session_state.current_section) 
)
section_id = [k for k, v in ALL_SECTION_NAMES.items() if v == section_name][0]

# --- Main Page Logic (Handles section switching) ---
if st.session_state.current_section != section_id:
    st.session_state.current_section = section_id
    st.session_state.practice_started = False
    st.session_state.combined_sections = []
    
    if section_id == 1:
        st.session_state.mult_min = 2
        st.session_state.mult_max = 15
        st.session_state.mult_exclude_squares = False
    if section_id == 6:
        st.session_state.squares_min = 2
        st.session_state.squares_max = 20
    if section_id == 7:
        st.session_state.cubes_min = 2
        st.session_state.cubes_max = 12
    if section_id == 8:
        st.session_state.pow2_min = 2
        st.session_state.pow2_max = 12
    if section_id == 10:
        st.session_state.pow3_min = 2
        st.session_state.pow3_max = 6
    if section_id == 12:
        st.session_state.sectioned_primes_tutorial_done = False
    
    if section_id == 15: 
        all_modes = set(PRACTICE_MODES.keys())
        # --- MODIFIED: New Shortcut Logic ---
        exclude_modes = {"frac_dec_u", "dec_frac_u", "prime_s"}
        st.session_state.combined_sections = sorted(list(all_modes - exclude_modes))
        st.session_state.practice_started = True
    
    if section_id not in [0, 14]: # Generate first question unless it's Home or Combined
        new_question(section_id)
    
    st.rerun() 


# --- Sidebar Widgets (Conditional) ---
if section_id == 1:
    st.sidebar.markdown("---")
    st.sidebar.subheader("Multiplication Options")
    st.sidebar.number_input("Min Number", min_value=2, max_value=1000, key="mult_min", on_change=on_mult_option_change)
    st.sidebar.number_input("Max Number", min_value=2, max_value=1000, key="mult_max", on_change=on_mult_option_change)
    st.sidebar.checkbox("Exclude Squares?", key="mult_exclude_squares", on_change=on_mult_option_change)
if section_id == 2:
    st.sidebar.markdown("---")
    st.sidebar.radio("Mode:", ("Uncommon", "All"), key="frac_to_dec_mode", on_change=on_frac_to_dec_mode_change)
if section_id == 3:
    st.sidebar.markdown("---")
    st.sidebar.radio("Mode:", ("Uncommon", "All"), key="dec_to_frac_mode", on_change=on_dec_to_frac_mode_change)
if section_id == 6:
    st.sidebar.markdown("---")
    st.sidebar.subheader("Squares Options")
    st.sidebar.number_input("Min Base", min_value=2, max_value=100, key="squares_min", on_change=on_squares_option_change)
    st.sidebar.number_input("Max Base", min_value=2, max_value=100, key="squares_max", on_change=on_squares_option_change)
if section_id == 7:
    st.sidebar.markdown("---")
    st.sidebar.subheader("Cubes Options")
    st.sidebar.number_input("Min Base", min_value=2, max_value=100, key="cubes_min", on_change=on_cubes_option_change)
    st.sidebar.number_input("Max Base", min_value=2, max_value=100, key="cubes_max", on_change=on_cubes_option_change)
if section_id == 8:
    st.sidebar.markdown("---")
    st.sidebar.subheader("Powers of 2 Options")
    st.sidebar.radio("Mode:", ("Give Power", "Give Answer"), key="pow2_mode", on_change=on_pow2_option_change)
    st.sidebar.number_input("Min Exponent", min_value=2, max_value=20, key="pow2_min", on_change=on_pow2_option_change)
    st.sidebar.number_input("Max Exponent", min_value=2, max_value=20, key="pow2_max", on_change=on_pow2_option_change)
if section_id == 10:
    st.sidebar.markdown("---")
    st.sidebar.subheader("Powers of 3 Options")
    st.sidebar.radio("Mode:", ("Give Power", "Give Answer"), key="pow3_mode", on_change=on_pow3_option_change)
    st.sidebar.number_input("Min Exponent", min_value=2, max_value=15, key="pow3_min", on_change=on_pow3_option_change)
    st.sidebar.number_input("Max Exponent", min_value=2, max_value=15, key="pow3_max", on_change=on_pow3_option_change)
if section_id == 12:
    st.sidebar.markdown("---")
    st.sidebar.radio("Mode:", ("Is This Prime?", "Sectioned Primes"), key="prime_mode", on_change=on_prime_mode_change)


# --- Section 14: Combined Practice Setup ---
if st.session_state.current_section == 14 and not st.session_state.practice_started:
    
    st.header("Combined Practice Setup")
    mode = st.radio("Mode:", ("Include", "Exclude"), horizontal=True, key="combined_mode")
    default_exclude_keys = {
        "frac_dec_u", "dec_frac_u", "prime_s"
    }
    
    st.markdown("---")
    cols = st.columns(3)
    selections = {}
    
    num_modes = len(PRACTICE_MODE_KEYS)
    items_per_col = (num_modes + 2) // 3 
    
    for i, key in enumerate(PRACTICE_MODE_KEYS):
        label = PRACTICE_MODE_LABELS[i]
        
        if mode == "Include":
            default_val = False
        else: 
            default_val = (key not in default_exclude_keys)
        
        col_index = i // items_per_col
        with cols[col_index]:
            selections[key] = st.checkbox(label, value=default_val, key=f"check_{key}")

    st.markdown("---")
    if st.button("Start Practice"):
        selected_keys = [key for key, selected in selections.items() if selected]
        
        if mode == "Include":
            st.session_state.combined_sections = sorted(list(selected_keys))
        else:
            all_keys_set = set(PRACTICE_MODES.keys())
            selected_keys_set = set(selected_keys)
            st.session_state.combined_sections = sorted(list(all_keys_set - selected_keys_set))
        
        if not st.session_state.combined_sections:
            st.error("No sections selected! Please select at least one.")
        else:
            st.session_state.practice_started = True
            new_question(14) 
            st.rerun()

# --- NEW: Home/Welcome Page Logic ---
elif st.session_state.current_section == 0:
    st.subheader("Welcome to GMAT Mental Math Practice!")
    st.markdown("""
    This guide is designed to help you practice mental math skills and memorization for the GMAT.
    
    - Use the **sidebar menu** on the left to select a practice section.
    - Many sections (like Multiplication or Squares) have **customizable parameters** (e.g., number ranges) that will appear in the sidebar.
    - Other sections (like Fractions or Primes) have **sub-sections** to choose from.
    - In Combined Practice you can practice multiple sections at once.
    
    All options are defaulted to the most common and useful ranges for GMAT prep.
    
    Select a section to begin!
    """)

# --- Tutorial Screen Logic ---
elif (st.session_state.current_section == 12 and 
      st.session_state.prime_mode == "Sectioned Primes" and 
      not st.session_state.sectioned_primes_tutorial_done):
    
    st.header("Sectioned Primes: Example")
    st.info("List the prime numbers in the tens asked.\n\ne.g., `2, 3, 5, 7` $\qquad$ or $\qquad$ `2 3 5 7`")
    st.subheader(TUTORIAL_PRIME_QUESTION)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.text_input("Your Answer:", label_visibility="collapsed", key="user_answer_input", on_change=handle_tutorial_submission)
    with col2:
        st.button("Check Answer", on_click=handle_tutorial_submission)

# --- Main Question & Answer Area (Regular Practice) ---
elif st.session_state.current_section not in [14, 0] or st.session_state.practice_started:

    # Safety check
    if not st.session_state.question:
        if st.session_state.current_section in [14, 15] and not st.session_state.combined_sections:
            st.warning("Please go back and configure your combined practice (Section 14).")
        else:
            if st.session_state.current_section:
                 new_question(st.session_state.current_section)
            else:
                 new_question(1) # Failsafe
            st.rerun()

    # Display the current question
    if st.session_state.question:
        st.header(st.session_state.question)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.text_input("Your Answer:", label_visibility="collapsed", key="user_answer_input", on_change=handle_submission)
    with col2:
        st.button("Check Answer", on_click=handle_submission)