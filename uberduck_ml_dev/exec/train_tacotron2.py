# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/exec.train_tacotron2.ipynb (unless otherwise specified).

__all__ = ['run']

# Cell
from ..trainer.tacotron2 import Tacotron2Trainer
from ..vendor.tfcompat.hparam import HParams
from ..models.tacotron2 import DEFAULTS as TACOTRON2_DEFAULTS
from ..utils.exec import parse_args
import sys
import json

# Cell
def run(rank, device_count, hparams):
    trainer = Tacotron2Trainer(hparams, rank=rank, world_size=device_count)
    try:
        trainer.train()
    except Exception as e:
        print(f"Exception raised while training: {e}")
        # TODO: save state.
        raise e

# Cell
try:
    from nbdev.imports import IN_NOTEBOOK
except:
    IN_NOTEBOOK = False
if __name__ == "__main__" and not IN_NOTEBOOK:
    args = parse_args(sys.argv[1:])
    config = TACOTRON2_DEFAULTS.values()
    if args.config:
        with open(args.config) as f:
            config.update(json.load(f))
    hparams = HParams(**config)
    if hparams.distributed_run:
        device_count = torch.cuda.device_count()
        mp.spawn(run, (device_count, hparams), device_count)
    else:
        run(None, None, hparams)