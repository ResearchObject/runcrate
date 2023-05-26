cwlVersion: v1.2
class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}

inputs:
  in_file: File

outputs:
  out_file:
    type: File
    outputSource:
      - date/date_out
      - isodate/date_out
    pickValue: first_non_null

steps:
  date:
    in:
      somefile: in_file
    out: [date_out]
    run: datetool.cwl
  isodate:
    in:
      somefile: in_file
    out: [date_out]
    run: isodatetool.cwl
