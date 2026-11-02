# Patch unit tests

18 tests passed; 0 failures/errors. Every successful fixture asserts the complete expected text and reconstruction from exact edited offsets; rejection fixtures assert the expected exception/current-text behavior.

```text
test_attribution (test_patch_contract.ContractTests.test_attribution) ... ok
test_broad (test_patch_contract.ContractTests.test_broad) ... ok
test_certainty (test_patch_contract.ContractTests.test_certainty) ... ok
test_current_text (test_patch_contract.ContractTests.test_current_text) ... ok
test_delete (test_patch_contract.ContractTests.test_delete) ... ok
test_event (test_patch_contract.ContractTests.test_event) ... ok
test_evidence (test_patch_contract.ContractTests.test_evidence) ... ok
test_insert_after (test_patch_contract.ContractTests.test_insert_after) ... ok
test_insert_before (test_patch_contract.ContractTests.test_insert_before) ... ok
test_lookup (test_patch_contract.ContractTests.test_lookup) ... ok
test_lookup_ambiguous (test_patch_contract.ContractTests.test_lookup_ambiguous) ... ok
test_missing (test_patch_contract.ContractTests.test_missing) ... ok
test_multiple (test_patch_contract.ContractTests.test_multiple) ... ok
test_noop (test_patch_contract.ContractTests.test_noop) ... ok
test_number (test_patch_contract.ContractTests.test_number) ... ok
test_quote (test_patch_contract.ContractTests.test_quote) ... ok
test_roles (test_patch_contract.ContractTests.test_roles) ... ok
test_whitespace (test_patch_contract.ContractTests.test_whitespace) ... ok

----------------------------------------------------------------------
Ran 18 tests in 0.001s

OK
```
