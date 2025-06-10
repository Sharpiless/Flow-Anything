# Flow-Anything: Learning Real-World Optical Flow Estimation from Large-Scale Single-view Images

[Paper Link](https://arxiv.org/pdf/2506.07740)

https://github.com/user-attachments/assets/d0e9a972-8864-4e26-9276-85124217afc9


---

## 📢 Project Status

We are actively organizing and cleaning up the full codebase (training, inference, evaluation).  
The repository will be **continuously updated** in the coming weeks — please stay tuned for:

- 🛠️ Full training scripts
- 📦 Data preparation tools
- 📈 Evaluation pipelines
- 🔖 Additional pre-trained models for different datasets

---

## 🚀 Pre-trained Checkpoints

You can find the released pre-trained checkpoints here:  
👉 [Flow-Anything Checkpoints](https://github.com/Sharpiless/Flow-Anything/releases/tag/checkpoints)

---

## Quick Start

### installation

```
conda create --name SEA-RAFT python=3.10.13
conda activate SEA-RAFT
pip install -r requirements.txt
```

### inference

```
python infer.py \
    --input [path to images] \
    --out [path to save] \
    --cfg config/eval/sintel-M.json \
    --model [path to ckpt]
```

## ✅ TODO

- [ ] **Data generation and pre-training code**  
  (including dataset preprocessing, augmentation, and full training pipeline)

- [ ] **Inference and evaluation code on Point Tracking tasks**  
  (standardized pipelines for Point Tracking benchmarks and visualization)

- [ ] **Clean inference-optimized code**  
  (lightweight, modular implementation specifically designed for fast deployment & real-time inference)

---

Thank you for your interest and support! ⭐️  
Feel free to open an issue if you have any questions or suggestions.

---
