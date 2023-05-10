#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: Workflow

requirements:
  ScatterFeatureRequirement: {}

inputs:
  dir_array: Directory[]

outputs: []

steps:
  date_step:
    label: Prints date of input dirs
    scatter: dir
    in:
      dir: dir_array
    out: []
    run: dirdate.cwl
