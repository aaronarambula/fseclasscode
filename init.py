# ============================================================
# OBSTACLE DETECTOR - Like a helper for your eyes!
# ============================================================
# Imagine you have a really smart helper that:
#   1. Feels how close things are (like how you hold your hands
#      close together to show something is "this big")
#   2. Buzzes like a bee when something is nearby
#   3. Takes a picture and tells you what it sees
#   4. Talks to you out loud!
# That's what this whole program does!
# ============================================================


# ----------------------------
# GETTING OUR TOOLS READY
# ----------------------------

import time
# "time" is like a stopwatch. We use it to make the program
# wait for a little bit, like counting "1... 2... 3..." before
# doing something again.

import subprocess
# "subprocess" lets our program ask the computer to do things,
# like turning on the camera or playing a sound.
# Think of it like asking a friend to press a button for you.

import base64
# "base64" is a translator. Pictures are made of lots of tiny
# dots, but the AI brain only understands words. base64 turns
# the picture into a secret code made of letters so the AI
# can read it. Like turning a drawing into a description!

import sys
# "sys" helps us show error messages when something goes wrong.
# Like when you spill something and say "Uh oh!" — sys helps
# the computer say "Uh oh!" too.

import os
# "os" lets us talk to the computer itself.
# We use it here to keep our secret keys safe, instead of
# writing them right in the code for everyone to see.

from elevenlabs.client import ElevenLabs
# ElevenLabs is like a magic voice machine.
# You give it words and it talks out loud in a real human voice!
# Like when a storybook reads itself to you.

from openai import OpenAI
# OpenAI is a super smart AI brain (called GPT).
# We send it a picture and it tells us what's in the picture,
# like having a friend who is REALLY good at describing things.

from gpiozero import DistanceSensor, PWMOutputDevice, Button
# gpiozero talks to the little electronic parts plugged into
# our computer (called a Raspberry Pi).
#
# DistanceSensor = the part that figures out how far away
#   something is. It shouts "PING!" and listens for the echo,
#   just like yelling in a cave!
#
# PWMOutputDevice = controls the vibration motor. PWM means we
#   can make it buzz softly or buzz really strong, not just
#   on or off. Like how a phone vibrates harder for some alerts.
#
# Button = a real physical button someone can press with
#   their finger!


# ----------------------------
# CONNECTING TO THE AI BRAIN (OpenAI)
# ----------------------------

client = OpenAI(api_key="")
# This is our "library card" for the AI brain.
# The api_key is like a secret password that proves who we are.
# Without it, the AI won't talk to us!
# ⚠️ Keep this secret — it's like your home address, don't share it!

MODEL = "gpt-5-nano-2025-08-07"
# This is which version of the AI brain we want to use.
# Think of it like picking which friend to call —
# this one is fast and good at describing pictures.


# ----------------------------
# CONNECTING TO THE VOICE MACHINE (ElevenLabs)
# ----------------------------

elevenlabs = ElevenLabs(
    api_key=""
    # This is our "library card" for the voice machine.
    # Just like the OpenAI key above, this is our secret password.
    # ⚠️ Keep this secret too!
)


# ----------------------------
# CAMERA SETTINGS
# ----------------------------

IMAGE_PATH = "captured_image.jpg"
# This is the name we give the photo when we save it.
# Like putting a label on a folder. Every new picture
# will overwrite (replace) this same file.

RESOLUTION = "640x480"
# This is how big the picture will be.
# 640 dots wide and 480 dots tall.
# Like saying "make the drawing 640 squares across and
# 480 squares tall."


# ----------------------------
# FUNCTION: Take a picture
# ----------------------------

def capture_image(path: str):
    # A "function" is like a recipe. You call its name
    # and it follows all the steps inside.
    # This recipe takes one photo and saves it.

    subprocess.run(
        # subprocess.run asks the computer to run a program for us.

        ["fswebcam",     # "fswebcam" is a camera app on our computer
         "-r", RESOLUTION,  # "-r" means "resolution" — how big the photo is
         "-S", "2",      # "-S 2" means skip the first 2 frames while the
                         # camera wakes up. Like blinking when you first
                         # open your eyes in the morning!
         "--no-banner",  # Don't put a text banner on the photo
         path],          # Save the photo to this file name
        check=True       # If something goes wrong, tell us right away
    )


# ----------------------------
# FUNCTION: Turn picture into secret code for the AI
# ----------------------------

def to_data_url(path: str) -> str:
    # The AI brain can't open files on our computer.
    # So we turn the whole picture into a long string of
    # letters and numbers, like a secret code.
    # Then we can send the code to the AI inside a message!

    with open(path, "rb") as f:
        # Open the picture file in "read bytes" mode.
        # "Bytes" are the tiny pieces that make up any file.
        # "rb" means "I want to read the raw pieces, not words."

        b64 = base64.b64encode(f.read()).decode("utf-8")
        # f.read() — read all the tiny pieces
        # base64.b64encode() — turn those pieces into safe letters
        # .decode("utf-8") — make it a normal text string

    return f"data:image/jpeg;base64,{b64}"
    # This puts a little label in front of the code so the AI
    # knows "hey, this is a JPEG picture!" Like writing
    # "THIS IS A PHOTO:" before the secret code.


# ----------------------------
# FUNCTION: Make the computer talk out loud
# ----------------------------

def speak_text(text: str):
    # This is our "talk out loud" recipe.
    # Give it any words and it will say them in a real voice!

    safe_text = text.replace("\n", " ").strip()
    # "\n" is a special invisible character that means "new line"
    # (like pressing Enter). Voice machines don't like those,
    # so we replace them with spaces. .strip() removes any
    # extra spaces at the beginning or end. Like tidying up
    # before going outside!

    if not safe_text:
        return
    # If the text is completely empty after cleaning,
    # there's nothing to say, so we stop here.
    # Like if someone hands you an empty paper to read.

    try:
        # "try" means: attempt this, but if something breaks,
        # don't crash — go to the "except" part instead.

        audio = elevenlabs.text_to_speech.convert(
            # Ask ElevenLabs to turn our words into sound!

            voice_id="IKne3meq5aSn9XLyUdCD",
            # This picks WHICH voice to use. Every voice has an ID,
            # like how every person has a name.
            # We're using "Charlie" — a casual Australian male voice!

            text=safe_text,
            # These are the words we want spoken out loud.

            model_id="eleven_turbo_v2",
            # This is which voice engine to use.
            # "turbo_v2" is fast AND sounds good.
            # Like choosing the fast lane at the grocery store!

            language_code="en"
            # "en" means English. So the voice knows to speak English.
        )

        with open("speech.mp3", "wb") as f:
            for chunk in audio:
                f.write(chunk)
        # The voice comes back in little pieces called "chunks"
        # (like slices of bread). We put all the slices together
        # and save them as a sound file called "speech.mp3".

        subprocess.run(["mpg123", "speech.mp3"], check=False)
        # "mpg123" is a program that plays MP3 sound files.
        # check=False means: even if something goes a little wrong
        # with playing, don't crash the whole program.

    except Exception as e:
        print("TTS Error:", e)
        # If ANYTHING above broke, tell us what went wrong.
        # TTS stands for "Text To Speech."


# ----------------------------
# FUNCTION: Ask the AI what's in the picture
# ----------------------------

def describe_image(path: str) -> str:
    # This recipe sends a photo to the AI brain and asks
    # "what do you see?" Then it gives us the answer as words.

    data_url = to_data_url(path)
    # First, turn the picture into the secret letter-code
    # so we can send it to the AI.

    prompt = (
        "Describe the main visible object(s) in one short sentence. "
        "Also read any visible text exactly as written. "
        "Keep the answer simple and useful."
    )
    # A "prompt" is what we say TO the AI — like asking it a question.
    # We're telling it: describe what you see in one sentence,
    # read any words you spot, and keep it short and easy to understand.

    resp = client.responses.create(
        # Send our message (with the picture!) to the AI brain.

        model=MODEL,
        # Use the model we chose up at the top of the file.

        reasoning={"effort": "low"},
        # "effort: low" means we want a quick answer, not a long
        # think-it-over answer. Like asking a simple question
        # vs. doing homework.

        max_output_tokens=200,
        # Don't write more than 200 "tokens" (roughly 150 words).
        # We only need a short description, not an essay!

        input=[{
            "role": "user",
            # "user" means this message is coming from us (the human).

            "content": [
                {"type": "input_text", "text": prompt},
                # First piece: the question we're asking in words.

                {"type": "input_image", "image_url": data_url}
                # Second piece: the picture (as our secret code).
            ]
        }],
    )

    text = getattr(resp, "output_text", None)
    # Try to get the AI's answer from the response.
    # "getattr" safely looks for "output_text" — if it doesn't
    # exist, it gives us None instead of crashing.

    if text:
        return text.strip()
    # If we got an answer, clean up any extra spaces and give it back.

    return "No response returned. I could not understand the image."
    # If the AI didn't give us anything useful, say so.


# ----------------------------
# HARDWARE SETTINGS — The physical parts!
# ----------------------------

TRIG_PIN = 17
# The "trigger" pin on the distance sensor.
# This is the leg of the sensor that SENDS the ping sound.
# Think of it like a mouth — it yells "HELLO!"

ECHO_PIN = 18
# The "echo" pin on the distance sensor.
# This is the leg that LISTENS for the sound to bounce back.
# Think of it like an ear — it listens for the "hello" echo.

MOTOR_PIN = 27
# This is the pin connected to the vibration motor.
# Pin 27 is like a switch — we turn it on to make it buzz.

BUTTON_PIN = 22
# This is the pin connected to the physical button.
# When someone presses it, pin 22 wakes up and tells our program.

sensor = DistanceSensor(echo=ECHO_PIN, trigger=TRIG_PIN, max_distance=2.0)
# Create the distance sensor and tell it which pins to use.
# max_distance=2.0 means we only care about things within 2 meters
# (about 6.5 feet). Anything farther away we ignore.

motor = PWMOutputDevice(MOTOR_PIN)
# Create the vibration motor.
# PWM lets us control HOW STRONG the buzz is, not just on/off.
# Like how a fan can spin slow or fast.

button = Button(BUTTON_PIN, pull_up=True)
# Create the button on pin 22.
# pull_up=True is an electronics trick that makes the button
# work reliably. Without it, the signal can be "wobbly."


# ----------------------------
# DISTANCE WARNING SETTINGS
# ----------------------------

WARNING_THRESHOLDS = [4.0, 3.0, 2.0, 1.0]
# These are the distances (in feet) where we want to speak a warning.
# Like signs on the road: "4 feet!", "3 feet!", "2 feet!", "1 foot!"

WARNING_MESSAGES = {
    4.0: "Caution. Object four feet ahead.",
    3.0: "Warning. Object three feet ahead.",
    2.0: "Close. Object two feet ahead.",
    1.0: "Stop. Object one foot ahead.",
}
# This is a "dictionary" — like a real dictionary but for our program.
# Each distance number has a matching message to say out loud.
# So when we're 2 feet away, the program looks up 2.0 and
# finds "Close. Object two feet ahead."

last_spoken_threshold = None
# This remembers the last warning we spoke.
# If we already said "2 feet!", we don't want to keep repeating it
# every single loop. None means we haven't said anything yet.

WARNING_COOLDOWN = 2.0
# After saying a warning, wait at least 2 seconds before
# saying the same one again. Like a polite pause.

last_warning_time = 0.0
# This remembers WHEN we last spoke a warning.
# 0.0 means way back at the very start — never yet.


# ----------------------------
# FUNCTION: Say a warning if something is close
# ----------------------------

def check_distance_warnings(distance_ft: float):
    # This recipe looks at how far away something is and
    # decides whether to speak a warning out loud.

    global last_spoken_threshold, last_warning_time
    # "global" means: use the variables from the TOP of the file,
    # not new ones just for this function.
    # Like borrowing a shared toy rather than making a new one.

    current_threshold = None
    # Start by assuming we're not inside any warning zone.

    for t in WARNING_THRESHOLDS:
        # Go through each warning distance one at a time.
        # [4.0, 3.0, 2.0, 1.0]

        if distance_ft <= t:
            current_threshold = t
            # If we're closer than this threshold, remember it.
            # Because the list goes from big to small, the LAST
            # match will be the smallest zone we're inside.
            # Example: 1.5 feet is inside 4ft, 3ft, AND 2ft zones.
            # The loop ends at 2.0 because 1.5 > 1.0, so we land
            # on the 2ft zone — the most urgent one.

    now = time.time()
    # Get the current time in seconds. Like looking at a clock
    # that counts seconds since forever ago.

    if current_threshold is None:
        # We're farther than all the warning zones (more than 4 ft away).
        last_spoken_threshold = None
        # Reset memory so when we come back close, it warns again.
        return
        # "return" means "we're done with this function, go back."

    if (current_threshold != last_spoken_threshold or
            (now - last_warning_time) > WARNING_COOLDOWN):
        # Speak a warning IF:
        #   - We moved into a DIFFERENT zone than last time, OR
        #   - Enough time has passed (more than 2 seconds)
        # This stops the program from saying the same thing
        # over and over really fast!

        speak_text(WARNING_MESSAGES[current_threshold])
        # Look up the right message for this distance and say it.

        last_spoken_threshold = current_threshold
        # Remember which zone we just warned about.

        last_warning_time = now
        # Remember when we said it.


# ----------------------------
# FUNCTION: Update the vibration motor
# ----------------------------

def update_vibration():
    # This recipe runs over and over in our main loop.
    # It checks how far away things are and adjusts the buzzing.

    try:
        distance_m = sensor.distance * sensor.max_distance
        # sensor.distance gives a number between 0 and 1.
        # (0 = touching, 1 = as far as max_distance)
        # We multiply by max_distance (2.0 meters) to get
        # the real distance in meters.

        distance_ft = distance_m * 3.28084
        # Convert meters to feet. There are 3.28084 feet in a meter.
        # Like converting dollars to euros — just multiply!

        if distance_ft <= 4.5:
            # If something is within 4.5 feet, start buzzing!

            intensity = max(0.2, min(1.0, (4.5 - distance_ft) / 4.5))
            # Figure out HOW HARD to buzz.
            #
            # (4.5 - distance_ft) / 4.5 gives a number from 0 to 1:
            #   - At exactly 4.5 ft: (4.5-4.5)/4.5 = 0   (no buzz)
            #   - At exactly 0 ft:   (4.5-0.0)/4.5 = 1.0 (full buzz)
            #
            # min(1.0, ...) makes sure it never goes above 1.0
            # max(0.2, ...) makes sure the minimum buzz is 0.2
            #   (a gentle buzz you can feel, instead of nothing)
            #
            # Like turning up music — closer = louder buzz!

            motor.value = intensity
            # Set the motor to buzz at the intensity we calculated.

        else:
            motor.value = 0
            # Nothing close — motor off. No buzz.

        print(f"Distance: {distance_ft:.4f} ft | Vibration: {motor.value:.4f}")
        # Print the numbers to the screen so we can see what's happening.
        # :.4f means "show 4 decimal places", like 1.2345.

        check_distance_warnings(distance_ft)
        # Also check if we need to say a warning out loud!

    except Exception as e:
        print("Sensor error:", e)
        motor.value = 0
        # If the sensor has a problem, print the error and
        # turn off the motor so it doesn't get stuck buzzing.


# ----------------------------
# FUNCTION: What happens when the button is pressed
# ----------------------------

def on_button_pressed():
    # This recipe runs every time someone physically
    # pushes the button!

    print("Button pressed. Capturing image...")
    # Print a message so we can see it happened.

    try:
        capture_image(IMAGE_PATH)
        # Step 1: Take a picture and save it.

        result = describe_image(IMAGE_PATH)
        # Step 2: Send the picture to the AI and get a description.

        print("OpenAI says:", result)
        # Step 3: Print the description to the screen.

        speak_text(result)
        # Step 4: Say the description out loud!

    except Exception as e:
        print("ERROR:", repr(e), file=sys.stderr)
        # If ANYTHING went wrong in the steps above,
        # print the error. repr() shows ALL the details.
        # sys.stderr is the "error channel" — like a
        # special red marker for problems.


# ----------------------------
# SETTING UP THE BUTTON LISTENER
# ----------------------------

button.when_pressed = on_button_pressed
# This tells the button: "when someone presses you,
# run the on_button_pressed recipe."
# It's like tying a string from the button to a bell —
# press the button, ring the bell!


# ----------------------------
# MAIN LOOP — The heartbeat of the program
# ----------------------------

print("Running... press the button to take a picture.")
# Tell us the program started successfully.

try:
    while True:
        # "while True" means: do this FOREVER until we stop it.
        # Like a merry-go-round that keeps spinning.

        update_vibration()
        # Check the distance and update the motor + warnings.

        time.sleep(0.1)
        # Wait 1/10th of a second before checking again.
        # This is a tiny pause so the program doesn't
        # run SO fast it overheats or uses too much power.
        # Like taking a tiny breath between each check.

except KeyboardInterrupt:
    pass
    # If someone presses Ctrl+C on the keyboard to stop
    # the program, this catches it and lets us clean up
    # nicely instead of crashing with an error message.
    # "pass" means "do nothing — just exit the loop."

finally:
    motor.value = 0
    # "finally" runs no matter what — even if there was an error.
    # ALWAYS turn off the motor when we're done.
    # Like turning off the lights when you leave a room!
