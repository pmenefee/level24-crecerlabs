############################################################
#              GLOBAL VAR DEFAULT VALUES                   #
#----------------------------------------------------------#
# !! THESE VALUES MAY BE OVERRIDDEN OUTSIDE THIS FILE !!   #
############################################################

app_name = "Paul"                                               # Call out name of app for user.  i.e. "Hey Siri"
greetings = ["hello", "hey", "yo", "hi"]                        # Possible callout phrasing for app
command_file = "commands.yaml"                                  # Edit this file to add commands to the system
show_plot_gui = True                                            # View the voice graph, segments and timing in realtime
RTTM_output_file = "file.rttm"
hugging_face_token = "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"    # HF token

# DEBUGING
output_to_concole = True            # Output the audio text to the console.
test_controller = "SR"              # which stream to test.  [SR | VR]  SR = Speech, VR = Voice