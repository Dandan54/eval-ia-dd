# Speech to Text and Translation Script

This repository contains a Python script that uses Azure Cognitive Services to convert speech to text, translate the detected text into English, and synthesize translated text into speech. It supports automatic language detection and requires appropriate Azure services credentials.

## Prerequisites

- Python 3.x
- Azure Speech Service subscription
- Azure Translator Text subscription

## Setup

1. **Clone the repository**:

   git clone https://github.com/Dandan54/eval-ia-dd.git    
   cd eval-ia-dd

2. **Fill the env file with your information**:

   SPEECH_KEY=your_speech_key  
   SPEECH_REGION=your_speech_region  
   TRANSLATE_KEY=your_translate_key  
   TRANSLATOR_REGION=your_translator_region  
   TRANSLATE_ENDPOINT=https://<your-translator-resource-name>.cognitiveservices.azure.com  

- Replace the placeholders with your actual Azure credentials.

3. **Usage**:

   python main.py path_to_audio_file

- Replace path_to_audio_file with the path to the audio file you want.


