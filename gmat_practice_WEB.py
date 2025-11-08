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
L22_SQUARES = {x: x**2 for x in range(2, 21)}
L22_SQUARES[25] = 25*25
BASES_SQUARES = list(L22_SQUARES.keys())

# Case 7
L3_CUBES = {x: x**3 for x in range(2, 13)}
BASES_CUBES = list(L3_CUBES.keys())

# Case 8/9
L2_POWERS = {x: 2**x for x in range(2, 13)}
EXPONENTS_L2 = list(L2_POWERS.keys())

# Case 10/11
L3_POWERS = {x: 3**x for x in range(2, 7)}
EXPONENTS_L3 = list(L3_POWERS.keys())

# Case 12
PRIMES_LIST = [
    [2, 3, 5, 7], [11, 13, 17, 19], [23, 29], [31, 37],
    [41, 43, 47], [53, 59], [61, 67], [71, 73, 79],
    [83, 89], [97]
]

# Case 13
PRIMES_SET = set([2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97])
ODD_NUMS = set([num for num in range(1, 101, 2)])
IS_PRIME_NUMS = list(ODD_NUMS.union(PRIMES_SET))

ALL_SECTION_NAMES = {
    1: 'Multiplication',
    2: 'Uncommon- Fractions to Decimal',
    3: 'Uncommon- Decimal to Fraction',
    4: 'All- Fractions to Decimal',
    5: 'All- Decimal to Fractions',
    6: 'Squares {2-20} and {25}',
    7: 'Cubes {2-12}',
    8: 'Powers of 2 (give power)',
    9: 'Powers of 2 (give answer)',
    10: 'Powers of 3 (give power)',
    11: 'Powers of 3 (give answer)',
    12: 'Sectioned Prime Numbers',
    13: 'Is This Prime?',
    14: 'Combined Practice',
    15: 'Combined Practice (Shortcut)'
}

# --- 2. SESSION STATE INITIALIZATION ---
if 'question' not in st.session_state:
    st.session_state.question = None
if 'answer' not in st.session_state:
    st.session_state.answer = None
if 'current_section' not in st.session_state:
    st.session_state.current_section = 1 # Default to section 1
if 'combined_sections' not in st.session_state:
    st.session_state.combined_sections = []
if 'practice_started' not in st.session_state:
    st.session_state.practice_started = False
if 'section_type' not in st.session_state:
    st.session_state.section_type = 1 # Default to section 1

# We only need this one state for the text box
if 'user_answer_input' not in st.session_state:
    st.session_state.user_answer_input = ""

# --- Add new state for multiplication options ---
if 'mult_min' not in st.session_state:
    st.session_state.mult_min = 2
if 'mult_max' not in st.session_state:
    st.session_state.mult_max = 15
if 'mult_exclude_squares' not in st.session_state:
    st.session_state.mult_exclude_squares = False


# --- 3. QUESTION GENERATOR FUNCTIONS ---
def new_question(section_id):
    """Resets the state and generates a new question for the given section."""
    st.session_state.question = None
    st.session_state.answer = None
    st.session_state.section_type = section_id

    match section_id:
        case 1:
            # --- Read multiplication options from session state ---
            min_val = st.session_state.mult_min
            max_val = st.session_state.mult_max
            exclude_squares = st.session_state.mult_exclude_squares

            # Validate range
            if min_val > max_val:
                st.error("Min number cannot be greater than max number. Fix in sidebar.")
                st.session_state.question = "Error: Fix options in sidebar"
                st.session_state.answer = "" # Set a dummy answer
                return

            a = random.randint(min_val, max_val)
            b = random.randint(min_val, max_val)
            
            # Handle "exclude squares" logic
            if exclude_squares:
                # If the range is just one number (e.g., 5 to 5), we can't exclude squares.
                # So we only run the loop if the range is greater than 0.
                if min_val != max_val:
                    while a == b:
                        b = random.randint(min_val, max_val)
            
            st.session_state.question = f'{a} x {b} = ?'
            st.session_state.answer = str(a * b)
        case 2:
            frac = random.choice(L_FRAC_RARAS)
            st.session_state.question = f'{frac} = ?'
            st.session_state.answer = round(float(eval(frac)), 5)
        case 3:
            frac = random.choice(L_FRAC_RARAS)
            val = round(float(eval(frac)), 5)
            st.session_state.question = f'{val} = ?'
            st.session_state.answer = frac
        case 4:
            frac = random.choice(LT_FRAC_TODAS)
            st.session_state.question = f'{frac} = ?'
            st.session_state.answer = round(float(eval(frac)), 5)
        case 5:
            frac = random.choice(LT_FRAC_TODAS)
            val = round(float(eval(frac)), 5)
            st.session_state.question = f'{val} = ?'
            st.session_state.answer = frac
        case 6:
            base = random.choice(BASES_SQUARES)
            st.session_state.question = f'{base}^2 = ?'
            st.session_state.answer = str(L22_SQUARES[base])
        case 7:
            base = random.choice(BASES_CUBES)
            st.session_state.question = f'{base}^3 = ?'
            st.session_state.answer = str(L3_CUBES[base])
        case 8:
            exp = random.choice(EXPONENTS_L2)
            val = L2_POWERS[exp]
            st.session_state.question = f'{val} = 2^?'
            st.session_state.answer = str(exp)
        case 9:
            exp = random.choice(EXPONENTS_L2)
            st.session_state.question = f'2^{exp} = ?'
            st.session_state.answer = str(L2_POWERS[exp])
        case 10:
            exp = random.choice(EXPONENTS_L3)
            val = L3_POWERS[exp]
            st.session_state.question = f'{val} = 3^?'
            st.session_state.answer = str(exp)
        case 11:
            exp = random.choice(EXPONENTS_L3)
            st.session_state.question = f'3^{exp} = ?'
            st.session_state.answer = str(L3_POWERS[exp])
        case 12:
            p = random.randint(0,9)
            st.session_state.question = f'Primes in the {p*10}s: ?'
            st.session_state.answer = set(PRIMES_LIST[p]) # Store answer as a set
        case 13:
            num = random.choice(IS_PRIME_NUMS)
            st.session_state.question = f'Is {num} prime? (1=Y, 0=N)'
            st.session_state.answer = "1" if num in PRIMES_SET else "0"
        
        case 14 | 15: # Combined practice logic
            if not st.session_state.combined_sections:
                st.error("No sections selected for combined practice!")
                st.session_state.practice_started = False
                return
            
            chosen_section_id = random.choice(st.session_state.combined_sections)
            new_question(chosen_section_id) # Recursively call the generator


# --- 4. SPEED-RUN SUBMISSION HANDLER ---
# This function handles all the logic for Enter/Button click
def handle_submission():
    """Handles the answer submission and state logic."""
    
    # 1. Get the user's answer
    user_input = st.session_state.user_answer_input
    
    # 2. Check if it's empty
    if not user_input and st.session_state.section_type != 12:
        st.warning("Please enter an answer.")
        return

    # 3. Check the answer
    correct = False
    correct_answer_str = str(st.session_state.answer)
    section = st.session_state.section_type

    try:
        if section in [1, 6, 7, 8, 9, 10, 11]:
            correct = (user_input.strip() == correct_answer_str)
        
        elif section in [2, 4]: # Frac to Decimal
            val = st.session_state.answer
            correct = (abs(float(user_input) - val) < 0.001)
        
        elif section in [3, 5]: # Decimal to Frac
            correct = (abs(eval(user_input) - eval(correct_answer_str)) < 0.001)

        elif section == 12: # Primes list
            ans_nums = re.findall(r'\d+', user_input)
            ans_set = set(int(num) for num in ans_nums)
            correct = (ans_set == st.session_state.answer)
            correct_answer_str = ", ".join(map(str, sorted(list(st.session_state.answer))))
            
        elif section == 13: # Is Prime
            correct = (user_input.strip()[-1] == correct_answer_str)
            correct_answer_str = "Yes, Prime" if correct_answer_str == "1" else "No"
    
    except Exception as e:
        st.error(f"Invalid input format. Error: {e}")
        return

    # 4. Handle correct or wrong answer
    if correct:
        st.toast("BIEN! 🎉", icon="✅") # Show a success toast
        new_question(st.session_state.current_section) # Load next question
        st.session_state.user_answer_input = "" # Clear text box
    else:
        # NEW LOGIC: Show a "wrong" toast, clear the box, and that's it.
        # This re-loads the SAME question with a blank box.
        st.toast(f"MAL... {correct_answer_str}", icon="❌")
        st.session_state.user_answer_input = ""


# --- 5. UI LAYOUT ---

# --- Add a callback for when multiplication options change ---
def on_mult_option_change():
    # We only need to generate a new question if we are *currently* in section 1
    if st.session_state.current_section == 1:
        new_question(1)
        st.session_state.user_answer_input = "" # Clear text box

st.set_page_config(layout="wide")
st.title("🧠 GMAT Quant Practice")

# --- Sidebar for Navigation ---
st.sidebar.title("Menu")
section_name = st.sidebar.radio(
    "Select a section:",
    options=ALL_SECTION_NAMES.values(),
    key="menu_selection",
    # Use index to find the ID of the current_section
    index=list(ALL_SECTION_NAMES.keys()).index(st.session_state.current_section) 
)

# Find the section ID from the name
section_id = [k for k, v in ALL_SECTION_NAMES.items() if v == section_name][0]

# --- NEW: Show multiplication options if section 1 is selected ---
if section_id == 1:
    st.sidebar.markdown("---")
    st.sidebar.subheader("Multiplication Options")
    # Bind widgets to session state using key= and trigger callback
    st.sidebar.number_input(
        "Min Number", 
        min_value=2, 
        max_value=99, 
        key="mult_min", 
        on_change=on_mult_option_change
    )
    st.sidebar.number_input(
        "Max Number", 
        min_value=2, 
        max_value=99, 
        key="mult_max", 
        on_change=on_mult_option_change
    )
    st.sidebar.checkbox(
        "Exclude Squares?", 
        key="mult_exclude_squares", 
        on_change=on_mult_option_change
    )

# --- Main Page Logic ---
if st.session_state.current_section != section_id:
    # User has clicked a new section
    st.session_state.current_section = section_id
    st.session_state.practice_started = False
    st.session_state.combined_sections = []
    st.session_state.user_answer_input = "" # Clear text box
    
    if section_id == 15: # For hard-coded section 15
        all_sects = set(range(1, 14))
        exclude_sects = {2, 3, 12}
        st.session_state.combined_sections = sorted(list(all_sects - exclude_sects))
        st.session_state.practice_started = True
    
    if section_id != 14: # Generate first question
        new_question(section_id)
        st.rerun() 
    else:
        st.rerun() # Show section 14 setup screen


# --- Section 14: Combined Practice Setup ---
if st.session_state.current_section == 14 and not st.session_state.practice_started:
    st.header("Combined Practice Setup")
    st.write("Select the sections you want to practice.")
    
    selectable_sections = {k: v for k, v in ALL_SECTION_NAMES.items() if k not in [14, 15]}
    mode = st.radio("Mode:", ("Include", "Exclude"), horizontal=True)
    
    selected_names = st.multiselect(
        f"Sections to {mode.lower()}:",
        options=selectable_sections.values(),
        default=[ALL_SECTION_NAMES[2], ALL_SECTION_NAMES[3], ALL_SECTION_NAMES[12]] if mode == "Exclude" else None
    )
    
    selected_ids = set(k for k, v in selectable_sections.items() if v in selected_names)
    all_ids = set(selectable_sections.keys())

    if st.button("Start Practice"):
        if mode == "Include":
            st.session_state.combined_sections = sorted(list(selected_ids))
        else:
            st.session_state.combined_sections = sorted(list(all_ids - selected_ids))
        
        if not st.session_state.combined_sections:
            st.error("No sections selected! Please select at least one.")
        else:
            st.session_state.practice_started = True
            new_question(14) # Call the combined generator
            st.session_state.user_answer_input = "" # Clear text box
            st.rerun() # Rerun to hide the setup and show the question

# --- Main Question & Answer Area ---
if st.session_state.current_section not in [14] or st.session_state.practice_started:

    # Safety check
    if not st.session_state.question:
        if st.session_state.current_section in [14, 15] and not st.session_state.combined_sections:
            st.warning("Please go back and configure your combined practice (Section 14).")
        else:
            # This is the first run for the selected section
            if st.session_state.current_section:
                 new_question(st.session_state.current_section)
            else:
                # Failsafe, default to section 1
                 new_question(1)
            st.rerun()

    # --- NO MORE ERROR MESSAGE OR BUTTON LOGIC. IT'S ALL IN THE TOAST! ---

    # Display the current question
    if st.session_state.question: # Only show if a question is loaded
        st.header(st.session_state.question)
    
    # --- FINAL UI: The button always says "Check Answer" ---
    col1, col2 = st.columns([3, 1])
    with col1:
        st.text_input(
            "Your Answer:", 
            label_visibility="collapsed", 
            key="user_answer_input", # This key links the widget to st.session_state
            on_change=handle_submission # Calls function when user hits Enter
        )
    with col2:
        st.button(
            "Check Answer", # Button label is now static
            on_click=handle_submission # Calls function when button is clicked
        )