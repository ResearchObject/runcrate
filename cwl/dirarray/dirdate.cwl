#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: CommandLineTool
baseCommand: [date, "-r"]

inputs:
  dir:
    type: Directory
    inputBinding:
      position: 1

outputs: []
