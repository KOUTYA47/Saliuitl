# Makefile
# Claude Code CLI wrappers for multi-agent research workflow
# Usage examples:
#   make help
#   make lead TASK="Break my goal into tasks" OUTPUT="One TASKS.md entry"
#   make runner EXP=experiments/exp_20260201_inria_2p TASK="Verify run.sh reproducibility" INPUT="experiments/exp_20260201_inria_2p/run.sh"
#   make analyst EXP=experiments/exp_20260201_inria_2p TASK="Check RR/LPR numerators denominators" INPUT="experiments/exp_20260201_inria_2p/logs/stdout.txt experiments/exp_20260201_inria_2p/results/"
#
# Notes:
# - This assumes `claude` is on PATH and `claude code` works in this repo.
# - Agent behavior is invoked by ROLE instruction referencing .claude/agents/*.md

SHELL := /usr/bin/env bash
.ONESHELL:
.SHELLFLAGS := -euo pipefail -c

CLAUDE ?= claude
CLAUDE_CODE := $(CLAUDE) code

# Optional variables
TASK ?=
OUTPUT ?=
INPUT ?=
EXP ?=

# Internal helper: format INPUT list into YAML-ish bullets
define _format_inputs
$(if $(strip $(INPUT)),INPUT:$(newline)$(foreach f,$(INPUT),- $(f)$(newline)),)
endef

newline :=


.PHONY: help
help:
	@cat <<'EOF'
Claude Code CLI Makefile

Targets:
  make lead      TASK="..." [OUTPUT="..."] [INPUT="file1 file2 ..."]
  make runner    TASK="..." [OUTPUT="..."] [INPUT="..."] [EXP=experiments/exp_xxx]
  make analyst   TASK="..." [OUTPUT="..."] [INPUT="..."] [EXP=experiments/exp_xxx]
  make triage    PROBLEM="..."   (Lead decides which agent should handle)
  make sanity    (quick check that agents are recognized)
  make show-env  (runs scripts/env_check.sh if present)

Variables:
  TASK     Required for lead/runner/analyst
  OUTPUT   Optional: what you want back
  INPUT    Optional: space-separated file/dir paths to include
  EXP      Optional: experiment directory (used only for convenience)
  CLAUDE   Optional: override claude binary (default: claude)

Examples:
  make lead TASK="Create a TASKS.md entry for alpha sweep on nn_det_threshold" OUTPUT="One TASKS.md entry"
  make runner EXP=experiments/exp_20260201_inria_2p TASK="Review run.sh for reproducibility" INPUT="experiments/exp_20260201_inria_2p/run.sh"
  make analyst EXP=experiments/exp_20260201_inria_2p TASK="Summarize metrics into a CSV table" INPUT="experiments/exp_20260201_inria_2p/results/"

Tip:
  Keep TASK explicit, and always mention CONVENTIONS.md / TASKS.md in context to avoid drift.
EOF


.PHONY: lead
lead:
	@if [[ -z "$(strip $(TASK))" ]]; then echo "ERROR: TASK is required. e.g. make lead TASK=\"...\""; exit 1; fi
	@$(CLAUDE_CODE) <<'EOF'
CONTEXT:
- This repository contains .claude/agents/lead.md
- Follow CONVENTIONS.md strictly
- Use TASKS.md as the task definition format

ROLE:
- Act as the Lead agent defined in .claude/agents/lead.md

$(call _format_inputs)
TASK:
$(TASK)

OUTPUT:
$(if $(strip $(OUTPUT)),$(OUTPUT),Provide a clear, structured response.)
EOF


.PHONY: runner
runner:
	@if [[ -z "$(strip $(TASK))" ]]; then echo "ERROR: TASK is required. e.g. make runner TASK=\"...\""; exit 1; fi
	@$(CLAUDE_CODE) <<'EOF'
CONTEXT:
- This repository contains .claude/agents/experiment-runner.md
- Follow CONVENTIONS.md strictly
- Do NOT modify experimental parameters unless explicitly instructed
- Prefer pointing out violations over "fixing" them

ROLE:
- Act as the Experiment Runner agent defined in .claude/agents/experiment-runner.md

$(if $(strip $(EXP)),EXPERIMENT_DIR:$(newline)- $(EXP)$(newline),)
$(call _format_inputs)
TASK:
$(TASK)

OUTPUT:
$(if $(strip $(OUTPUT)),$(OUTPUT),Pass/Fail + issues list (if any).)
EOF


.PHONY: analyst
analyst:
	@if [[ -z "$(strip $(TASK))" ]]; then echo "ERROR: TASK is required. e.g. make analyst TASK=\"...\""; exit 1; fi
	@$(CLAUDE_CODE) <<'EOF'
CONTEXT:
- This repository contains .claude/agents/result-analyst.md
- Follow CONVENTIONS.md strictly
- Metrics must be explicit (state numerator and denominator)

ROLE:
- Act as the Result Analyst agent defined in .claude/agents/result-analyst.md

$(if $(strip $(EXP)),EXPERIMENT_DIR:$(newline)- $(EXP)$(newline),)
$(call _format_inputs)
TASK:
$(TASK)

OUTPUT:
$(if $(strip $(OUTPUT)),$(OUTPUT),Verification report + anomalies + next checks.)
EOF


.PHONY: triage
triage:
	@if [[ -z "$(strip $(PROBLEM))" ]]; then echo "ERROR: PROBLEM is required. e.g. make triage PROBLEM=\"...\""; exit 1; fi
	@$(CLAUDE_CODE) <<'EOF'
CONTEXT:
- Follow CONVENTIONS.md strictly

ROLE:
- Act as the Lead agent defined in .claude/agents/lead.md

TASK:
Given the following problem, decide which agent should handle it and propose the next command (make target).
Problem: $(PROBLEM)

OUTPUT:
- Selected agent (lead/runner/analyst or propose a new agent)
- Reason
- Next command (e.g., make runner ... / make analyst ...)
EOF


.PHONY: sanity
sanity:
	@$(CLAUDE_CODE) <<'EOF'
CONTEXT:
- This repository contains .claude/agents/*.md

TASK:
Confirm you can see these agent definitions:
- .claude/agents/lead.md
- .claude/agents/experiment-runner.md
- .claude/agents/result-analyst.md
Then summarize each agent's constraints in 3 bullets.

OUTPUT:
- One section per agent
EOF


.PHONY: show-env
show-env:
	@if [[ -x scripts/env_check.sh ]]; then scripts/env_check.sh; else echo "scripts/env_check.sh not found or not executable"; fi
