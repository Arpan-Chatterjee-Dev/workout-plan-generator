import streamlit as st
from typing import List
from dotenv import load_dotenv
from groq import Groq

GROQ_MODEL="openai/gpt-oss-20b"

load_dotenv()
def generate_workout_plan(
            goal:str,
            experience:str,
            days_per_week:int,
            equipment:List[str],
            injuries:str)->str:

  if not 1 <= days_per_week <= 7:
        return "Please select between 1 and 7 workout days."
  if not equipment:
        return "Please select at least one equipment option."
  
  system_prompt=f"""
  You are an expert fitness trainer specialized in providing customized fitness plans based on user preference.
  Below are the strict requirement that the generated plan needs follow:
   1. plan needs to be to day-to-day basis for {days_per_week} day(s) a week
   2. For each exercise, provide:
      i) Exercise name
     ii) Basic instructions
    iii) Number of sets
     iv) Number of repetitions
      v) Rest period between sets
   3. Respect the user's experience level and fitness goal.
   4. Use ONLY the equipment available to the user. Do not suggest exercises requiring unavailable equipment.
   5. Consider the user's reported injuries or limitations. Avoid exercises that conflict with those limitations.
   6. Do not make any medical claims. 
   7. If the user reports any injury or physical limitation,
      include a disclaimer advising them to consult an appropriate healthcare professional before performing exercises that
      may aggravate their condition.
   8. Return a clearly formatted, practical workout plan.
  """
  user_prompt=f"""
  User preferences:
   User's fitness goal is to {goal}. User is {experience} in doing workouts. User wants to workout only {days_per_week} day(s) of the week.
   User's access to workout equipment is {",".join(equipment)}.
   User's previously reported injuries are {injuries or "None"}
  """
  try:
   llm = Groq()
   response=llm.chat.completions.create(model=GROQ_MODEL,
                              messages=[
                               {"role":"system","content":system_prompt},
                               {"role":"user","content":user_prompt}
                                       ])
   if not response.choices:
    return "Unable to generate a workout plan. Please try again."
   content = response.choices[0].message.content
   if not content or not content.strip():
    return "The AI returned an empty response. Please try again."
   return content
  except Exception as e:
    print(f"Error generating workout plan: {e}")
    return "Sorry, cannot generate the plan now! Try again after a while"

def build_UI():
 st.set_page_config("Workout Plan Generator")
 st.markdown(
    "<h1 style='text-align: center;'>Workout Plan Generator</h1>",
    unsafe_allow_html=True)
 st.markdown(
    "<span style='font-weight:bold; color:yellow;'>Enter Your Fitness Goal</span>",
    unsafe_allow_html=True
 )
 with st.form(key="user_form"):
  selected_goal=st.selectbox(label="Fitness Goal",options=["Build muscle","Lose fat","General fitness","Improve endurance"])
  experience_level=st.selectbox(label="Experience Level",options=["Beginner","Intermediate","Advanced"])
  no_of_days=st.slider("Number of Days",min_value=1, max_value=7)
  equipment_access=st.multiselect(label="Equipment Access",options=["No equipment","Home dumbbells","Full gym"])
  injury_info=st.text_area("Any Injuries?",max_chars=100)
  pressed=st.form_submit_button("Generate Plan")
  if pressed:
   if not equipment_access:
    st.warning("Please select your available equipment.")
   elif "No equipment" in equipment_access and len(equipment_access) >1:
    st.warning("Conflicting equipment availability selection")  
   else:
     with st.spinner("Generating your workout plan..."):
      plan=generate_workout_plan(
            goal=selected_goal,
            experience=experience_level,
            days_per_week=no_of_days,
            equipment=equipment_access,
            injuries=injury_info
        )
      st.markdown(plan)
if __name__=="__main__":
   build_UI()
