---
name: Bug report
description: Report a defect in the YOLO Image Gateway
title: "bug: "
labels: [bug]
body:
  - type: markdown
    attributes:
      value: |
        Thanks for reporting a bug. Please include enough detail to reproduce the behavior without using private images or secrets.
  - type: textarea
    id: summary
    attributes:
      label: Summary
      description: What went wrong?
    validations:
      required: true
  - type: textarea
    id: reproduce
    attributes:
      label: Steps to reproduce
      description: Include request shape, endpoint, and minimal image/input details. Do not paste secrets.
      placeholder: |
        1. Start server with ...
        2. Send request to ...
        3. Observe ...
    validations:
      required: true
  - type: dropdown
    id: endpoint
    attributes:
      label: Affected endpoint
      options:
        - POST /v1/chat/completions
        - GET /v1/models
        - GET /healthz
        - Other / unknown
    validations:
      required: true
  - type: textarea
    id: expected
    attributes:
      label: Expected behavior
    validations:
      required: true
  - type: textarea
    id: actual
    attributes:
      label: Actual behavior
    validations:
      required: true
  - type: textarea
    id: environment
    attributes:
      label: Environment
      placeholder: |
        OS:
        Python:
        CPU:
        GPU present? yes/no:
        Package version / commit:
    validations:
      required: false
  - type: checkboxes
    id: scope
    attributes:
      label: Scope check
      options:
        - label: This report is not requesting tracking support.
        - label: This report is not requesting video support.
        - label: This report is not requesting segmentation support.
