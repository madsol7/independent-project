# ================================================================
# 0. IMPORTS AND API SETUP
# ================================================================
# os, random, streamlit, dotenv, genai
# load_dotenv(), read GEMINI_API_KEY, create client (or None if no key)
# MODEL_NAME constant


# ================================================================
# 1. PAGE SETUP
# ================================================================
# st.set_page_config(...)
# st.title(...)
#===============================================================
# 2. GAME STATE SETUP
# ================================================================
# "game_started" flag in st.session_state (set once, False by default)


# ================================================================
# 3. GAME FLOW FUNCTIONS
# ================================================================
# start_game(name): set health, max_health, inventory, rooms list,
#                   room_number, result values, action_complete
# restart_game(): clear session state, rerun
# get_current_room(): return rooms[room_number]
# continue_game(): clear last result, room_number += 1, rerun


# ================================================================
# 4. INVENTORY AND HEALTH HELPERS
# ================================================================
# add_item(item)
# has_item(item)
# remove_item(item)
# take_damage(amount): never let health go below 0
# heal_player(amount): never go above max_health


# ================================================================
# 5. AI STORYTELLER (GEMINI)
# ================================================================
# generate_story(room, action, outcome, fallback_message)
#   - return fallback if client is None
#   - build the prompt (player, room, health, inventory, action, outcome, rules)
#   - try the API call, return fallback on empty result or error


# ================================================================
# 6. DICE AND RESULT LOGIC
# ================================================================
# roll_dice(): random 1-6
# set_result(result_type, message, value): store result, action_complete = True, rerun
# chance_encounter(...): ONE button, roll dice, add bonus_item +2 if owned,
#                        success -> story + set_result("success")
#                        failure -> take_damage + story + set_result("damage")


# ================================================================
# 7. REUSABLE DISPLAY FUNCTIONS
# ================================================================
# show_room(title, description)
# show_continue_button(text)
# show_player_info(): name, health, inventory, "Room X of Y", divider


# ================================================================
# 8. START SCREEN
# ================================================================
# if not game_started:
#   intro text, name input, "Enter the Foyer" button
#   validate name is not empty, then start_game(name) and rerun


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
#   10b. corridor
#   10c. cctv
#   10d. gallery
#   10e. vault      (uses the bonus item)
#   10f. getaway
#   10g. exit       (the final else)