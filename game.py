# ================================================================
# 0. IMPORTS AND API SETUP
# ================================================================
import os
import random

import streamlit as st
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key) if api_key else None

MODEL_NAME = "gemini-3.5-flash-lite"
# ================================================================
# 1. PAGE SETUP
# ================================================================
st.set_page_config(page_title="ART GALLERY HEIST", page_icon="🎨", layout="centered")
st.title("🎨 ART GALLERY HEIST")
#===============================================================
# 2. GAME STATE SETUP
# ================================================================
# "game_started" flag in st.session_state (set once, False by default)
if "game_started" not in st.session_state:
    st.session_state.game_started = False

# ================================================================
# 3. GAME FLOW FUNCTIONS
# ================================================================
# start_game(name): set health, max_health, inventory, rooms list,
#                   room_number, result values, action_complete
# restart_game(): clear session state, rerun
# get_current_room(): return rooms[room_number]
# continue_game(): clear last result, room_number += 1, rerun

def start_game(name):
    """Set the same starting values and five-room route as the final app."""
    st.session_state.game_started = True
    st.session_state.player_name = name
    st.session_state.health = 10
    st.session_state.max_health = 10
    st.session_state.inventory = ["Torch"]
    st.session_state.rooms = [ "foyer", "corridor", "cctv", "gallery",
        "vault", "getaway", "exit"]
    st.session_state.room_number = 0
    st.session_state.result_type = ""
    st.session_state.result_message = ""
    st.session_state.result_value = ""
    st.session_state.action_complete = False
def restart_game():
    st.session_state.clear()
    st.rerun()
 
def get_current_room():
    """Use the room number to find the name of the current room."""
    return st.session_state.rooms[st.session_state.room_number]
room = get_current_room
     
def continue_game():
    """Clear the last action and move to the next room."""
    st.session_state.result_type = ""
    st.session_state.result_message = ""
    st.session_state.result_value = ""
    st.session_state.action_complete = False
    st.session_state.room_number += 1
    st.rerun()

def show_room(title, description):
    """Display a room heading and its description."""
    st.header(title)
    st.write(description)

def show_player_info():
    st.subheader(f"🕴 {st.session_state.player_name} ")
    left, right = st.columns(2)
    with left:
        st.write(f"🔥 Health: {st.session_state.health} / {st.session_state.max_health}")
    with right:
        st.write(f"👜 Inventory: {', '.join(st.session_state.inventory)}")  
    st.caption(
        f"Room {st.session_state.room_number + 1}"
        f"of {len(st.session_state.rooms)}"
    )
    st.divider()
def show_result():
    # [UPDATE] Replace yesterday's show_result() with this whole function.
    kind = st.session_state.result_type
    value = st.session_state.result_value
 
    if kind == "item":
        st.success(f"👜 NEW ITEM: {value}")
    elif kind == "damage":
        st.error(f"💔 DAMAGE: You lose {value} health.")
    elif kind == "heal":
        st.success(f"💚 HEALED: You recover {value} health.")
    elif kind == "success":
        st.success("✅ Success!")
    else:
        st.info("The heist continues...")
 
    st.write(st.session_state.result_message)
 
 
def show_continue_button(text = "Continue"):
    if st.button(text):
        continue_game()
# ================================================================
# 4. INVENTORY AND HEALTH HELPERS
# ================================================================
# add_item(item)
# has_item(item)
# remove_item(item)
# take_damage(amount): never let health go below 0
# heal_player(amount): never go above max_health

def add_item(item):
    if item not in st.session_state.inventory:
                    st.session_state.inventory.append(item)
 
def has_item(item):
     return item in st.session_state.inventory
 
def remove_item(item):
     if item in st.session_state.inventory:
                         st.session_state.inventory.remove(item)

def take_damage(amount):
    st.session_state.health = st.session_state.health - amount
    if st.session_state.health < 0:
        st.session_state.health = 0
# def heal_player(amount):
#     old_health = st.session_state.health
#     st.session_state.health = min(st.session_state.max_health, st.session_state.health + amount)
#     return st.session_state.health - old_health
# ================================================================
# 5. AI STORYTELLER (GEMINI)
# ================================================================
# generate_story(room, action, outcome, fallback_message)
#   - return fallback if client is None
#   - build the prompt (player, room, health, inventory, action, outcome, rules)
#   - try the API call, return fallback on empty result or error
def generate_story(room, action, outcome, fallback_message):
    if client is None:
        return fallback_message
    inventory_text = ",".join(st.session_state.inventory)
    prompt = f"""
You are the storyteller for a art gallery heist called Heist escape.
 
Player: {st.session_state.player_name}
Room: {room}
Health: {st.session_state.health}/{st.session_state.max_health}
Inventory: {inventory_text}
 
Action:
{action}
 
Outcome:
{outcome}
 
Describe what happens in 30-50 words.
 
Use second person.
Use mysterious and thrilling language.
Do not change the outcome.
Do not change health or inventory.
Do not introduce new choices.
"""
 
    try:
        interaction = client.interactions.create(
            model="gemini-3.5-flash-lite",
            input=prompt,
            generation_config={"thinking_level": "minimal"}
        )
        if interaction.output_text:
            return interaction.output_text
        return fallback_message
    except Exception as error:
        st.error(f"Gemini error: {error}")
        return fallback_message

# ================================================================
# 6. DICE AND RESULT LOGIC
# ================================================================
# roll_dice(): random 1-6
# set_result(result_type, message, value): store result, action_complete = True, rerun
# chance_encounter(...): ONE button, roll dice, add bonus_item +2 if owned,
#                        success -> story + set_result("success")
#                        failure -> take_damage + story + set_result("damage")

def roll_dice():
    return random.randint(1, 6)
 
def chance_encounter(button_text, room, action, success_number, success_outcome, success_fallback, failure_outcome, failure_fallback, damage, bonus_item=""):
    if st.button(button_text):
        roll = roll_dice()
        if bonus_item != "" and has_item(bonus_item):
            roll = roll + 2
        if roll >= success_number:
            story = generate_story(room, action, success_outcome, success_fallback)
            set_result("success", story)
        else:
            take_damage(damage)
            story = generate_story(room, action, failure_outcome, failure_fallback)
            set_result("damage", story, damage)
        st.rerun
# ================================================================
# 7. REUSABLE DISPLAY FUNCTIONS
# ================================================================
# show_room(title, description)
# show_continue_button(text)
# show_player_info(): name, health, inventory, "Room X of Y", divider


def set_result(result_type, message, value=None):
    st.session_state.result_type = result_type
    st.session_state.result_message = message
    st.session_state.result_value = value
    st.session_state.action_complete = True
    st.rerun()

# ================================================================
# 8. START SCREEN
# ================================================================
# if not game_started:
#   intro text, name input, "Enter the Foyer" button
#   validate name is not empty, then start_game(name) and rerun
if not st.session_state.game_started:

    st.write("It is heist day you wake up with a mix of excitment and nerves, You are not leaving empty handed.")

    name = st.text_input("What is your name?")

    if st.button("Enter the Gallery"):
        if name.strip():
            start_game(name)
            st.rerun()
        else:
            st.warning("Enter your name first before starting.")

else:

    # Game has started, so health now exists.
    show_player_info()

    # Check whether the player has died.
    if st.session_state.health <= 0:

        show_room(
            "💀 Game Over",
            "You got caught! You failed your mission."
        )

        st.error("You did not complete the heist .")

        if st.button("🔄 Try Again"):
            restart_game()

        st.stop()

    # Only get the room after confirming the game is running.
    room = get_current_room()

# ================================================================
# 9. MAIN GAME FLOW (the order of these checks matters)
# ================================================================
# else:
#   show_player_info()
#
#   9a. GAME OVER SCREEN   -> health <= 0, restart button
#   9b. WIN SCREEN         -> room_number >= len(rooms), balloons, play again
#   9c. OUTCOME SCREEN     -> action_complete, show result, continue button
#   9d. ROOM SCREEN        -> get_current_room(), then the room checks below


# ================================================================
# 10. ROOMS (inside 9d, one block per room)
# ================================================================
# Each block: show_room(title, description) then ONE chance_encounter(...)
#
#   10a. foyer
    if room == "foyer":

        show_room(
            "🏛️ The foyer",
            "You walk into the gallery, today is the day"
        )

        show_continue_button("🚪 Leave the foyer")
#   10b. corridor
    elif room == "corridor":

        show_room(
            "🚶‍♂️ The Corridor",
            "You open your bag one last time to check you have everything."
        )

        if not st.session_state.action_complete:

            left, right = st.columns(2)

            with left:
                if st.button("🔎 Open your bag"):
                    add_item("Black gloves")
                    set_result(
                        "item",
                        "You find your black gloves inside the bag. How could you forget? You put them on immediately.",
                        "Black gloves"
                    )   

            with right:
                if st.button("➡️ Don't open your bag"):
                    st.session_state.health -= 3
                    st.session_state.fingerprints_left = True
                    set_result(
                        "story",
                        "You close your bag, worried it will draw attention. Your bare hands brush the door handle and the wall as you move on... (-3 health)"
                    )

        else:
            show_result()
            show_continue_button()
#   10c. cctv
    elif room == "cctv":

        show_room(
        "📹 The CCTV room",
        "A wall of screens flickers in front of you. A guard's coffee is still warm on the desk. "
        "Every camera in the building is watching, and one of them is watching you."
    )

        if not st.session_state.action_complete:

            left, right = st.columns(2)

        with left:
            if st.button("🔁 Loop the footage"):
                roll = random.randint(1, 6)
                st.session_state.dice_roll = roll
                if roll >= 3:
                    st.session_state.cameras = "looped"
                    set_result(
                        "story",
                        f"🎲 You rolled a {roll}. Your fingers fly over the keyboard and the screens "
                        "replay ten calm minutes on repeat. Nobody will notice a thing."
                    )
                else:
                    st.session_state.cameras = "live"
                    st.session_state.health -= 2
                    set_result(
                        "story",
                        f"🎲 You rolled a {roll}. The loop glitches and a red light blinks on the "
                        "panel. The cameras are still recording, and you've probably been seen. (-2 health)"
                    )

            if st.button("🔌 Switch the cameras off"):
                st.session_state.cameras = "off"
                st.session_state.health -= 2
                set_result(
                    "story",
                    "You pull the power. The screens go black, but a silent alarm pings "
                    "somewhere in the building. (-2 health)"
                )

        with right:
            if st.button("🪪 Grab the security pass and go"):
                st.session_state.cameras = "live"
                st.session_state.health -= 2
                add_item("Security pass")
                set_result(
                    "item",
                    "You swipe the pass off the desk and run. You can feel the cameras "
                    "following you out. (-2 health)",
                    "Security pass"
                )

            if st.button("➡️ Ignore the screens"):
                st.session_state.cameras = "live"
                st.session_state.health -= 3
                set_result(
                    "story",
                    "You walk past without touching anything. Every camera catches your face. (-3 health)"
                )

    else:
        show_result()
        show_continue_button()
#   10d. gallery
#   10e. vault      (uses the bonus item)
#   10f. getaway
#   10g. exit       (the final else)
#ending
def get_ending(health, gloves_on, cameras, double):
    if health <= 0:
        return "TRAPPED"        # police are on their way
    if not gloves_on or cameras == "live":
        return "TRACED"         # you got out, but they have evidence
    if double == "painting+jewels":
        return "PERFECT HEIST"  # gloves, no CCTV, vault looted
    return "CLEAN ESCAPE"       # painting only, no traces