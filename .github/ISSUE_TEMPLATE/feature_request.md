---
name: Feature request
description: Propose a scoped feature for the YOLO Image Gateway
title: "feat: "
labels: [enhancement]
body:
  - type: textarea
    id: problem
    attributes:
      label: Problem / use case
      description: What user problem would this solve?
    validations:
      required: true
  - type: textarea
    id: proposal
    attributes:
      label: Proposed behavior
      description: Describe the smallest useful behavior.
    validations:
      required: true
  - type: checkboxes
    id: non_goals
    attributes:
      label: Non-goal compatibility
      options:
        - label: This does not require tracking.
        - label: This does not require video processing.
        - label: This does not require segmentation.
        - label: This does not require background jobs or queues.
        - label: This does not require a database.
        - label: This does not require GPU/CUDA.
  - type: textarea
    id: acceptance
    attributes:
      label: Acceptance criteria
      description: What testable behavior proves the feature works?
      placeholder: |
        - ...
    validations:
      required: true
