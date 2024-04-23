# will be using https://huggingface.co/speechbrain/tts-tacotron2-ljspeech

import torchaudio
from speechbrain.inference.TTS import Tacotron2
from speechbrain.inference.vocoders import HIFIGAN
import datetime

# Intialize TTS (tacotron2) and Vocoder (HiFIGAN)
tacotron2 = Tacotron2.from_hparams(source="speechbrain/tts-tacotron2-ljspeech", savedir="tmpdir_tts")
hifi_gan = HIFIGAN.from_hparams(source="speechbrain/tts-hifigan-ljspeech", savedir="tmpdir_vocoder")
storage_path = 'tts/'

def text_to_speech(text):
    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    mel_output, mel_length, alignment = tacotron2.encode_text(text)
    waveforms = hifi_gan.decode_batch(mel_output)
    torchaudio.save(storage_path + now + '.wav',waveforms.squeeze(1), 22050)