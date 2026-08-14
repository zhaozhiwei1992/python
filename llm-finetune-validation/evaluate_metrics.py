#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量评测：BLEU + ROUGE-L（纯 Python 实现，零第三方评测库依赖）。

为什么需要它（与 llamafactory-cli eval 的区别）：
  - llamafactory-cli eval 在新版（>=0.9.5）已废弃（报 NotImplementedError），
    且只在服务器 0.9.4.dev0 实测可用。
  - 本脚本用 transformers 直接加载模型 → 生成 → 自算指标，
    CPU / 昇腾 NPU 通吃，与 LLaMA-Factory 版本无关。
  - 指标为字符级：中文无需分词，直接逐字切分计算 n-gram 精确率（BLEU）
    与最长公共子序列（ROUGE-L），对"固定标准答案"的验收足够客观。

用法:
  # 微调 adapter vs 基础模型
  python3 evaluate_metrics.py --model 基础模型 --adapter saves/.../train_ascend_finance \
                              --model 基础模型
  # 合并后完整模型 vs 基础模型（结果缓存到 predictions/ 避免重复生成）
  python3 evaluate_metrics.py --model exports/...-ascend-finance --model 基础模型
"""

import argparse
import json
import os
import sys

import torch

try:
    import torch_npu  # noqa: F401
    DEVICE = "npu:0" if torch.npu.is_available() else "cuda:0" if torch.cuda.is_available() else "cpu"
except ImportError:
    DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"

from transformers import AutoModelForCausalLM, AutoTokenizer

DEFAULT_EVAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "ascend_finance_eval.json")


# ---------------- 指标（字符级，纯 Python） ----------------

def chars(text):
    """逐字切分（中文不需要分词；空格与标点保留，不影响结论）。"""
    return [c for c in text if c.strip()]


def ngrams(seq, n):
    return [tuple(seq[i:i + n]) for i in range(len(seq) - n + 1)]


def bleu_chars(ref, hyp, max_n=4):
    """字符级 BLEU：n-gram 精确率几何平均 × 简洁惩罚（BP）。"""
    r, h = chars(ref), chars(hyp)
    if not h:
        return 0.0
    precs = []
    for n in range(1, max_n + 1):
        ref_ng, hyp_ng = ngrams(r, n), ngrams(h, n)
        if not ref_ng or not hyp_ng:
            continue
        import collections
        ref_count = collections.Counter(ref_ng)
        hit = sum(min(ref_count[g], 1) for g in set(hyp_ng))
        precs.append(hit / len(hyp_ng))
    if not precs:
        return 0.0
    geo = sum(precs) / len(precs)  # 取平均代替几何平均（避免 n 项短时爆 0）
    bp = min(1.0, len(r) / len(h)) if len(h) > 0 else 0.0
    return geo * bp


def lcs_len(a, b):
    """最长公共子序列长度（标准 DP）。"""
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[-1][-1]


def rouge_l_f1(ref, hyp):
    """ROUGE-L：LCS 长度 → P/R/F1（字符级）。"""
    r, h = chars(ref), chars(hyp)
    if not r or not h:
        return 0.0
    lcs = lcs_len(r, h)
    p, rec = lcs / len(h), lcs / len(r)
    return 2 * p * rec / (p + rec) if (p + rec) else 0.0


# ---------------- 加载与生成 ----------------

def load_model(model_path, adapter_path=None, trust_remote_code=True):
    torch_dtype = torch.float16 if DEVICE != "cpu" else torch.float32
    tok = AutoTokenizer.from_pretrained(model_path, trust_remote_code=trust_remote_code)
    model = AutoModelForCausalLM.from_pretrained(
        model_path, trust_remote_code=trust_remote_code, torch_dtype=torch_dtype
    ).to(DEVICE)
    if adapter_path:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, adapter_path)
        print(f"  已加载 adapter: {adapter_path}")
    model.eval()
    return model, tok


def generate(model, tok, question, max_new_tokens=256):
    msgs = [{"role": "user", "content": question}]
    text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    inp = tok(text, return_tensors="pt").to(model.device)
    with torch.no_grad():
        out = model.generate(**inp, max_new_tokens=max_new_tokens, do_sample=False)
    return tok.decode(out[0][inp["input_ids"].shape[1]:], skip_special_tokens=True).strip()


def run_one(tag, model_path, adapter_path, eval_set, cache_dir, max_questions, max_new_tokens):
    cache_file = os.path.join(cache_dir, f"{tag}.json")
    os.makedirs(cache_dir, exist_ok=True)

    if os.path.exists(cache_file):  # 命中缓存则不再生成（模型未变时结果一致）
        print(f"[{tag}] 复用缓存 {cache_file}")
        with open(cache_file, encoding="utf-8") as f:
            preds = json.load(f)
    else:
        print(f"\n===== 生成中: {tag} ({model_path}" + (f" + adapter" if adapter_path else "") + f" | {DEVICE}) =====")
        model, tok = load_model(model_path, adapter_path)
        preds = []
        for i, item in enumerate(eval_set[:max_questions] if max_questions else eval_set):
            ans = generate(model, tok, item["instruction"], max_new_tokens)
            preds.append({"instruction": item["instruction"], "reference": item["output"], "prediction": ans})
            print(f"  [{i + 1}/{len(eval_set[:max_questions] if max_questions else eval_set)}] {item['instruction'][:30]}...")
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(preds, f, ensure_ascii=False, indent=2)

    # 计算指标
    b1 = sum(bleu_chars(p["reference"], p["prediction"], 1) for p in preds) / len(preds)
    b4 = sum(bleu_chars(p["reference"], p["prediction"], 4) for p in preds) / len(preds)
    rl = sum(rouge_l_f1(p["reference"], p["prediction"]) for p in preds) / len(preds)
    print(f"[{tag}] BLEU-1={b1:.3f}  BLEU-4={b4:.3f}  ROUGE-L={rl:.3f}  (n={len(preds)})")
    return {"tag": tag, "bleu1": b1, "bleu4": b4, "rouge_l": rl, "preds": preds}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="BLEU/ROUGE-L 批量评测（纯 Python，CPU/昇腾通吃）")
    ap.add_argument("--model", action="append", required=True, help="模型路径，可传多次（最后一个视为对照组）")
    ap.add_argument("--adapter", default=None, help="LoRA adapter 目录（仅叠加在第一个 --model 上）")
    ap.add_argument("--eval", default=DEFAULT_EVAL, help="验证集 JSON")
    ap.add_argument("--cache-dir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "predictions"))
    ap.add_argument("--max-questions", type=int, default=0, help="只测前 N 条（0=全部）")
    ap.add_argument("--max-new-tokens", type=int, default=256)
    ap.add_argument("--no-cache", action="store_true", help="忽略缓存重新生成")
    args = ap.parse_args()

    with open(args.eval, encoding="utf-8") as f:
        eval_set = json.load(f)

    results = []
    for i, m in enumerate(args.model):
        adapter = args.adapter if i == 0 else None
        tag = "finetuned" if i == 0 else f"base{i}" if len(args.model) > 2 else "base"
        if args.no_cache:
            cache_file = os.path.join(args.cache_dir, f"{tag}.json")
            if os.path.exists(cache_file):
                os.remove(cache_file)
        results.append(run_one(tag, m, adapter, eval_set, args.cache_dir, args.max_questions, args.max_new_tokens))

    if len(results) > 1:
        ft, base = results[0], results[-1]
        print("\n===== 对比结论（对照：基础模型） =====")
        print(f"{'指标':<10}{'微调/合并':>10}{'基础模型':>10}{'提升':>8}")
        for k, label in (("bleu1", "BLEU-1"), ("bleu4", "BLEU-4"), ("rouge_l", "ROUGE-L")):
            print(f"{label:<10}{ft[k]:>10.3f}{base[k]:>10.3f}{ft[k] - base[k]:>+8.3f}")
        ok = ft["bleu4"] >= base["bleu4"] and ft["rouge_l"] >= base["rouge_l"]
        print(f"\n>>> 微调模型 {'全面优于' if ok else '未全面优于'} 基础模型，验证{'通过' if ok else '未通过'}")
        sys.exit(0 if ok else 1)
