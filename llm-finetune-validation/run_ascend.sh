#!/bin/bash
# =============================================================
# 昇腾 NPU 全流程一键脚本（101.26 服务器）
# 数据准备 → 训练（LoRA）→ 批量评测（CLI eval，基础 vs 微调）→ 导出合并
#           → 关键词命中验证（evaluate_metrics.py 可选替代 CLI eval）
#
# 用法:
#   bash run_ascend.sh            # 全流程
#   bash run_ascend.sh train      # 单步: env|data|train|eval|export|verify|chat
#
# 前置: 按笔记完成 conda activate ascend_llm_env、模型下载到 HF 标准目录
# =============================================================
set -uo pipefail

# ---------- 可调配置（按服务器实际修改） ----------
CONDA_ENV=${CONDA_ENV:-ascend_llm_env}
LLM_FACTORY_HOME=${LLM_FACTORY_HOME:-/root/LLaMA-Factory}
MODEL_PATH=${MODEL_PATH:-/data/models/qwen2.5-1.5b-instruct}
DIR="$(cd "$(dirname "$0")" && pwd)"                 # llm-finetune-validation/
RUNS_DIR=${RUNS_DIR:-$LLM_FACTORY_HOME/saves/Qwen2.5-1.5B-Instruct/lora/train_ascend_finance}
ADAPTER="$RUNS_DIR"                                   # 训练输出即 adapter
MERGED_DIR=${MERGED_DIR:-$LLM_FACTORY_HOME/exports/Qwen2.5-1.5B-Instruct-ascend-finance}
YAML="$DIR/yaml"
EVAL_JSON="$DIR/data/ascend_finance_eval.json"
export ASCEND_RT_VISIBLE_DEVICES=${ASCEND_RT_VISIBLE_DEVICES:-0}   # 单卡；多卡不设
export USE_BF16=0 USE_FP16=1 NPU_FORCE_FP32_GRAD=1                 # 昇腾关键环境变量

log() { echo; echo "========== [$*] =========="; }
die() { echo "!! 失败: $*" >&2; exit 1; }

check_env() {
    log "环境检查"
    [ -f /usr/local/Ascend/ascend-toolkit/set_env.sh ] && source /usr/local/Ascend/ascend-toolkit/set_env.sh || die "未找到 CANN set_env.sh"
    conda activate "$CONDA_ENV" 2>/dev/null || source activate "$CONDA_ENV" 2>/dev/null || die "conda 环境 $CONDA_ENV 不可用"
    python -c "import torch, torch_npu; print('torch:', torch.__version__, '| NPU:', torch.npu.is_available(), '| 卡数:', torch.npu.device_count())" || die "torch_npu 不可用"
    [ -d "$MODEL_PATH" ] || die "基础模型目录不存在: $MODEL_PATH"
    echo "OK"
}

register_dataset() {
    log "数据集注册（幂等）"
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
    log "训练（LoRA SFT）"
    cd "$LLM_FACTORY_HOME" || die "cd $LLM_FACTORY_HOME 失败"
    llamafactory-cli train "$YAML/train_ascend_1.5b_lora_sft.yaml" || die "训练失败"
    ls "$ADAPTER"/adapter_model.safetensors >/dev/null 2>&1 || die "未找到 adapter_model.safetensors: $ADAPTER"
    echo "  OK: $ADAPTER"
}

eval_step() {
    log "批量评测（do_predict 路线，离线可用，基础 vs 微调）"
    cd "$LLM_FACTORY_HOME" || die "cd 失败"
    # 注意: 默认走离线 do_predict（方案 A，0.9.x 通用、无需外网）。
    #       方案 B 在线基准评测（需外网 + 仅 ≤0.9.4）可选跑:
    #       llamafactory-cli eval $YAML/eval_ascend_bench.yaml
    llamafactory-cli train "$YAML/predict_ascend_1.5b_lora.yaml" || die "微调模型评测失败"
    llamafactory-cli train "$YAML/predict_ascend_base.yaml" || die "基础模型评测失败"
    echo "  predictions: saves/Qwen2.5-1.5B-Instruct/lora/eval_{finetuned,base}/"
}

export_step() {
    log "导出（合并 LoRA → 完整 HF 模型）"
    cd "$LLM_FACTORY_HOME" || die "cd 失败"
    llamafactory-cli export "$YAML/export_ascend_1.5b_merged.yaml" || die "导出失败"
    ls "$MERGED_DIR"/model-*.safetensors >/dev/null 2>&1 || die "导出目录缺少权重: $MERGED_DIR"
    echo "  OK: $MERGED_DIR"
}

verify() {
    log "关键词命中验证（合并模型 vs 基础模型，版本无关）"
    python "$DIR/verify_keywords.py" \
        --model "$MERGED_DIR" --model "$MODEL_PATH" --eval "$EVAL_JSON" \
        || die "验证未通过（微调模型命中率低于基础模型）"
    log "BLEU/ROUGE 硬对比（evaluate_metrics.py，版本无关，结果缓存在 predictions/）"
    python "$DIR/evaluate_metrics.py" \
        --model "$MERGED_DIR" --model "$MODEL_PATH" --eval "$EVAL_JSON" \
        || die "评测失败"
}

chat() {
    log "人工对比（开两个终端分别跑）"
    echo "  基础模型: python3 $DIR/chat_compare.py --model $MODEL_PATH"
    echo "  微调模型: python3 $DIR/chat_compare.py --model $MODEL_PATH --adapter $ADAPTER"
    echo "  合并模型: python3 $DIR/chat_compare.py --model $MERGED_DIR"
}

case "${1:-all}" in
    env)    check_env ;;
    data)   register_dataset ;;
    train)  check_env && register_dataset && train ;;
    eval)   check_env && eval_step ;;
    export) check_env && export_step ;;
    verify) check_env && verify ;;
    chat)   chat ;;
    all)    check_env && register_dataset && train && eval_step && export_step && verify && chat ;;
    *) die "用法: $0 [all|env|data|train|eval|export|verify|chat]" ;;
esac

echo
echo "===== 昇腾全流程完成。验收要点 ====="
echo "1. trainer_state.json loss 持续下降"
echo "2. CLI eval 报告：eval_finetuned 的 BLEU/ROUGE 显著高于 eval_base"
echo "3. verify_keywords.py：合并模型命中率 ≥ 基础模型"
echo "4. evaluate_metrics.py：BLEU/ROUGE 硬对比表，微调全面优于基础"
echo "5. 导出目录含完整 model-*.safetensors + tokenizer"
