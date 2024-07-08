from dotenv import load_dotenv
import os
import argparse
import azure.cognitiveservices.speech as speech_sdk
from azure.ai.translation.text import TranslatorCredential, TextTranslationClient
from azure.ai.translation.text.models import InputTextItem
from azure.cognitiveservices.speech.audio import AudioOutputConfig
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
            print(f"Original command in {detected_language}: {command}")
            print(f"Translated command in English: {translated_command}")

            # Ask for a response in English
            response = input("Enter your response in English: ")

            # Translate the response to the detected language
            translated_response = translate_text_to_original_language(client, response, detected_language)

            if translated_response:
                print(f"Translated response in {detected_language}: {translated_response}")
                # Speak the translated response in the detected language
                text_to_speech(translated_response, detected_language, ai_key, ai_region)
            else:
                print("Translation of response failed.")

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
        # Translate the text to English
        input_text_elements = [InputTextItem(text=text_to_translate)]
        translation_response = client.translate(content=input_text_elements, to=["en"])
        translation = translation_response[0] if translation_response else None

        # Check if translation was successful
        if translation:
            source_language = translation.detected_language
            for translated_text in translation.translations:
                return translated_text.text

    except Exception as ex:
        print(f"Translation failed: {ex}")
        return None

def translate_text_to_original_language(client, text_to_translate, original_language):
    try:
        # Translate the text to original language
        input_text_elements = [InputTextItem(text=text_to_translate)]
        translation_response = client.translate(content=input_text_elements, to=[original_language])
        translation = translation_response[0] if translation_response else None

        # Check if translation was successful
        if translation:
            for translated_text in translation.translations:
                return translated_text.text

    except Exception as ex:
        print(f"Translation to original language failed: {ex}")
        return None

def text_to_speech(text_to_speak, language, ai_key, ai_region):
    try:
        # Configure speech synthesis
        speech_config = speech_sdk.SpeechConfig(subscription=ai_key, region=ai_region)

        # Configure language for text-to-speech
        if language.startswith("en"):
            speech_config.speech_synthesis_language = "en-US"
        elif language.startswith("fr"):
            speech_config.speech_synthesis_language = "fr-FR"
        elif language.startswith("ja"):
            speech_config.speech_synthesis_language = "ja-JP"
        elif language.startswith("it"):
            speech_config.speech_synthesis_language = "it-IT"

        audio_config = AudioOutputConfig(use_default_speaker=True)

        # Create a speech synthesizer
        synthesizer = speech_sdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        # Speak the text
        result = synthesizer.speak_text_async(text_to_speak).get()

        if result.reason == speech_sdk.ResultReason.SynthesizingAudioCompleted:
            print(f"Successfully synthesized speech in {language}: {text_to_speak}")

        elif result.reason == speech_sdk.ResultReason.Canceled:
            cancellation = result.cancellation_details
            print(f"Speech synthesis canceled: {cancellation.reason}")
            if cancellation.reason == speech_sdk.CancellationReason.Error:
                print(f"Error details: {cancellation.error_details}")

    except Exception as ex:
        print(f"Speech synthesis failed: {ex}")

if __name__ == "__main__":
    main()