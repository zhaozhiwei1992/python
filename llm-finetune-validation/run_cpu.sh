#!/bin/bash
# =============================================================
# 通用全流程一键脚本（本机 CPU / 自有 GPU 环境）
# 数据准备 → 训练（LoRA）→ BLEU/ROUGE 评测 → 关键词命中验证 → 提示人工对比
#
# 用法:
#   conda activate llm_finetune_cpu   # 或任意装了 transformers+peft 的环境
#   bash run_cpu.sh                   # 全流程
#   bash run_cpu.sh train             # 只训练
#   bash run_cpu.sh eval              # 只评测+验证
#
# 特点:
#   - 训练/导出用 llamafactory-cli（标准 YAML，key=value 覆盖路径）
#   - 评测用 evaluate_metrics.py + verify_keywords.py（纯 Python，
#     因为新版 llamafactory-cli 的 eval 子命令已废弃）
#   - CPU 上 0.5B 全量 1 epoch ≈ 75 分钟（实测单步 ≈12 分钟）；有 GPU 就去掉
#     CUDA_VISIBLE_DEVICES= 强制行，训练快 1-2 个数量级
# =============================================================
set -uo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"                 # 本脚本目录（llm-finetune-validation/）
LLM_FACTORY_HOME=${LLM_FACTORY_HOME:-/home/zhaozhiwei/workspace/LLaMA-Factory}
MODEL_PATH=${MODEL_PATH:-/home/zhaozhiwei/workspace/models/Qwen2.5-0.5B-Instruct}  # CPU/GPU 均可；昇腾用 run_ascend.sh
RUNS_DIR="$DIR/runs/cpu"
TRAIN_YAML="$DIR/yaml/train_ascend_1.5b_lora_sft.yaml"
EVAL_JSON="$DIR/data/ascend_finance_eval.json"
ADAPTER="$RUNS_DIR/adapter"                            # 训练输出 = 评测/验证时加载的 adapter
export CUDA_VISIBLE_DEVICES=""                         # 强制 CPU（若在 GPU 环境去掉这行）

log() { echo; echo "========== [$*] =========="; }
die() { echo "!! 失败: $*" >&2; exit 1; }

check_env() {
    log "环境检查"
    command -v llamafactory-cli >/dev/null || die "未找到 llamafactory-cli（先 conda activate llm_finetune_cpu 或 pip install -e LLaMA-Factory）"
    python -c "import torch, transformers, peft; print('torch', torch.__version__, '| transformers', transformers.__version__)" || die "依赖缺失"
    [ -d "$MODEL_PATH" ] || die "模型目录不存在: $MODEL_PATH"
    echo "OK"
}

register_dataset() {
    log "数据集注册（幂等，追加到 $LLM_FACTORY_HOME/data/dataset_info.json）"
    python - "$DIR/data/dataset_info_add.json" "$LLM_FACTORY_HOME/data/dataset_info.json" <<'PY'
import json, sys
add_file, info_file = sys.argv[1], sys.argv[2]
add = json.load(open(add_file, encoding="utf-8"))
info = json.load(open(info_file, encoding="utf-8"))
changed = False
for k, v in add.items():
    if k not in info:
        info[k] = v; changed = True; print(f"  新增注册: {k}")
if changed:
    json.dump(info, open(info_file, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
else:
    print("  已注册过，跳过")
PY
    cp "$DIR/data/ascend_finance_train.json" "$DIR/data/ascend_finance_eval.json" "$LLM_FACTORY_HOME/data/" || die "拷贝数据集失败"
    echo "  OK"
}

train() {
    log "训练（LoRA SFT，输出 $ADAPTER；CPU 上 0.5B 全量 1 epoch ≈ 75 分钟，GPU 环境快很多）"
    mkdir -p "$RUNS_DIR"
    cd "$LLM_FACTORY_HOME" || die "cd $LLM_FACTORY_HOME 失败"
    llamafactory-cli train "$TRAIN_YAML" \
        model_name_or_path="$MODEL_PATH" \
        output_dir="$ADAPTER" \
        num_train_epochs=1.0 || die "训练失败"
    ls "$ADAPTER"/adapter_model.safetensors >/dev/null 2>&1 || die "未找到 adapter_model.safetensors"
    echo "  OK: $ADAPTER"
}

eval_step() {
    [ -f "$ADAPTER/adapter_model.safetensors" ] || die "未找到 adapter: $ADAPTER（先 bash run_cpu.sh train）"
    log "批量评测（BLEU/ROUGE，微调 adapter vs 基础模型）"
    cd "$DIR" || die "cd 失败"
    python3 evaluate_metrics.py \
        --model "$MODEL_PATH" --adapter "$ADAPTER" \
        --model "$MODEL_PATH" \
        --eval "$EVAL_JSON" || die "评测失败"
    log "关键词命中验证（微调 adapter vs 基础模型）"
    python3 verify_keywords.py \
        --model "$MODEL_PATH" --adapter "$ADAPTER" \
        --model "$MODEL_PATH" \
        --eval "$EVAL_JSON" || die "验证未通过（微调命中率低于基础模型）"
}

chat() {
    [ -f "$ADAPTER/adapter_model.safetensors" ] || die "未找到 adapter: $ADAPTER"
    log "人工对比（开两个终端分别跑以下命令，问同样的问题）"
    echo "  基础模型: python3 $DIR/chat_compare.py --model $MODEL_PATH"
    echo "  微调模型: python3 $DIR/chat_compare.py --model $MODEL_PATH --adapter $ADAPTER"
}

case "${1:-all}" in
    env)    check_env ;;
    data)   register_dataset ;;
    train)  check_env && register_dataset && train ;;
    eval)   eval_step ;;
    chat)   chat ;;
    all)    check_env && register_dataset && train && eval_step && chat ;;
    *) die "用法: $0 [all|env|data|train|eval|chat]" ;;
esac

echo
echo "===== 全流程完成。验收要点 ====="
echo "1. $ADAPTER/training_loss.png loss 曲线持续下降"
echo "2. 评测对比表：BLEU/ROUGE 微调 >> 基础（基础应≈0）"
echo "3. 关键词命中率：微调 ≥ 基础（基础对照组应≈0%）"
echo "4. 人工对比：微调能答出 国库集中支付/85_一体化系统/你是谁，基础答不出"
