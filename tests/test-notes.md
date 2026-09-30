# Test notes

Coverage in [test_bao.py](test_bao.py):

| Behaviour tested | Test function |
| --- | --- |
| Adding and listing each task kind | `test_adding_and_listing` |
| Marking, unmarking, noting, and deleting | `test_marking_unmarking_noting_and_deleting` |
| Missing and malformed input, invalid dates, and out-of-range times; no changes saved after invalid input | `test_invalid_inputs` |
| Saving and loading tasks and changes, including a missing data folder | `test_saving_and_loading` |
| Deadline parsing and `due`, including matching and nonmatching dates | `test_deadline_parsing_and_due` |
| Case-insensitive partial matching with `find`, excluding notes | `test_find` |
