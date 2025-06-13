# OCRS pre-trained model 
OCRS
![alt text](intro.png)

Link: https://github.com/robertknight/ocrs
## Datasets

The models are trained exclusively on datasets which are a) open and b) have non-restrictive licenses. This currently includes:
- [HierText](https://github.com/google-research-datasets/hiertext) (CC-BY-SA 4.0)

## Pre-trained models

Pre-trained models are available from [HuggingFace](https://huggingface.co/robertknight/ocrs) as PyTorch checkpoints,
[ONNX](https://onnx.ai) and [RTen](https://github.com/robertknight/rten) models.

### install :
git clone https://github.com/robertknight/ocrs.git
cd ocrs
cargo run -p ocrs-cli -r -- image.png