# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/data_loader.ipynb (unless otherwise specified).

__all__ = ['TextMelDataset', 'TextMelCollate']

# Cell
import os
import random
import re
from pathlib import Path
from typing import List

import numpy as np
from scipy.io.wavfile import read
import torch
from torch.utils.data import Dataset

from .models.common import STFT, MelSTFT
from .text.util import text_to_sequence
from .utils.audio import compute_yin
from .utils.utils import load_filepaths_and_text


# Cell


def _orig_to_dense_speaker_id(speaker_ids):
    speaker_ids = sorted(list(set(speaker_ids)))
    return {orig: idx for orig, idx in zip(speaker_ids, range(len(speaker_ids)))}


class TextMelDataset(Dataset):
    def __init__(
        self,
        audiopaths_and_text: str,
        text_cleaners: List[str],
        p_arpabet: float,
        n_mel_channels: int,
        sample_rate: int,
        mel_fmin: float,
        mel_fmax: float,
        filter_length: int,
        hop_length: int,
        win_length: int,
        max_wav_value: float = 32768.0,
        include_f0: bool = False,
        pos_weight: float = 10,
        f0_min: int = 80,
        f0_max: int = 880,
        harmonic_thresh=0.25,
        debug: bool = False,
        debug_dataset_size: int = None,
    ):
        super().__init__()
        path = audiopaths_and_text
        self.audiopaths_and_text = load_filepaths_and_text(path)
        self.text_cleaners = text_cleaners
        self.p_arpabet = p_arpabet
        self.stft = MelSTFT(
            filter_length=filter_length,
            hop_length=hop_length,
            win_length=win_length,
            n_mel_channels=n_mel_channels,
            sampling_rate=sample_rate,
            mel_fmin=mel_fmin,
            mel_fmax=mel_fmax,
        )
        self.max_wav_value = max_wav_value
        self.sample_rate = sample_rate
        self.filter_length = filter_length
        self.hop_length = hop_length
        self.mel_fmin = mel_fmin
        self.mel_fmax = mel_fmax
        self.include_f0 = include_f0
        self.f0_min = f0_min
        self.f0_max = f0_max
        self.harmonic_threshold = harmonic_thresh
        # speaker id lookup table
        speaker_ids = [i[2] for i in self.audiopaths_and_text]
        self._speaker_id_map = _orig_to_dense_speaker_id(speaker_ids)
        self.debug = debug
        self.debug_dataset_size = debug_dataset_size

    def _get_f0(self, audio):
        f0, harmonic_rates, argmins, times = compute_yin(
            audio,
            self.sample_rate,
            self.filter_length,
            self.hop_length,
            self.f0_min,
            self.f0_max,
            self.harmonic_threshold,
        )
        pad = int((self.filter_length / self.hop_length) / 2)
        f0 = [0.0] * pad + f0 + [0.0] * pad
        f0 = np.array(f0, dtype=np.float32)
        return f0

    def _get_data(self, audiopath_and_text):
        path, transcription, speaker_id = audiopath_and_text
        speaker_id = self._speaker_id_map[speaker_id]
        sample_rate, wav_data = read(path)
        text_sequence = torch.LongTensor(
            text_to_sequence(
                transcription, self.text_cleaners, p_arpabet=self.p_arpabet
            )
        )
        audio = torch.FloatTensor(wav_data)
        audio_norm = audio / self.max_wav_value
        audio_norm = audio_norm.unsqueeze(0)
        melspec = self.stft.mel_spectrogram(audio_norm)
        melspec = torch.squeeze(melspec, 0)
        if not self.include_f0:
            return (text_sequence, melspec, speaker_id)
        f0 = self._get_f0(audio.data.cpu().numpy())
        f0 = torch.from_numpy(f0)[None]
        f0 = f0[:, : melspec.size(1)]

        return (text_sequence, melspec, speaker_id, f0)

    def __getitem__(self, idx):
        """Return"""
        return self._get_data(self.audiopaths_and_text[idx])

    def __len__(self):
        if self.debug and self.debug_dataset_size:
            return min(self.debug_dataset_size, len(self.audiopaths_and_text))
        return len(self.audiopaths_and_text)

# Cell


class TextMelCollate:
    def __init__(self, n_frames_per_step: int = 1, include_f0: bool = False):
        self.n_frames_per_step = n_frames_per_step
        self.include_f0 = include_f0

    def __call__(self, batch):
        """Collate's training batch from normalized text and mel-spectrogram
        PARAMS
        ------
        batch: [text_normalized, mel_normalized, speaker_id]
        """
        # Right zero-pad all one-hot text sequences to max input length
        input_lengths, ids_sorted_decreasing = torch.sort(
            torch.LongTensor([len(x[0]) for x in batch]), dim=0, descending=True
        )
        max_input_len = input_lengths[0]

        text_padded = torch.LongTensor(len(batch), max_input_len)
        text_padded.zero_()
        for i in range(len(ids_sorted_decreasing)):
            text = batch[ids_sorted_decreasing[i]][0]
            text_padded[i, : text.size(0)] = text

        # Right zero-pad mel-spec
        num_mels = batch[0][1].size(0)
        max_target_len = max([x[1].size(1) for x in batch])
        if max_target_len % self.n_frames_per_step != 0:
            max_target_len += (
                self.n_frames_per_step - max_target_len % self.n_frames_per_step
            )
            assert max_target_len % self.n_frames_per_step == 0

        # include mel padded, gate padded and speaker ids
        mel_padded = torch.FloatTensor(len(batch), num_mels, max_target_len)
        mel_padded.zero_()
        gate_padded = torch.FloatTensor(len(batch), max_target_len)
        gate_padded.zero_()
        output_lengths = torch.LongTensor(len(batch))
        speaker_ids = torch.LongTensor(len(batch))
        if self.include_f0:
            f0_padded = torch.FloatTensor(len(batch), 1, max_target_len)
            f0_padded.zero_()

        for i in range(len(ids_sorted_decreasing)):
            mel = batch[ids_sorted_decreasing[i]][1]
            mel_padded[i, :, : mel.size(1)] = mel
            gate_padded[i, mel.size(1) - 1 :] = 1
            output_lengths[i] = mel.size(1)
            speaker_ids[i] = batch[ids_sorted_decreasing[i]][2]
            if self.include_f0:
                f0 = batch[ids_sorted_decreasing[i]][3]
                f0_padded[i, :, : f0.size(1)] = f0

        # NOTE(zach): would model_inputs be better as a namedtuple or dataclass?
        if self.include_f0:
            model_inputs = (
                text_padded,
                input_lengths,
                mel_padded,
                gate_padded,
                output_lengths,
                speaker_ids,
                f0_padded,
            )
        else:
            model_inputs = (
                text_padded,
                input_lengths,
                mel_padded,
                gate_padded,
                output_lengths,
                speaker_ids,
            )

        return model_inputs