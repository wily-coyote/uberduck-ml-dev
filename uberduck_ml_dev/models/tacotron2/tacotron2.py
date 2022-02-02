# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/models.tacotron2.tacotron2.ipynb (unless otherwise specified).

__all__ = ['Tacotron2', 'DEFAULTS', 'config', 'DEFAULTS', 'config', 'NON_ATTENTIVE_DEFAULTS']

# Cell
import pdb
from torch import nn
from ..base import TTSModel
from ..common import Attention, Conv1d, LinearNorm, GST
from ...text.symbols import symbols
from ...vendor.tfcompat.hparam import HParams
from ...utils.utils import to_gpu, get_mask_from_lengths
import numpy as np
import torch
from torch.autograd import Variable
from torch.cuda.amp import autocast
from torch.nn import functional as F
from ...utils.duration import (
    GaussianUpsampling,
    RangePredictor,
    PositionalEncoding,
    DurationPredictor,
)
from .decoder import Decoder
from .encoder import Encoder
from .prenet import Prenet
from .postnet import Postnet

# Cell
from ...data.batch import Batch


class Tacotron2(TTSModel):
    def __init__(self, hparams):
        super().__init__(hparams)

        self.mask_padding = hparams.mask_padding
        self.fp16_run = hparams.fp16_run
        self.pos_weight = hparams.pos_weight
        self.n_mel_channels = hparams.n_mel_channels
        self.n_frames_per_step_initial = hparams.n_frames_per_step_initial
        self.n_frames_per_step_current = hparams.n_frames_per_step_initial
        self.embedding = nn.Embedding(self.n_symbols, hparams.symbols_embedding_dim)
        std = np.sqrt(2.0 / (self.n_symbols + hparams.symbols_embedding_dim))
        val = np.sqrt(3.0) * std  # uniform bounds for std
        self.embedding.weight.data.uniform_(-val, val)
        self.encoder = Encoder(hparams)
        self.decoder = Decoder(hparams)
        self.postnet = Postnet(hparams)
        self.speaker_embedding_dim = hparams.speaker_embedding_dim
        self.encoder_embedding_dim = hparams.encoder_embedding_dim
        self.has_speaker_embedding = hparams.has_speaker_embedding
        self.cudnn_enabled = hparams.cudnn_enabled
        self.non_attentive = hparams.non_attentive
        self.location_specific_attention = hparams.location_specific_attention
        if self.non_attentive:
            self.duration_predictor = DurationPredictor(hparams)

        if self.n_speakers > 1 and not self.has_speaker_embedding:
            raise Exception("Speaker embedding is required if n_speakers > 1")
        if hparams.has_speaker_embedding:
            self.speaker_embedding = nn.Embedding(
                self.n_speakers, hparams.speaker_embedding_dim
            )
        else:
            self.speaker_embedding = None
        if self.n_speakers > 1:
            self.spkr_lin = nn.Linear(
                self.speaker_embedding_dim, self.encoder_embedding_dim
            )
        else:
            self.spkr_lin = lambda a: torch.zeros(
                self.encoder_embedding_dim, device=a.device
            )

        self.gst_init(hparams)

    def gst_init(self, hparams):
        self.gst_lin = None
        self.gst_type = None

        if hparams.get("gst_type") == "torchmoji":
            assert hparams.gst_dim, "gst_dim must be set"
            self.gst_type = hparams.get("gst_type")
            self.gst_lin = nn.Linear(hparams.gst_dim, self.encoder_embedding_dim)
            print("Initialized Torchmoji GST")
        else:
            print("Not using any style tokens")

    def parse_batch(self, batch: Batch):

        # pdb.set_trace()
        durations_padded = batch.durations_padded
        text_int_padded = batch.text_int_padded
        input_lengths = batch.input_lengths
        mel_padded = batch.mel_padded
        gate_target = batch.gate_target
        output_lengths = batch.output_lengths
        speaker_ids = batch.speaker_ids
        embedded_gst = batch.gst
        f0_padded = batch.f0_padded
        gate_pred = batch.gate_pred

        if self.cudnn_enabled:
            text_int_padded = to_gpu(text_int_padded).long()
            input_lengths = to_gpu(input_lengths).long()
            mel_padded = to_gpu(mel_padded).float()
            gate_target = to_gpu(gate_target).float()
            speaker_ids = to_gpu(speaker_ids).long()
            output_lengths = to_gpu(output_lengths).long()
            gate_pred = to_gpu(output_lengths).long()
            if durations_padded is not None:
                durations_padded = to_gpu(durations_padded).long()
            if embedded_gst is not None:
                embedded_gst = to_gpu(embedded_gst).float()

        # max_len = torch.max(input_lengths.data).item()
        ret_x = Batch(
            text_int_padded=text_int_padded,
            input_lengths=input_lengths,
            mel_padded=mel_padded,
            gate_pred=gate_pred,
            output_lengths=output_lengths,
            speaker_ids=speaker_ids,
            gst=embedded_gst,
            durations_padded=durations_padded,
            f0_padded=f0_padded,
            # max_len=max_len,
        )
        if self.location_specific_attention:
            # pdb.set_trace()
            ret_y = Batch(mel_padded=mel_padded, gate_target=gate_target)
        if self.non_attentive:
            ret_y = Batch(mel_padded=mel_padded, durations_padded=durations_padded)

        return (ret_x, ret_y)

    def parse_output(self, outputs, output_lengths=None):

        if self.mask_padding and output_lengths is not None:
            mask = ~get_mask_from_lengths(output_lengths)
            mask = mask.expand(self.n_mel_channels, mask.size(0), mask.size(1))
            mask = F.pad(mask, (0, outputs.mel_outputs.size(2) - mask.size(2)))
            mask = mask.permute(1, 0, 2)

            outputs.mel_outputs.data.masked_fill_(mask, 0.0)
            outputs.mel_outputs_postnet.data.masked_fill_(mask, 0.0)
            if self.location_specific_attention:
                outputs.gate_pred.data.masked_fill_(mask[:, 0, :], 1e3)

        return outputs

    @torch.no_grad()
    def get_alignment(self, inputs):
        (
            input_text,
            input_lengths,
            targets,
            max_len,
            output_lengths,
            speaker_ids,
            *_,
        ) = inputs

        input_lengths, output_lengths = input_lengths.data, output_lengths.data

        embedded_inputs = self.embedding(input_text).transpose(1, 2)
        embedded_text = self.encoder(embedded_inputs, input_lengths)
        encoder_outputs = embedded_text
        if self.speaker_embedding:
            embedded_speakers = self.speaker_embedding(speaker_ids)[:, None]
            encoder_outputs += self.spkr_lin(embedded_speakers)

        encoder_outputs = torch.cat((encoder_outputs,), dim=2)

        mel_outputs, gate_pred, alignments = self.decoder(
            encoder_outputs,
            targets,
            input_lengths=input_lengths,
            encoder_output_lengths=input_lengths,
        )
        return alignments

    def forward(self, inputs: Batch):
        input_text = inputs.text_int_padded
        input_lengths = inputs.input_lengths
        targets = inputs.mel_padded
        output_lengths = inputs.output_lengths
        speaker_ids = inputs.speaker_ids
        gst = inputs.gst
        durations_padded = inputs.durations_padded
        # max_len = inputs.max_len

        input_lengths, output_lengths = input_lengths.data, output_lengths.data

        embedded_inputs = self.embedding(input_text).transpose(1, 2)
        embedded_text = self.encoder(embedded_inputs, input_lengths)
        encoder_outputs = embedded_text
        if self.speaker_embedding:
            embedded_speakers = self.speaker_embedding(speaker_ids)[:, None]
            encoder_outputs += self.spkr_lin(embedded_speakers)

        if self.gst_lin is not None:
            assert (
                gst is not None
            ), f"embedded_gst is None but gst_type was set to {self.gst_type}"
            encoder_outputs += self.gst_lin(gst)
        #         encoder_outputs = torch.cat((encoder_outputs,), dim=2)

        if self.location_specific_attention:
            # pdb.set_trace()
            mel_outputs, gate_pred, alignments = self.decoder(
                encoder_outputs=encoder_outputs,
                decoder_inputs=targets,
                encoder_output_lengths=input_lengths,
                # output_lengths=input_lengths,
                output_lengths=output_lengths,
            )

        if self.non_attentive:
            predicted_durations = self.decoder.duration_predictor(
                encoder_outputs, input_lengths.cpu()
            )
            # pdb.set_trace()
            mel_outputs, predicted_durations = self.decoder(
                encoder_outputs=encoder_outputs,
                decoder_inputs=targets,
                # output_lengths=input_lengths,
                output_lengths=output_lengths,
                input_lengths=input_lengths,
                durations=durations_padded,
            )

        # pdb.set_trace()
        mel_outputs_postnet = self.postnet(mel_outputs)
        mel_outputs_postnet = mel_outputs + mel_outputs_postnet

        if self.location_specific_attention:
            output_raw = Batch(
                mel_outputs=mel_outputs,
                mel_outputs_postnet=mel_outputs_postnet,
                gate_pred=gate_pred,
                output_lengths=output_lengths,
                alignments=alignments,
            )

        if self.non_attentive:
            output_raw = Batch(
                predicted_durations=predicted_durations,
                mel_outputs=mel_outputs,
                mel_outputs_postnet=mel_outputs_postnet,
            )

        output = self.parse_output(output_raw, output_lengths)
        return output

    @torch.no_grad()
    def inference(self, inputs: Batch):
        # text, input_lengths, speaker_ids, embedded_gst, *_ = inputs
        text_int_padded = inputs.text_int_padded
        input_lengths = inputs.input_lengths
        speaker_ids = inputs.speaker_ids
        gst = inputs.gst

        embedded_inputs = self.embedding(text_int_padded).transpose(1, 2)
        embedded_text = self.encoder.inference(embedded_inputs, input_lengths)
        encoder_outputs = embedded_text
        if self.speaker_embedding:
            embedded_speakers = self.speaker_embedding(speaker_ids)[:, None]
            encoder_outputs += self.spkr_lin(embedded_speakers)

        if self.gst_lin is not None:
            assert (
                gst is not None
            ), f"embedded_gst is None but gst_type was set to {self.gst_type}"
            encoder_outputs += self.gst_lin(gst)
        #         encoder_outputs = torch.cat((encoder_outputs,), dim=2)

        mel_outputs, gate_pred, alignments, mel_lengths = self.decoder.inference(
            encoder_outputs, input_lengths
        )
        mel_outputs_postnet = self.postnet(mel_outputs)
        mel_outputs_postnet = mel_outputs + mel_outputs_postnet

        return self.parse_output(
            [mel_outputs, mel_outputs_postnet, gate_pred, alignments, mel_lengths]
        )

    @torch.no_grad()
    def inference_noattention(self, inputs):
        """Run inference conditioned on an attention map."""
        text, input_lengths, speaker_ids, attention_maps = inputs
        embedded_inputs = self.embedding(text).transpose(1, 2)
        embedded_text = self.encoder.inference(embedded_inputs, input_lengths)

        encoder_outputs = torch.cat((embedded_text,), dim=2)

        mel_outputs, gate_pred, alignments = self.decoder.inference_noattention(
            encoder_outputs, attention_maps
        )
        mel_outputs_postnet = self.postnet(mel_outputs)
        mel_outputs_postnet = mel_outputs + mel_outputs_postnet

        return self.parse_output(
            [mel_outputs, mel_outputs_postnet, gate_pred, alignments]
        )

    @torch.no_grad()
    def inference_partial_tf(
        self, inputs, tf_mel, tf_until_idx,
    ):
        """Run inference with partial teacher forcing.

        Teacher forcing is done until tf_until_idx in the mel spectrogram.
        Make sure you pass the mel index and not the text index!

        tf_mel: (B, T, n_mel_channels)
        """
        text, input_lengths, *_ = inputs
        embedded_inputs = self.embedding(text).transpose(1, 2)
        embedded_text = self.encoder.inference(embedded_inputs, input_lengths)
        encoder_outputs = torch.cat((embedded_text,), dim=2)

        mel_outputs, gate_pred, alignments = self.decoder.inference_partial_tf(
            encoder_outputs, tf_mel, tf_until_idx,
        )

        mel_outputs_postnet = self.postnet(mel_outputs)
        mel_outputs_postnet = mel_outputs + mel_outputs_postnet

        return self.parse_output(
            [mel_outputs, mel_outputs_postnet, gate_pred, alignments]
        )

# Cell
from ...vendor.tfcompat.hparam import HParams
from ..base import DEFAULTS as MODEL_DEFAULTS

DEFAULTS = HParams(
    symbols_embedding_dim=512,
    fp16_run=False,
    mask_padding=True,
    n_mel_channels=80,
    # encoder parameters
    encoder_kernel_size=5,
    encoder_n_convolutions=3,
    encoder_embedding_dim=512,
    # decoder parameters
    coarse_n_frames_per_step=None,
    decoder_rnn_dim=1024,
    prenet_dim=256,
    prenet_f0_n_layers=1,
    prenet_f0_dim=1,
    prenet_f0_kernel_size=1,
    prenet_rms_dim=0,
    prenet_fms_kernel_size=1,
    max_decoder_steps=1000,
    gate_threshold=0.5,
    p_attention_dropout=0.1,
    p_decoder_dropout=0.1,
    p_teacher_forcing=1.0,
    pos_weight=None,
    # attention parameters
    attention_rnn_dim=1024,
    attention_dim=128,
    # location layer parameters
    attention_location_n_filters=32,
    attention_location_kernel_size=31,
    # mel post-processing network parameters
    postnet_embedding_dim=512,
    postnet_kernel_size=5,
    postnet_n_convolutions=5,
    n_speakers=1,
    speaker_embedding_dim=128,
    # reference encoder
    with_gst=False,
    ref_enc_filters=[32, 32, 64, 64, 128, 128],
    ref_enc_size=[3, 3],
    ref_enc_strides=[2, 2],
    ref_enc_pad=[1, 1],
    filter_length=1024,
    hop_length=256,
    include_f0=False,
    ref_enc_gru_size=128,
    symbol_set="nvidia_taco2",
    num_heads=8,
    text_cleaners=["english_cleaners"],
    sampling_rate=22050,
    checkpoint_name=None,
    max_wav_value=32768.0,
    mel_fmax=8000,
    mel_fmin=0,
    n_frames_per_step_initial=1,
    win_length=1024,
    has_speaker_embedding=False,
    gst_type=None,
    torchmoji_model_file=None,
    torchmoji_vocabulary_file=None,
    sample_inference_speaker_ids=None,
    sample_inference_text="That quick beige fox jumped in the air loudly over the thin dog fence.",
    distributed_run=False,
    cudnn_enabled=False,
    # compute_durations=False,
    non_attentive=False,
    location_specific_attention=True,
    include_durations=False,
    compute_durations=False,
)

config = DEFAULTS.values()
config.update(MODEL_DEFAULTS.values())
DEFAULTS = HParams(**config)

# Cell
from ...vendor.tfcompat.hparam import HParams
from ..base import DEFAULTS as MODEL_DEFAULTS

config = DEFAULTS.values()
config.update(
    dict(
        # compute_durations=True,
        non_attentive=True,
        positional_embedding_dim=32,
        range_lstm_dim=1024,
        duration_lstm_dim=1024,
        location_specific_attention=False,
        cudnn_enabled=True,
        include_durations=True,
        compute_durations=True,
        decoder_rnn_dim_nlayers=2,
    )
)
config.update(MODEL_DEFAULTS.values())
NON_ATTENTIVE_DEFAULTS = HParams(**config)