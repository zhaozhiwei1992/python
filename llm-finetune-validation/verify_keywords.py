#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证集自动核查：加载模型（基础模型 / 微调 adapter / 合并后完整模型），
对验证集逐条生成回答，检查输出是否命中标准答案中的关键术语，输出命中率表格。

设计动机（对比 llamafactory-cli）：
  - 与 LLaMA-Factory 版本无关（新版已废弃 llamafactory-cli eval，本脚本不受影响）
  - 直接出"人类可读"的逐题 PASS/FAIL 表格，而非一堆 BLEU/ROUGE 数字
  - 是"基础模型答错 → 微调后答对"的硬性证明（对照组命中率≈0%）

环境自适应：npU > CUDA > CPU；CPU 自动用 float32，NPU/CUDA 用 float16。

用法:
  # 1) 微调 adapter vs 基础模型（训练后立刻验证，无需导出）
  python3 verify_keywords.py --model 基础模型 --adapter saves/.../train_ascend_finance

  # 2) 合并后的完整模型 vs 基础模型
  python3 verify_keywords.py --model exports/Qwen2.5-1.5B-Instruct-ascend-finance

  # 3) 两个完整模型直接对比（最后一个视为对照组）
  python3 verify_keywords.py --model 微调模型 --model 基础模型

  # 4) 快速测试：只跑前 5 条
  python3 verify_keywords.py --model 基础模型 --max-questions 5
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

# 每条验证题的关键术语（与 data/ascend_finance_eval.json 的 instruction 一一对应）
KEYWORDS = {
    "国库集中支付的含义是什么？": ["国库单一账户体系", "财政直接支付", "财政授权支付"],
    "为什么要推行国库集中支付？": ["国库单一账户体系", "直接支付", "透明度"],
    "财政资金如何直接付给供应商？": ["财政部门", "代理银行", "支付指令"],
    "工资和政府采购支出一般用什么方式支付？": ["财政直接支付", "财政部门"],
    "预算单位日常零星支出用什么方式支付？": ["财政授权支付", "预算单位", "零余额账户"],
    "财政授权支付是在什么额度内办理的？": ["用款额度", "预算单位", "授权"],
    "零余额账户每天是怎么清零的？": ["代理银行", "垫付", "清算"],
    "代理银行垫付的资金如何收回？": ["清算", "国库单一账户"],
    "国库单一账户体系包括哪些账户？": ["国库单一账户", "零余额账户", "特设专户"],
    "为什么所有财政资金都要纳入国库单一账户体系？": ["统一", "集中管理", "国库单一账户"],
    "基本支出都包含哪些费用？": ["人员经费", "公用经费"],
    "人员经费具体包括什么？": ["工资", "津贴补贴", "社会保障缴费"],
    "信息化建设项目支出属于哪类支出？": ["项目支出", "基本支出之外"],
    "项目支出有什么管理要求？": ["项目预算", "项目库管理", "专款专用"],
    "预算单位在国库集中支付中扮演什么角色？": ["部门预算", "用款额度", "资金支付"],
    "预算单位的主要职责是什么？": ["部门预算", "财务核算", "资金支付"],
    "预算单位如何获得用款额度？": ["用款计划", "财政部门", "批复"],
    "用款计划多久申报一次？": ["按季度", "财政部门"],
    "差旅费可以用什么方式结算？": ["公务卡", "报销"],
    "公务卡欠款由谁归还？": ["财政资金", "报销"],
    "谁签发财政直接支付的支付指令？": ["财政部门", "支付指令"],
    "支付指令需要包含哪些要素？": ["收款人", "金额", "用途"],
    "代理银行如何与国库结清当日垫付资金？": ["清算", "国库单一账户", "日终"],
    "为什么要进行日终清算？": ["余额为零", "代理银行", "垫付"],
    "85_一体化系统包括哪些功能模块？": ["预算编制", "国库集中支付", "政府采购"],
    "85_一体化系统在财政业务中起什么作用？": ["一体化", "全生命周期", "财政预算管理"],
    "85_一体化系统如何办理财政直接支付？": ["财政部门", "支付指令", "银企直连"],
    "预算单位在85_一体化系统中能否自行支付？": ["财政授权支付", "用款额度"],
    "85_一体化系统的支付指令是怎么发到银行的？": ["银企直连", "支付指令", "代理银行"],
    "85_一体化系统如何保证支付全程可追溯？": ["留痕", "支付凭证", "记账"],
    "银企直连比人工网银操作好在哪？": ["自动", "效率", "对账"],
    "支付结果是如何自动回到85_一体化系统的？": ["银企直连", "自动回传"],
    "85_一体化系统生成支付指令前校验什么？": ["预算指标", "用款额度", "收款人"],
    "支付指令的电子签名和加密有什么用？": ["安全", "银企直连"],
    "你是谁？介绍一下你自己。": ["财政一体化智能助手", "财政研发中心"],
    "你被谁开发出来的？": ["财政研发中心"],
    "财政直接支付和财政授权支付有什么区别？": ["财政部门", "预算单位", "支付指令"],
    "85_一体化系统的支付方式是怎样的？": ["财政直接支付", "财政授权支付", "银企直连"],
}

DEFAULT_EVAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "ascend_finance_eval.json")


def load_model(model_path, adapter_path=None, trust_remote_code=True):
    """加载模型（可选套 LoRA adapter）。返回 (model, tokenizer)。"""
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


def check(model_path, adapter_path, eval_path, max_questions):
    print(f"\n===== 模型: {model_path}" + (f" + adapter" if adapter_path else "") + f" | device={DEVICE} =====\n")
    model, tok = load_model(model_path, adapter_path)

    with open(eval_path, encoding="utf-8") as f:
        eval_set = json.load(f)

    total, pass_cnt, hit_sum, hit_all = 0, 0, 0, 0
    for item in eval_set[:max_questions] if max_questions else eval_set:
        q = item["instruction"]
        kws = KEYWORDS.get(q)
        if not kws:
            continue
        ans = generate(model, tok, q)
        hits = [kw for kw in kws if kw in ans]
        passed = len(hits) >= max(1, len(kws) * 2 // 3)
        total += 1
        pass_cnt += int(passed)
        hit_sum += len(hits)
        hit_all += len(kws)
        print(f"[{'PASS' if passed else 'FAIL'}] Q: {q}")
        print(f"       命中 {len(hits)}/{len(kws)}: {hits}")
        print(f"       A: {ans[:160]}")

    rate = pass_cnt / max(total, 1) * 100
    print(f"\n>>> 通过 {pass_cnt}/{total}（{rate:.0f}%），术语命中 {hit_sum}/{hit_all}")
    return rate


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="验证集关键术语命中率自动核查")
    ap.add_argument("--model", action="append", required=True,
                    help="模型路径（可传多次做对比，最后一个视为对照组）")
    ap.add_argument("--adapter", default=None, help="LoRA adapter 目录（加载在 --model 之上）")
    ap.add_argument("--eval", default=DEFAULT_EVAL, help="验证集 JSON（默认 data/ascend_finance_eval.json）")
    ap.add_argument("--max-questions", type=int, default=0, help="只测前 N 条（0=全部，快速调试用）")
    args = ap.parse_args()

    models = args.model
    rates = [check(m, args.adapter if i == 0 else None, args.eval, args.max_questions) for i, m in enumerate(models)]

    if len(rates) > 1:
        base, ft = rates[-1], rates[0]
        print("\n===== 对比结论 =====")
        for m, r in zip(models, rates):
            print(f"  {r:5.1f}%  {m}")
        print(f"\n>>> 微调模型命中率 {'≥' if ft >= base else '<'} 基础模型，验证{'通过' if ft >= base else '未通过'}")
        sys.exit(0 if ft >= base else 1)
