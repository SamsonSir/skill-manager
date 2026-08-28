---
name: meta-superpowers-workflow
kind: meta
description: Use when a development, debugging, planning, review, or skill-authoring task should follow the Superpowers workflow instead of ad hoc skill selection.
triggers:
  - superpowers workflow
  - use superpowers meta skill
  - run superpowers
  - structured superpowers flow
  - meta superpowers
meta_priority: 80
always: false
final_text_mode: auto
metadata:
  opensquilla:
    risk: high
    capabilities:
      - filesystem-write
      - network-read
      - shell
      - process-control
composition:
  steps:
    - id: classify
      kind: llm_classify
      output_choices:
        - START_OR_GENERAL
        - FEATURE_OR_CREATIVE_BUILD
        - BUG_OR_TEST_FAILURE
        - WRITTEN_PLAN_EXECUTION
        - PARALLEL_WORK
        - CODE_REVIEW_RESPONSE
        - SKILL_AUTHORING
        - VERIFY_OR_FINISH
      with:
        text: "{{ inputs.user_message | xml_escape | truncate(700) }}"

    - id: skill_policy
      kind: agent
      skill: using-superpowers
      depends_on: [classify]
      with:
        request: |
          Apply the Superpowers skill-selection policy to this request before any downstream work.
          Classification: {{ outputs.classify | xml_escape | truncate(80) }}
          Request: {{ inputs.user_message | xml_escape | truncate(1200) }}

    - id: intake
      kind: llm_chat
      depends_on: [skill_policy]
      with:
        system: "Extract task goal, task type, known inputs, missing context, success criteria, and side-effect risks. Keep it compact."
        task: |
          Classification: {{ outputs.classify | xml_escape | truncate(80) }}
          Request: {{ inputs.user_message | xml_escape | truncate(1400) }}

    - id: initial_method
      kind: agent
      skill: brainstorming
      depends_on: [intake]
      route:
        - when: "outputs.classify == 'BUG_OR_TEST_FAILURE'"
          to: systematic-debugging
        - when: "outputs.classify == 'CODE_REVIEW_RESPONSE'"
          to: receiving-code-review
        - when: "outputs.classify == 'SKILL_AUTHORING'"
          to: writing-skills
        - when: "outputs.classify == 'VERIFY_OR_FINISH'"
          to: verification-before-completion
        - when: "outputs.classify == 'START_OR_GENERAL'"
          to: using-superpowers
      with:
        request: |
          Run the first Superpowers method appropriate for the classified request.
          Classification: {{ outputs.classify | xml_escape | truncate(80) }}
          Intake: {{ outputs.intake | xml_escape | truncate(1600) }}

    - id: workspace_gate
      kind: agent
      skill: using-git-worktrees
      depends_on: [initial_method]
      with:
        request: |
          Decide whether this work needs an isolated git worktree before implementation.
          Create one only when appropriate and safe. If the classification does not need a worktree, return "No worktree needed" with the reason.
          Classification: {{ outputs.classify | xml_escape | truncate(80) }}
          Intake: {{ outputs.intake | xml_escape | truncate(1200) }}
          Initial method output: {{ outputs.initial_method | xml_escape | truncate(1600) }}

    - id: plan_or_test
      kind: agent
      skill: writing-plans
      depends_on: [workspace_gate]
      route:
        - when: "outputs.classify == 'BUG_OR_TEST_FAILURE'"
          to: test-driven-development
        - when: "outputs.classify == 'WRITTEN_PLAN_EXECUTION'"
          to: executing-plans
        - when: "outputs.classify == 'PARALLEL_WORK'"
          to: dispatching-parallel-agents
        - when: "outputs.classify == 'SKILL_AUTHORING'"
          to: test-driven-development
        - when: "outputs.classify == 'VERIFY_OR_FINISH'"
          to: requesting-code-review
        - when: "outputs.classify == 'START_OR_GENERAL'"
          to: using-superpowers
      with:
        request: |
          Choose the next Superpowers planning or implementation discipline.
          For feature or creative builds, produce a plan before touching code.
          For bugs, require TDD after root-cause investigation.
          Classification: {{ outputs.classify | xml_escape | truncate(80) }}
          Intake: {{ outputs.intake | xml_escape | truncate(1200) }}
          Initial method output: {{ outputs.initial_method | xml_escape | truncate(2200) }}

    - id: execution_strategy
      kind: agent
      skill: subagent-driven-development
      depends_on: [plan_or_test]
      route:
        - when: "outputs.classify == 'WRITTEN_PLAN_EXECUTION'"
          to: executing-plans
        - when: "outputs.classify == 'PARALLEL_WORK'"
          to: subagent-driven-development
        - when: "outputs.classify == 'FEATURE_OR_CREATIVE_BUILD'"
          to: test-driven-development
        - when: "outputs.classify == 'BUG_OR_TEST_FAILURE'"
          to: systematic-debugging
        - when: "outputs.classify == 'CODE_REVIEW_RESPONSE'"
          to: receiving-code-review
        - when: "outputs.classify == 'SKILL_AUTHORING'"
          to: writing-skills
      with:
        request: |
          Execute or prepare execution according to the selected Superpowers discipline. Stop if user approval or missing context is required.
          Classification: {{ outputs.classify | xml_escape | truncate(80) }}
          Plan/test output: {{ outputs.plan_or_test | xml_escape | truncate(3000) }}

    - id: review_gate
      kind: agent
      skill: requesting-code-review
      depends_on: [execution_strategy]
      with:
        request: |
          Review the result for behavioral regressions, missing tests, and integration risks. If no code changed, review the workflow artifact instead.
          Classification: {{ outputs.classify | xml_escape | truncate(80) }}
          Execution strategy output: {{ outputs.execution_strategy | xml_escape | truncate(3000) }}

    - id: verify
      kind: agent
      skill: verification-before-completion
      depends_on: [review_gate]
      with:
        request: |
          Verify before any completion claim. Require concrete evidence, commands, outputs, or explicit limitations.
          Original request: {{ inputs.user_message | xml_escape | truncate(1000) }}
          Review output: {{ outputs.review_gate | xml_escape | truncate(2400) }}

    - id: finish
      kind: agent
      skill: finishing-a-development-branch
      depends_on: [verify]
      with:
        request: |
          If implementation is complete and tests pass, present the normal branch completion options. If this is not a branch-completion moment, say so and stop.
          Verification output: {{ outputs.verify | xml_escape | truncate(2400) }}

    - id: deliver
      kind: llm_chat
      depends_on: [finish]
      with:
        system: "Write a concise final answer in the user's language. Include the chosen Superpowers path, what ran, verification status, and any blocked steps."
        task: |
          Request: {{ inputs.user_message | xml_escape | truncate(1000) }}
          Classification: {{ outputs.classify | xml_escape | truncate(80) }}
          Initial method: {{ outputs.initial_method | xml_escape | truncate(1200) }}
          Plan/test: {{ outputs.plan_or_test | xml_escape | truncate(1200) }}
          Execution: {{ outputs.execution_strategy | xml_escape | truncate(1200) }}
          Verification: {{ outputs.verify | xml_escape | truncate(1200) }}
          Finish: {{ outputs.finish | xml_escape | truncate(1200) }}
---

# Meta Superpowers Workflow

## Overview

This Meta Skill converts the 14 skills under `superpowers/` into a routed
workflow. It is intentionally not "run every skill." It classifies the request,
then follows the smallest Superpowers chain that satisfies the work.

## Included Skills

- `using-superpowers`
- `brainstorming`
- `writing-plans`
- `using-git-worktrees`
- `test-driven-development`
- `systematic-debugging`
- `dispatching-parallel-agents`
- `subagent-driven-development`
- `executing-plans`
- `receiving-code-review`
- `requesting-code-review`
- `verification-before-completion`
- `finishing-a-development-branch`
- `writing-skills`

## Routing Rules

- New feature or creative build: `using-superpowers -> brainstorming -> using-git-worktrees -> writing-plans -> test-driven-development -> requesting-code-review -> verification-before-completion -> finishing-a-development-branch`
- Bug, failed test, or unexpected behavior: `using-superpowers -> systematic-debugging -> test-driven-development -> requesting-code-review -> verification-before-completion -> finishing-a-development-branch`
- Written plan execution: `using-superpowers -> using-git-worktrees -> executing-plans` or `subagent-driven-development -> requesting-code-review -> verification-before-completion -> finishing-a-development-branch`
- Independent parallel work: `using-superpowers -> dispatching-parallel-agents -> subagent-driven-development -> requesting-code-review -> verification-before-completion`
- Code review feedback: `using-superpowers -> receiving-code-review -> test-driven-development if changes are needed -> verification-before-completion`
- Skill creation or editing: `using-superpowers -> writing-skills -> test-driven-development-style skill validation -> verification-before-completion`
- Finish-only request: `using-superpowers -> verification-before-completion -> finishing-a-development-branch`

## Codex Fallback Behavior

If the runtime does not support OpenSquilla `kind: meta`, read this as a normal
Skill and manually follow the routing rules above. Load child skills only when
their route is reached.

## Hard Stops

- Do not implement behavior changes before the TDD step unless the user
  explicitly waives TDD.
- Do not propose bug fixes before root-cause investigation.
- Do not claim completion before verification evidence exists.
- Do not merge, push, publish, delete, or discard work without explicit user
  approval.

## Validation Prompts

- "Use superpowers workflow to build a small feature."
- "Run superpowers on this failing test."
- "Execute this existing implementation plan."
- "Use superpowers to address this review feedback."
- "Create a new skill for this repeated workflow."
