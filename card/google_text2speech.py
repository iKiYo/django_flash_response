"""Synthesizes speech from the input string of text or ssml.

Note: ssml must be well-formed according to:
    https://www.w3.org/TR/speech-synthesis/
"""
import os
import errno
from google.cloud import texttospeech


def get_speech_audio(file_name, input_text):
    # Instantiates a client
    client = texttospeech.TextToSpeechClient()#.\
    #         from_service_account_json(
    #             'flash-response-project-3facbd35462e.json'
    #             )

    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=input_text)

    # Build the voice request, select the language code ("en-US") and the ssml
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Wavenet-D",
        ssml_gender=texttospeech.SsmlVoiceGender.MALE,
    )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    # Create the user media directory if it does not exist
    if not os.path.exists(os.path.dirname(file_name)):
        try:
            os.makedirs(os.path.dirname(file_name))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    # The response's audio_content is binary.
    with open(file_name+".mp3", "wb+") as out:
        # Write the response to the output file.
        out.write(response.audio_content)
        print(F'Audio content written to file {file_name}.mp3')
        
