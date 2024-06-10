############################################################
#              GLOBAL VAR DEFAULT VALUES                   #
#----------------------------------------------------------#
# !! THESE VALUES MAY BE OVERRIDDEN OUTSIDE THIS FILE !!   #
############################################################

app_name = "Paul"                                               # Call out name of app for user.  i.e. "Hey Siri"
greetings = ["hello", "hey", "yo", "hi"]                        # Possible callout phrasing for app
command_file = "commands.yaml"                                  # Edit this file to add commands to the system
show_plot_gui = True                                            # View the voice graph, segments and timing in realtime
hugging_face_token = "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"    # HF token
similarity_threshold = .1                                       # Adjust as needed to control the accuracy of identifying the user.
sample_duration = 5                                             # Number of seconds to record speaker registration.
mic_name = "Headset Microphone (CORSAIR VOID ELITE Wireless Gaming Headset)"                    # Use option 5 from the menu to find the device name.
pause_threshold = .5                                            # How loing to wait before terminating listenting.

# DEBUGING
output_to_concole = True            # Output the audio text to the console.