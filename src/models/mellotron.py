from core import TTSModel

class Tacotron2(TTSModel):
    def __init__(self, hparams):
        super(Tacotron2, self).__init__()
        self.mask_padding = hparams.mask_padding
        self.fp16_run = hparams.fp16_run
        self.n_mel_channels = hparams.n_mel_channels
        self.n_frames_per_step = hparams.n_frames_per_step
        self.embedding = nn.Embedding(
            hparams.n_symbols, hparams.symbols_embedding_dim)
        std = sqrt(2.0 / (hparams.n_symbols + hparams.symbols_embedding_dim))
        val = sqrt(3.0) * std  # uniform bounds for std
        self.embedding.weight.data.uniform_(-val, val)
        self.encoder = Encoder(hparams)
        self.decoder = Decoder(hparams)
        self.postnet = Postnet(hparams)
        if hparams.with_gst:
            self.gst = GST(hparams)
        self.speaker_embedding = nn.Embedding(
            hparams.n_speakers, hparams.speaker_embedding_dim)

    def parse_batch(self, batch):
        text_padded, input_lengths, mel_padded, gate_padded, \
            output_lengths, speaker_ids, f0_padded = batch
        text_padded = to_gpu(text_padded).long()
        input_lengths = to_gpu(input_lengths).long()
        max_len = torch.max(input_lengths.data).item()
        mel_padded = to_gpu(mel_padded).float()
        gate_padded = to_gpu(gate_padded).float()
        output_lengths = to_gpu(output_lengths).long()
        speaker_ids = to_gpu(speaker_ids.data).long()
        f0_padded = to_gpu(f0_padded).float()
        return ((text_padded, input_lengths, mel_padded, max_len,
                 output_lengths, speaker_ids, f0_padded),
                (mel_padded, gate_padded))

    def parse_output(self, outputs, output_lengths=None):
        if self.mask_padding and output_lengths is not None:
            mask = ~get_mask_from_lengths(output_lengths)
            mask = mask.expand(self.n_mel_channels, mask.size(0), mask.size(1))
            mask = mask.permute(1, 0, 2)

            outputs[0].data.masked_fill_(mask, 0.0)
            outputs[1].data.masked_fill_(mask, 0.0)
            outputs[2].data.masked_fill_(mask[:, 0, :], 1e3)  # gate energies

        return outputs

    def forward(self, inputs):
        inputs, input_lengths, targets, max_len, \
            output_lengths, speaker_ids, f0s = inputs
        input_lengths, output_lengths = input_lengths.data, output_lengths.data

        embedded_inputs = self.embedding(inputs).transpose(1, 2)
        embedded_text = self.encoder(embedded_inputs, input_lengths)
        embedded_speakers = self.speaker_embedding(speaker_ids)[:, None]
        embedded_gst = self.gst(targets, output_lengths)
        embedded_gst = embedded_gst.repeat(1, embedded_text.size(1), 1)
        embedded_speakers = embedded_speakers.repeat(1, embedded_text.size(1), 1)

        encoder_outputs = torch.cat(
            (embedded_text, embedded_gst, embedded_speakers), dim=2)

        mel_outputs, gate_outputs, alignments = self.decoder(
            encoder_outputs, targets, memory_lengths=input_lengths, f0s=f0s)

        mel_outputs_postnet = self.postnet(mel_outputs)
        mel_outputs_postnet = mel_outputs + mel_outputs_postnet

        return self.parse_output(
            [mel_outputs, mel_outputs_postnet, gate_outputs, alignments],
            output_lengths)

    def inference(self, inputs):
        text, style_input, speaker_ids, f0s = inputs
        embedded_inputs = self.embedding(text).transpose(1, 2)
        embedded_text = self.encoder.inference(embedded_inputs)
        embedded_speakers = self.speaker_embedding(speaker_ids)[:, None]
        if hasattr(self, 'gst'):
            if isinstance(style_input, int):
                query = torch.zeros(1, 1, self.gst.encoder.ref_enc_gru_size).cuda()
                GST = torch.tanh(self.gst.stl.embed)
                key = GST[style_input].unsqueeze(0).expand(1, -1, -1)
                embedded_gst = self.gst.stl.attention(query, key)
            else:
                embedded_gst = self.gst(style_input)

        embedded_speakers = embedded_speakers.repeat(1, embedded_text.size(1), 1)
        if hasattr(self, 'gst'):
            embedded_gst = embedded_gst.repeat(1, embedded_text.size(1), 1)
            encoder_outputs = torch.cat(
                (embedded_text, embedded_gst, embedded_speakers), dim=2)
        else:
            encoder_outputs = torch.cat(
                (embedded_text, embedded_speakers), dim=2)

        mel_outputs, gate_outputs, alignments = self.decoder.inference(
            encoder_outputs, f0s)

        mel_outputs_postnet = self.postnet(mel_outputs)
        mel_outputs_postnet = mel_outputs + mel_outputs_postnet

        return self.parse_output(
            [mel_outputs, mel_outputs_postnet, gate_outputs, alignments])

    def inference_noattention(self, inputs):
        text, style_input, speaker_ids, f0s, attention_map = inputs
        embedded_inputs = self.embedding(text).transpose(1, 2)
        embedded_text = self.encoder.inference(embedded_inputs)
        embedded_speakers = self.speaker_embedding(speaker_ids)[:, None]
        if hasattr(self, 'gst'):
            if isinstance(style_input, int):
                query = torch.zeros(1, 1, self.gst.encoder.ref_enc_gru_size).cuda()
                GST = torch.tanh(self.gst.stl.embed)
                key = GST[style_input].unsqueeze(0).expand(1, -1, -1)
                embedded_gst = self.gst.stl.attention(query, key)
            else:
                embedded_gst = self.gst(style_input)

        embedded_speakers = embedded_speakers.repeat(1, embedded_text.size(1), 1)
        if hasattr(self, 'gst'):
            embedded_gst = embedded_gst.repeat(1, embedded_text.size(1), 1)
            encoder_outputs = torch.cat(
                (embedded_text, embedded_gst, embedded_speakers), dim=2)
        else:
            encoder_outputs = torch.cat(
                (embedded_text, embedded_speakers), dim=2)

        mel_outputs, gate_outputs, alignments = self.decoder.inference_noattention(
            encoder_outputs, f0s, attention_map)

        mel_outputs_postnet = self.postnet(mel_outputs)
        mel_outputs_postnet = mel_outputs + mel_outputs_postnet

        return self.parse_output(
            [mel_outputs, mel_outputs_postnet, gate_outputs, alignments])