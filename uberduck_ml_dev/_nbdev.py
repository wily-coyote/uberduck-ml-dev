# AUTOGENERATED BY NBDEV! DO NOT EDIT!

__all__ = ["index", "modules", "custom_doc_links", "git_url"]

index = {"ensure_speaker_table": "data.cache.ipynb",
         "STANDARD_MULTISPEAKER": "data.parse.ipynb",
         "STANDARD_SINGLESPEAKER": "data.parse.ipynb",
         "VCTK": "data.parse.ipynb",
         "word_frequencies": "data.statistics.ipynb",
         "create_wordcloud": "data.statistics.ipynb",
         "count_frequency": "data.statistics.ipynb",
         "pace_character": "data.statistics.ipynb",
         "pace_phoneme": "data.statistics.ipynb",
         "get_sample_format": "data.statistics.ipynb",
         "AbsoluteMetrics": "data.statistics.ipynb",
         "oversample": "data_loader.ipynb",
         "TextMelDataset": "data_loader.ipynb",
         "TextMelCollate": "data_loader.ipynb",
         "TextAudioSpeakerLoader": "data_loader.ipynb",
         "TextAudioSpeakerCollate": "data_loader.ipynb",
         "DistributedBucketSampler": "data_loader.ipynb",
         "get_summary_statistics": "exec.dataset_statistics.ipynb",
         "calculate_statistics": "exec.dataset_statistics.ipynb",
         "generate_markdown": "exec.dataset_statistics.ipynb",
         "parse_args": "utils.exec.ipynb",
         "run": "exec.train_vits.ipynb",
         "CACHE_LOCATION": "exec.generate_filelist.ipynb",
         "FORMATS": "exec.parse_data.ipynb",
         "batch": "exec.preprocess_vits.ipynb",
         "flatten": "exec.preprocess_vits.ipynb",
         "write_filenames": "exec.split_train_val.ipynb",
         "VITSEncoder": "models.attentions.ipynb",
         "Decoder": "models.tacotron2.ipynb",
         "MultiHeadAttention": "models.gradtts.ipynb",
         "FFN": "models.gradtts.ipynb",
         "TTSModel": "models.base.ipynb",
         "Conv1d": "models.common.ipynb",
         "LinearNorm": "models.common.ipynb",
         "LocationLayer": "models.common.ipynb",
         "Attention": "models.common.ipynb",
         "STFT": "models.common.ipynb",
         "MelSTFT": "models.common.ipynb",
         "ReferenceEncoder": "models.common.ipynb",
         "STL": "models.common.ipynb",
         "GST": "models.common.ipynb",
         "LayerNorm": "models.gradtts.ipynb",
         "Flip": "models.common.ipynb",
         "Log": "models.common.ipynb",
         "ElementwiseAffine": "models.common.ipynb",
         "DDSConv": "models.common.ipynb",
         "ConvFlow": "models.common.ipynb",
         "WN": "models.common.ipynb",
         "ResidualCouplingLayer": "models.common.ipynb",
         "ResBlock1": "vocoders.hifigan.ipynb",
         "ResBlock2": "vocoders.hifigan.ipynb",
         "LRELU_SLOPE": "vocoders.hifigan.ipynb",
         "BaseModule": "models.gradtts.ipynb",
         "Mish": "models.gradtts.ipynb",
         "Upsample": "models.gradtts.ipynb",
         "Downsample": "models.gradtts.ipynb",
         "Rezero": "models.gradtts.ipynb",
         "Block": "models.gradtts.ipynb",
         "ResnetBlock": "models.gradtts.ipynb",
         "LinearAttention": "models.gradtts.ipynb",
         "Residual": "models.gradtts.ipynb",
         "SinusoidalPosEmb": "models.gradtts.ipynb",
         "GradLogPEstimator2d": "models.gradtts.ipynb",
         "get_noise": "models.gradtts.ipynb",
         "Diffusion": "models.gradtts.ipynb",
         "sequence_mask": "utils.utils.ipynb",
         "fix_len_compatibility": "models.gradtts.ipynb",
         "fix_len_compatibility_text_edit": "models.gradtts.ipynb",
         "convert_pad_shape": "utils.utils.ipynb",
         "generate_path": "utils.utils.ipynb",
         "duration_loss": "models.gradtts.ipynb",
         "ConvReluNorm": "models.gradtts.ipynb",
         "DurationPredictor": "models.vits.ipynb",
         "Encoder": "models.tacotron2.ipynb",
         "TextEncoder": "models.vits.ipynb",
         "GradTTS": "models.gradtts.ipynb",
         "DEFAULTS": "models.vits.ipynb",
         "Postnet": "models.tacotron2.ipynb",
         "Prenet": "models.tacotron2.ipynb",
         "Mellotron": "models.mellotron.ipynb",
         "Tacotron2": "models.tacotron2.ipynb",
         "piecewise_rational_quadratic_transform": "models.transforms.ipynb",
         "searchsorted": "models.transforms.ipynb",
         "unconstrained_rational_quadratic_spline": "models.transforms.ipynb",
         "rational_quadratic_spline": "models.transforms.ipynb",
         "DEFAULT_MIN_BIN_WIDTH": "models.transforms.ipynb",
         "DEFAULT_MIN_BIN_HEIGHT": "models.transforms.ipynb",
         "DEFAULT_MIN_DERIVATIVE": "models.transforms.ipynb",
         "StochasticDurationPredictor": "models.vits.ipynb",
         "ResidualCouplingBlock": "models.vits.ipynb",
         "PosteriorEncoder": "models.vits.ipynb",
         "Generator": "vocoders.hifigan.ipynb",
         "DiscriminatorP": "vocoders.hifigan.ipynb",
         "DiscriminatorS": "vocoders.hifigan.ipynb",
         "MultiPeriodDiscriminator": "vocoders.hifigan.ipynb",
         "SynthesizerTrn": "models.vits.ipynb",
         "CMUDict": "text.cmudict.ipynb",
         "valid_symbols": "text.cmudict.ipynb",
         "symbols": "text.symbols.ipynb",
         "symbols_nvidia_taco2": "text.symbols.ipynb",
         "symbols_with_ipa": "text.symbols.ipynb",
         "grad_tts_symbols": "text.symbols.ipynb",
         "DEFAULT_SYMBOLS": "text.symbols.ipynb",
         "IPA_SYMBOLS": "text.symbols.ipynb",
         "NVIDIA_TACO2_SYMBOLS": "text.symbols.ipynb",
         "GRAD_TTS_SYMBOLS": "text.symbols.ipynb",
         "SYMBOL_SETS": "text.symbols.ipynb",
         "symbols_to_sequence": "text.symbols.ipynb",
         "arpabet_to_sequence": "text.symbols.ipynb",
         "should_keep_symbol": "text.symbols.ipynb",
         "symbol_to_id": "text.symbols.ipynb",
         "id_to_symbol": "text.symbols.ipynb",
         "curly_re": "text.symbols.ipynb",
         "words_re": "text.symbols.ipynb",
         "normalize_numbers": "text.util.ipynb",
         "expand_abbreviations": "text.util.ipynb",
         "expand_numbers": "text.util.ipynb",
         "lowercase": "text.util.ipynb",
         "collapse_whitespace": "text.util.ipynb",
         "convert_to_ascii": "text.util.ipynb",
         "convert_to_arpabet": "text.util.ipynb",
         "basic_cleaners": "text.util.ipynb",
         "transliteration_cleaners": "text.util.ipynb",
         "english_cleaners": "text.util.ipynb",
         "english_cleaners_phonemizer": "text.util.ipynb",
         "batch_english_cleaners_phonemizer": "text.util.ipynb",
         "g2p": "text.util.ipynb",
         "batch_clean_text": "text.util.ipynb",
         "clean_text": "text.util.ipynb",
         "english_to_arpabet": "text.util.ipynb",
         "cleaned_text_to_sequence": "text.util.ipynb",
         "text_to_sequence": "text.util.ipynb",
         "sequence_to_text": "text.util.ipynb",
         "BATCH_CLEANERS": "text.util.ipynb",
         "CLEANERS": "text.util.ipynb",
         "text_to_sequence_for_editts": "text.util.ipynb",
         "random_utterance": "text.util.ipynb",
         "utterances": "text.util.ipynb",
         "TTSTrainer": "trainer.base.ipynb",
         "GradTTSTrainer": "trainer.gradtts.ipynb",
         "MellotronTrainer": "trainer.mellotron.ipynb",
         "Tacotron2Loss": "trainer.tacotron2.ipynb",
         "Tacotron2Trainer": "trainer.tacotron2.ipynb",
         "feature_loss": "vocoders.hifigan.ipynb",
         "discriminator_loss": "vocoders.hifigan.ipynb",
         "generator_loss": "vocoders.hifigan.ipynb",
         "kl_loss": "trainer.vits.ipynb",
         "VITSTrainer": "trainer.vits.ipynb",
         "mel_to_audio": "utils.audio.ipynb",
         "differenceFunction": "utils.audio.ipynb",
         "cumulativeMeanNormalizedDifferenceFunction": "utils.audio.ipynb",
         "getPitch": "utils.audio.ipynb",
         "compute_yin": "utils.audio.ipynb",
         "convert_to_wav": "utils.audio.ipynb",
         "match_target_amplitude": "utils.audio.ipynb",
         "modify_leading_silence": "utils.audio.ipynb",
         "normalize_audio_segment": "utils.audio.ipynb",
         "normalize_audio": "utils.audio.ipynb",
         "trim_audio": "utils.audio.ipynb",
         "MAX_WAV_INT16": "utils.audio.ipynb",
         "load_wav_to_torch": "utils.audio.ipynb",
         "overlay_mono": "utils.audio.ipynb",
         "overlay_stereo": "utils.audio.ipynb",
         "mono_to_stereo": "utils.audio.ipynb",
         "stereo_to_mono": "utils.audio.ipynb",
         "resample": "utils.audio.ipynb",
         "get_audio_max": "utils.audio.ipynb",
         "to_int16": "utils.audio.ipynb",
         "save_figure_to_numpy": "utils.plot.ipynb",
         "plot_tensor": "utils.plot.ipynb",
         "plot_spectrogram": "utils.plot.ipynb",
         "plot_attention": "utils.plot.ipynb",
         "plot_attention_phonemes": "utils.plot.ipynb",
         "plot_gate_outputs": "utils.plot.ipynb",
         "load_filepaths_and_text": "utils.utils.ipynb",
         "get_alignment_metrics": "utils.utils.ipynb",
         "window_sumsquare": "utils.utils.ipynb",
         "griffin_lim": "utils.utils.ipynb",
         "dynamic_range_compression": "utils.utils.ipynb",
         "dynamic_range_decompression": "utils.utils.ipynb",
         "to_gpu": "utils.utils.ipynb",
         "get_mask_from_lengths": "utils.utils.ipynb",
         "reduce_tensor": "utils.utils.ipynb",
         "subsequent_mask": "utils.utils.ipynb",
         "slice_segments": "utils.utils.ipynb",
         "rand_slice_segments": "utils.utils.ipynb",
         "init_weights": "vocoders.hifigan.ipynb",
         "get_padding": "vocoders.hifigan.ipynb",
         "fused_add_tanh_sigmoid_multiply": "utils.utils.ipynb",
         "clip_grad_value_": "utils.utils.ipynb",
         "intersperse": "utils.utils.ipynb",
         "intersperse_emphases": "utils.utils.ipynb",
         "parse_values": "vendor.tfcompat.hparam.ipynb",
         "HParams": "vendor.tfcompat.hparam.ipynb",
         "PARAM_RE": "vendor.tfcompat.hparam.ipynb",
         "HiFiGanGenerator": "vocoders.hifigan.ipynb",
         "MultiScaleDiscriminator": "vocoders.hifigan.ipynb",
         "AttrDict": "vocoders.hifigan.ipynb",
         "build_env": "vocoders.hifigan.ipynb",
         "apply_weight_norm": "vocoders.hifigan.ipynb"}

modules = ["data/cache.py",
           "data/parse.py",
           "data/statistics.py",
           "data_loader.py",
           "exec/dataset_statistics.py",
           "exec/gather_dataset.py",
           "exec/generate_filelist.py",
           "exec/normalize_audio.py",
           "exec/parse_data.py",
           "exec/preprocess_vits.py",
           "exec/split_train_val.py",
           "exec/train_gradtts.py",
           "exec/train_mellotron.py",
           "exec/train_tacotron2.py",
           "exec/train_vits.py",
           "models/attentions.py",
           "models/base.py",
           "models/common.py",
           "models/gradtts.py",
           "models/mellotron.py",
           "models/tacotron2.py",
           "models/transforms.py",
           "models/vits.py",
           "text/cmudict.py",
           "text/symbols.py",
           "text/util.py",
           "trainer/base.py",
           "trainer/gradtts.py",
           "trainer/mellotron.py",
           "trainer/tacotron2.py",
           "trainer/vits.py",
           "utils/argparse.py",
           "utils/audio.py",
           "utils/plot.py",
           "utils/utils.py",
           "vendor/tfcompat/hparam.py",
           "vocoders/hifigan.py"]

doc_url = "https://uberduck-ai.github.io/uberduck_ml_dev/"

git_url = "https://github.com/uberduck-ai/uberduck_ml_dev/tree/master/"

def custom_doc_links(name):
    return None
