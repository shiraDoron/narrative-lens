# Integrity test results

19 tests passed, 0 failures, 0 errors. Verified sources, paired/grouped folds, recomputed metrics, Holm adjustment, reconstruction of fit subsets, temporal-control separation and blank human fields. No Narrative Classifier or frozen test evaluation was run.

```text
test_01_frozen_sources_unchanged (test_integrity.IntegrityTests.test_01_frozen_sources_unchanged) ... ok
test_02_only_train_authors_used (test_integrity.IntegrityTests.test_02_only_train_authors_used) ... ok
test_03_no_pair_filtered (test_integrity.IntegrityTests.test_03_no_pair_filtered) ... ok
test_04_group_disjoint_cv (test_integrity.IntegrityTests.test_04_group_disjoint_cv) ... ok
test_05_every_cv_metric_recomputes (test_integrity.IntegrityTests.test_05_every_cv_metric_recomputes) ... ok
test_06_fixed_fit_excludes_all_paired_groups (test_integrity.IntegrityTests.test_06_fixed_fit_excludes_all_paired_groups) ... ok
test_07_fixed_metrics_and_mcnemar (test_integrity.IntegrityTests.test_07_fixed_metrics_and_mcnemar) ... ok
test_08_holm_uses_all_four_primary_methods (test_integrity.IntegrityTests.test_08_holm_uses_all_four_primary_methods) ... ok
test_09_original_human_package_blank_and_exact (test_integrity.IntegrityTests.test_09_original_human_package_blank_and_exact) ... ok
test_10_additional_rewrite_manifest_exact (test_integrity.IntegrityTests.test_10_additional_rewrite_manifest_exact) ... ok
test_11_no_test_or_val_in_topics_and_style (test_integrity.IntegrityTests.test_11_no_test_or_val_in_topics_and_style) ... ok
test_12_confusion_totals (test_integrity.IntegrityTests.test_12_confusion_totals) ... ok
test_13_old_30_probe_is_recomputed_without_retraining (test_integrity.IntegrityTests.test_13_old_30_probe_is_recomputed_without_retraining) ... ok
test_14_protocol_frozen_before_results (test_integrity.IntegrityTests.test_14_protocol_frozen_before_results) ... ok
test_15_source_article_groups_unique (test_integrity.IntegrityTests.test_15_source_article_groups_unique) ... ok
test_16_aggregate_review_not_invented_per_id (test_integrity.IntegrityTests.test_16_aggregate_review_not_invented_per_id) ... ok
test_17_temporal_sensitivity_is_train_only_and_pair_disjoint (test_integrity.IntegrityTests.test_17_temporal_sensitivity_is_train_only_and_pair_disjoint) ... ok
test_18_source_human_forms_are_not_machine_gold (test_integrity.IntegrityTests.test_18_source_human_forms_are_not_machine_gold) ... ok
test_19_resample_and_expansion_metadata (test_integrity.IntegrityTests.test_19_resample_and_expansion_metadata) ... ok

----------------------------------------------------------------------
Ran 19 tests in 4.185s

OK
```
