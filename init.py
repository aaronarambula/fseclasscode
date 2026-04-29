import time
import subprocess
import base64
import sys
import os
from elevenlabs.client import ElevenLabs
from openai import OpenAI
from gpiozero import DistanceSensor, PWMOutputDevice, Button

# --- API Configuration ---
client = OpenAI(api_key="YOUR_OPENAI_KEY")
MODEL = "gpt-5-nano-2025-08-07"

elevenlabs = ElevenLabs(api_key="YOUR_ELEVENLABS_KEY")

# --- Camera & Image Settings ---
IMAGE_PATH = "captured_image.jpg"
RESOLUTION = "640x480"

def capture_image(path: str):
    """Captures a frame using fswebcam, skipping 2 frames for warm-up."""
    subprocess.run(
        ["fswebcam", "-r", RESOLUTION, "-S", "2", "--no-banner", path],
        check=True
    )

def to_data_url(path: str) -> str:
    """Encodes local image to base64 data URL for API transmission."""
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"

# --- Audio & AI Functions ---
def speak_text(text: str):
    """Converts text to speech using ElevenLabs and plays via mpg123."""
    safe_text = text.replace("\n", " ").strip()
    if not safe_text:
        return

    try:
        audio = elevenlabs.text_to_speech.convert(
            voice_id="IKne3meq5aSn9XLyUdCD", # Charlie (AU)
            text=safe_text,
            model_id="eleven_turbo_v2",
            language_code="en"
        )

        with open("speech.mp3", "wb") as f:
            for chunk in audio:
                f.write(chunk)

        subprocess.run(["mpg123", "speech.mp3"], check=False)
    except Exception as e:
        print(f"TTS Error: {e}")

def describe_image(path: str) -> str:
    """Sends image to OpenAI for a concise description and OCR."""
    data_url = to_data_url(path)
    prompt = (
        "Describe the main visible object(s) in one short sentence. "
        "Also read any visible text exactly as written. Keep it simple."
    )

    resp = client.responses.create(
        model=MODEL,
        reasoning={"effort": "low"},
        max_output_tokens=200,
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {"type": "input_image", "image_url": data_url}
            ]
        }],
    )

    text = getattr(resp, "output_text", None)
    return text.strip() if text else "No response returned."

# --- Hardware Configuration (GPIO) ---
TRIG_PIN = 17
ECHO_PIN = 18
MOTOR_PIN = 27
BUTTON_PIN = 22

sensor = DistanceSensor(echo=ECHO_PIN, trigger=TRIG_PIN, max_distance=2.0)
motor = PWMOutputDevice(MOTOR_PIN)
button = Button(BUTTON_PIN, pull_up=True)

# --- Proximity Logic ---
WARNING_THRESHOLDS = [4.0, 3.0, 2.0, 1.0]
WARNING_MESSAGES = {
    4.0: "Caution. Object four feet ahead.",
    3.0: "Warning. Object three feet ahead.",
    2.0: "Close. Object two feet ahead.",
    1.0: "Stop. Object one foot ahead.",
}

last_spoken_threshold = None
last_warning_time = 0.0
WARNING_COOLDOWN = 2.0

def check_distance_warnings(distance_ft: float):
    """Triggers voice warnings based on predefined distance thresholds."""
    global last_spoken_threshold, last_warning_time
    current_threshold = None

    for t in WARNING_THRESHOLDS:
        if distance_ft <= t:
            current_threshold = t

    now = time.time()
    if current_threshold is None:
        last_spoken_threshold = None
        return

    if (current_threshold != last_spoken_threshold or 
        (now - last_warning_time) > WARNING_COOLDOWN):
        speak_text(WARNING_MESSAGES[current_threshold])
        last_spoken_threshold = current_threshold
        last_warning_time = now

def update_vibration():
    """Adjusts haptic feedback intensity based on obstacle proximity."""
    try:
        distance_ft = (sensor.distance * sensor.max_distance) * 3.28084
        
        if distance_ft <= 4.5:
            # Linear scaling: closer distance = higher intensity
            intensity = max(0.2, min(1.0, (4.5 - distance_ft) / 4.5))
            motor.value = intensity
        else:
            motor.value = 0

        print(f"Dist: {distance_ft:.2f}ft | Motor: {motor.value:.2f}")
        check_distance_warnings(distance_ft)
    except Exception as e:
        print(f"Sensor Error: {e}")
        motor.value = 0

def on_button_pressed():
    """Event handler for image capture and AI analysis."""
    print("Capturing...")
    try:
        capture_image(IMAGE_PATH)
        result = describe_image(IMAGE_PATH)
        print(f"AI: {result}")
        speak_text(result)
    except Exception as e:
        print(f"Task Error: {e}", file=sys.stderr)

# --- Execution ---
button.when_pressed = on_button_pressed

print("System Active. Press button for AI description.")
try:
    while True:
        update_vibration()
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nShutting down...")
finally:
    motor.value = 0 # Ensure haptics stop on exit
