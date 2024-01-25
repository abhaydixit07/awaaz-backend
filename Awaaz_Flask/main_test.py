import random
import sounddevice as sd
from flask import Flask, jsonify
from flask_cors import CORS
from openai import OpenAI
from scipy.io.wavfile import write

app = Flask(__name__)
CORS(app)

COUPLED = {}
OPENAI_API_KEY = "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"  # Replace with your actual OpenAI API key
FS = 44100  # Sample rate
SECONDS = 3  # Duration of recording

SOUND_REFERENCE = {
    'S': 'SH',
    'F': 'TH',
    'L': 'R',
    'B': 'V',
    'P': 'F',
    'T': 'D'
}
LETTERS = ['S', 'F', 'L', 'B', 'P', 'T']
WRONG_WORDS = {
    'sunday': 'shunday',
    'free': 'three',
    'love': 'Rove',
    'boat': 'Voat',
    'pen': 'Fen',
    'tree': 'Dree'
}
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
    "free": "friː",
    "love": "lʌv",
    "boat": "boʊt",
    "pen": "pen",
    "tree": "triː"

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
        'Place your top teeth on your bottom lip and let your tongue go between your teeth for the sound (as in thin).',
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
    'H': ['Your lungs provide the airflow for every sound, especially this one.']
}


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


def check(word_given, word_recieved, check_for):
    if word_recieved[0:len(SOUND_REFERENCE[check_for])] == SOUND_REFERENCE[check_for]:
        remedy_list = {
            "remedy_list": REMEDY[check_for]
        }
        return jsonify(remedy_list)
    else:
        output = {
            "output": word_given+word_recieved
        }
        return jsonify(output)


@app.route('/record_audio', methods=['POST'])
def record_audio():
    global COUPLED
    try:
        myrecording = sd.rec(int(SECONDS * FS), samplerate=FS, channels=2)
        sd.wait()  # Wait until recording is finished

        # Print the path where the file will be saved
        print("Saving recording to: output.wav")

        # Save the recording to output.wav
        write('output.wav', FS, myrecording)

        word_from_user = audio_to_text("output.wav")

        output_from_check_word = check(EXAMPLE[COUPLED[0]].upper(), word_from_user.upper(), COUPLED[0])

        # Return both the generated word and the output
        return jsonify({
            "generatedWord": EXAMPLE[COUPLED[0]],
            "output": output_from_check_word.get_json().get('output')
        })

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": "An error occurred."})


def incre(count):
    count.count += 1


@app.route("/generate_word", methods=["GET"])
def generate_word():
    letter = random.choice(LETTERS)

    word_data = {
        "word1": EXAMPLE[letter],
        "pronuciation": PRONUNCIATION[EXAMPLE[letter]],
        "letter": letter,
        "wrong": WRONG_WORDS[EXAMPLE[letter]],
        "remedy": REMEDY[letter]

    }

    return jsonify(word_data)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
