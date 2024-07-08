from dotenv import load_dotenv
import os
import argparse
import azure.cognitiveservices.speech as speech_sdk
import uuid
from azure.ai.translation.text import TranslatorCredential, TextTranslationClient
from azure.ai.translation.text.models import InputTextItem
from playsound import playsound

def main():
    try:
        global speech_config

        # Get Configuration Settings
        load_dotenv()
        ai_key = os.getenv('SPEECH_KEY')
        ai_region = os.getenv('SPEECH_REGION')
        translate_key = os.getenv('TRANSLATE_KEY')
        translate_region = os.getenv('TRANSLATOR_REGION')
        translate_endpoint = os.getenv('TRANSLATE_ENDPOINT')

        # Ensure endpoint does not end with a slash
        if translate_endpoint.endswith('/'):
            translate_endpoint = translate_endpoint[:-1]

        # Check that translate_endpoint is correct
        print(f"Using translate endpoint: {translate_endpoint}")

        # Configure argument parser
        parser = argparse.ArgumentParser(description='Speech to Text with automatic language detection and translation')
        parser.add_argument('audio_file', type=str, help='Path to the audio file for transcription')
        args = parser.parse_args()

        # Configure speech service
        speech_config = speech_sdk.SpeechConfig(subscription=ai_key, region=ai_region)
        print('Ready to use speech service in:', speech_config.region)

        # Configure translation service
        credential = TranslatorCredential(translate_key, translate_region)
        client = TextTranslationClient(endpoint=translate_endpoint, credential=credential)
        print('Translation service ready to use.')

        # Get spoken input
        command, detected_language = TranscribeCommand(args.audio_file)

        # Translate the detected command to English
        translated_command = translate_text(client, command, detected_language)
        if translated_command:
            print(f"Translation succeed !")
        else:
            print("Translation failed.")

    except Exception as ex:
        print(ex)

def TranscribeCommand(audio_file):
    command = ''
    detected_language = ''

    try:
        # Configure speech recognition
        audio_config = speech_sdk.AudioConfig(filename=audio_file)

        # Create a speech recognizer with auto-detect language configuration
        auto_detect_source_language_config = speech_sdk.AutoDetectSourceLanguageConfig(languages=["en-US", "fr-FR", "ja-JP", "it-IT"])
        speech_recognizer = speech_sdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config, auto_detect_source_language_config=auto_detect_source_language_config)

        # Process speech input
        speech = speech_recognizer.recognize_once_async().get()
        if speech.reason == speech_sdk.ResultReason.RecognizedSpeech:
            detected_language = speech.properties.get(speech_sdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult)
            command = speech.text
            print(f"Detected language: {detected_language}")
            #print(f"Original command: {command}")
        else:
            print(f"Speech recognition failed: {speech.reason}")
            if speech.reason == speech_sdk.ResultReason.Canceled:
                cancellation = speech.cancellation_details
                print(f"Cancellation reason: {cancellation.reason}")
                print(f"Error details: {cancellation.error_details}")

    except Exception as ex:
        print(f"Speech recognition failed: {ex}")

    # Return the recognized command and detected language
    return command, detected_language

def translate_text(client, text_to_translate, detected_language):
    try:
        # Construct body of request
        input_text_elements = [InputTextItem(text=text_to_translate)]

        # Translate the text to English
        translation_response = client.translate(content=input_text_elements, to=["en"])
        translation = translation_response[0] if translation_response else None

        # Extract translated text from response
        if translation:
            source_language = translation.detected_language
            for translated_text in translation.translations:
                print(f"'{text_to_translate}' was translated from {source_language.language} to {translated_text.to} as '{translated_text.text}'.")
                return translated_text.text

    except Exception as ex:
        print(f"Translation failed: {ex}")
        return None

if __name__ == "__main__":
    main()
