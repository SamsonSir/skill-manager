---
name: meta-superpowers-daily-flow
kind: meta
description: "Use when a normal daily development or product task should follow the fixed Superpowers trio: brainstorm, write a plan, then verify risks."
triggers:
  - superpowers daily flow
  - fixed superpowers flow
  - brainstorm write plan verify
  - daily meta skill
meta_priority: 75
always: false
final_text_mode: auto
metadata:
  opensquilla:
    risk: medium
    capabilities:
      - filesystem-write
      - network-read
composition:
  steps:
    - id: brainstorm
      kind: agent
      skill: brainstorming
      with:
        request: |
          Think through the user's goal, intent, constraints, hidden requirements, and possible approaches.
          Do not implement yet.
          Request: {{ inputs.user_message | xml_escape | truncate(1600) }}

    - id: write_plan
      kind: agent
      skill: writing-plans
      depends_on: [brainstorm]
      with:
        request: |
          Turn the brainstormed direction into a concrete implementation plan.
          Include files, steps, tests, checkpoints, and expected verification.
          Original request: {{ inputs.user_message | xml_escape | truncate(1200) }}
          Brainstorm output: {{ outputs.brainstorm | xml_escape | truncate(2800) }}

    - id: verify
      kind: agent
      skill: verification-before-completion
      depends_on: [write_plan]
      with:
        request: |
          Check the plan for risks, missing tests, unsupported assumptions, unsafe side effects, and unclear acceptance criteria.
          Do not claim implementation is complete; this step verifies plan quality and risk before execution.
          Original request: {{ inputs.user_message | xml_escape | truncate(1000) }}
          Plan output: {{ outputs.write_plan | xml_escape | truncate(3200) }}

    - id: deliver
      kind: llm_chat
      depends_on: [verify]
      with:
        system: "Write a concise Chinese response. Include the plan summary, risks found by verification, and next action."
        task: |
          Request: {{ inputs.user_message | xml_escape | truncate(1000) }}
          Brainstorm: {{ outputs.brainstorm | xml_escape | truncate(1200) }}
          Plan: {{ outputs.write_plan | xml_escape | truncate(1800) }}
          Verification: {{ outputs.verify | xml_escape | truncate(1600) }}
---

# Meta Superpowers Daily Flow

## Overview

This is the strict minimal replica of the workflow described in the WeChat
article:

`brainstorm -> write_plan -> verify`

It is meant for daily repeated work where the agent should not decide whether
these steps are needed. The order is fixed and enforced by `depends_on`.

## What Each Step Does

- `brainstorm`: uses `brainstorming` to clarify requirements and choose an approach.
- `write_plan`: uses `writing-plans` to produce a concrete plan.
- `verify`: uses `verification-before-completion` to check risk, tests, assumptions, and acceptance criteria.

## What This Does Not Do

- It does not execute the plan.
- It does not create a branch or PR.
- It does not run all 14 Superpowers skills.
- It does not let the agent skip planning because the task "looks simple."

## When to Use

Use this when you want the article's fixed daily trio, especially before
starting product, coding, automation, or workflow work.

Use `meta-superpowers-workflow` instead when you want full routing across all
Superpowers skills, such as bug fixing, review handling, TDD implementation, or
branch finishing.
