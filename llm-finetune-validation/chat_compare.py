#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交互式人工对比：加载模型（基础 / 微调 adapter / 合并模型），循环提问，
观察回答。等价于 llamafactory-cli chat，但独立于 LLaMA-Factory（版本无关）。

用法:
  python3 chat_compare.py --model 基础模型                              # 基础模型
  python3 chat_compare.py --model 基础模型 --adapter saves/.../adapter  # 微调模型
  python3 chat_compare.py --model exports/...-ascend-finance            # 合并模型

交互:
  - 输入问题回车出答案；exit / quit 退出。
  - 想对比两个模型：开两个终端各跑一条命令，问同样的问题。
"""

import argparse
import os

import torch

try:
    import torch_npu  # noqa: F401
    DEVICE = "npu:0" if torch.npu.is_available() else "cuda:0" if torch.cuda.is_available() else "cpu"
except ImportError:
    DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"

from transformers import AutoModelForCausalLM, AutoTokenizer


def main():
    ap = argparse.ArgumentParser(description="交互式问答（基础/微调/合并模型通用）")
    ap.add_argument("--model", required=True, help="基础模型或合并后完整模型路径")
    ap.add_argument("--adapter", default=None, help="LoRA adapter 目录（微调模型用）")
    ap.add_argument("--max-new-tokens", type=int, default=256)
    ap.add_argument("--system", default="", help="可选的 system 提示（如设定角色）")
    args = ap.parse_args()

    torch_dtype = torch.float16 if DEVICE != "cpu" else torch.float32
    print(f"加载模型: {args.model}" + (f" + adapter: {args.adapter}" if args.adapter else "") + f" | device={DEVICE}")
    tok = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.model, trust_remote_code=True, torch_dtype=torch_dtype
    ).to(DEVICE)
    if args.adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, args.adapter)
    model.eval()

    print("\n=== 交互开始（输入 exit 退出）===")
    print("试试: 什么是国库集中支付？ / 85_一体化系统支持哪些支付方式？ / 你是谁？\n")
    while True:
        try:
            q = input("Q> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not q or q.lower() in ("exit", "quit"):
            break
        msgs = [{"role": "system", "content": args.system}] if args.system else []
        msgs.append({"role": "user", "content": q})
        text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        inp = tok(text, return_tensors="pt").to(model.device)
        with torch.no_grad():
            out = model.generate(**inp, max_new_tokens=args.max_new_tokens, do_sample=False)
        ans = tok.decode(out[0][inp["input_ids"].shape[1]:], skip_special_tokens=True).strip()
        print(f"A> {ans}\n")


if __name__ == "__main__":
    main()
