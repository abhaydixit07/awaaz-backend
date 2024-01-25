from flask import Flask, jsonify, request
from flask_cors import CORS
import sounddevice as sd
from scipy.io.wavfile import write
import os
from openai import OpenAI
import random

app = Flask(__name__)
CORS(app)

COUPLED = {}
OPENAI_API_KEY = "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"  # Replace with your actual OpenAI API key
FS = 44100  # Sample rate
SECONDS = 5  # Duration of recording

SOUND_REFERENCE = {
    'S': 'SH',
    'F': 'TH',
    'L': 'R',
    'B': 'V',
    'P': 'F',
    'D': 'T'
}
LETTERS = ['S', 'F', 'L', 'B', 'P', 'T']
EXAMPLE = {
    'S': 'sunday',
    'F': 'free',
    'L': 'love',
    'B': 'boat',
    'P': 'pen',
    'T': 'tree'
}
PRONUNCIATION = {
    "sunday": "sʌn.deɪ",
    # Add more pronunciation examples as needed
}

REMEDY = {
    'P': ['Put your lips together to make the sound. ', "Vocal cords don't vibrate for voiceless sounds."],
    'B': ['Put your lips together to make the sound. '],
    'M': ['Put your lips together to make the sound. ', 'Air flows through your nose.'],
    'W': ['Put your lips together and shape your mouth like you are saying "oo".'],
    'F': ['Place your bottom lip against your upper front teeth. ', 'Top teeth may be on your bottom lip.'],
    'V': ['Place your bottom lip against your upper front teeth. ', 'Top teeth may be on your bottom lip.'],
    'S': ['Keep your teeth close together to make the sound. ',
          'The ridge right behind your two front teeth is involved. ', 'The front of your tongue is used. ',
          "Vocal cords don't vibrate for voiceless sounds."],
    'Z': ['Keep your teeth close together to make the sound. ',
          'The ridge right behind your two front teeth is involved. ', 'The front of your tongue is used.'],
    'th': ['Place your top teeth on your bottom lip and let your tongue go between your teeth for the sound. ',
           'The front of your tongue is involved.'],
    'TH': [
        'Place your top teeth on your bottom lip and let your tongue go between your teeth for the sound (as in thin). ',
        'The front of your tongue is involved.'],
    'N': ['Air flows through your nose. ', 'The ridge right behind your two front teeth is involved. ',
          'The front of your tongue is used.'],
    'NG': ['Air flows through your nose.'],
    'SING': ['Air flows through your nose.'],
    'L': ['The ridge right behind your two front teeth is involved. ', 'The front of your tongue is used.'],
    'T': ['The ridge right behind your two front teeth is involved. ', 'The front of your tongue is used. ',
          "Vocal cords don't vibrate for voiceless sounds."],
    'D': ['The ridge right behind your two front teeth is involved. ', 'The front of your tongue is used.'],
    'CH': ['The front-roof of your mouth is the right spot for the sound.'],
    'J': ['The front-roof of your mouth is the right spot for the sound. ', 'The front of your tongue is used.'],
    'SH': ['The front-roof of your mouth is the right spot for the sound. ', 'The front of your tongue is used.'],
    'ZH': ['The front-roof of your mouth is the right spot for the sound. ', 'The front of your tongue is used.'],
    'K': ['The back-roof of your mouth is the right spot for the sound. ', 'The back of your tongue is used. ',
          "Vocal cords don't vibrate for voiceless sounds."],
    'G': ['The back-roof of your mouth is the right spot for the sound. ', 'The back of your tongue is used.'],
    'R': ['The back-roof of your mouth is the right spot for the sound. ', 'The back of your tongue is used.'],
    'Y': ['The front of your tongue is used.'],
    'CH': ['The front of your tongue is used.'],
    'H': ['Your lungs provide the airflow for every sound, especially this one.']
}

UPLOAD_FOLDER = 'uploads'  # Folder to store uploaded audio
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def check(word_given, word_received, check_for):
    para = word_given != word_received
    while word_given != word_received:
        if word_received[0:len(SOUND_REFERENCE[check_for])] == SOUND_REFERENCE[check_for]:
            remedy_list = {
                "remedy_list": REMEDY[check_for]
            }
            return jsonify(remedy_list)
        else:
            output = {
                "output": "PLEASE TRY AGAIN WRONG PRONUNCIATION"
            }
            return jsonify(output)
    print('VERY GOOD!! Correct pronunciation \n')


def audio_to_text(file_path):
    client = OpenAI(api_key=OPENAI_API_KEY)
    audio_file = open(file_path, "rb")
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="text"
    )
    print(transcript)
    return transcript


@app.route("/generate_word", methods=["GET"])
def generate_word():
    global COUPLED
    COUPLED = random.choice(LETTERS)
    word_data = {
        "word1": EXAMPLE[COUPLED[0]],
        "letter": COUPLED[0],
    }
    return jsonify(word_data)


@app.route('/record_audio', methods=['POST'])
def record_audio():
    global COUPLED
    try:
        # Check if 'audio' is in the request files
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"})

        # Get the audio file from the request
        audio_file = request.files['audio']

        # Save the audio file
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], 'recorded_audio.wav')
        audio_file.save(audio_path)

        # Convert audio to text using OpenAI Whisper or your preferred method
        word_from_user = audio_to_text(audio_path)

        # Perform pronunciation check
        output_from_check_word = check(EXAMPLE[COUPLED[0]].upper(), word_from_user.upper(), COUPLED[0])

        # Return both the generated word and the output
        return jsonify({
            "generatedWord": EXAMPLE[COUPLED[0]],
            "output": output_from_check_word.get_json().get('output')
        })

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": "An error occurred during audio processing."})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
