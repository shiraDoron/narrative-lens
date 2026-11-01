# Author Style Controlled Experiment — executed CPU pilot

This is an executed exploratory pilot, not an independent confirmatory study. Original data and checkpoint hashes are recorded in split_audit.json.

## Executed

28 account-author identifiers; 336 texts after original semantic-duplicate exclusions; three training seeds. Four primary conditions; local pinned LLM generation; bidirectional NLI, NER, numeric/negation/certainty/framing-anchor checks; author-disjoint narrative evaluation; independently refitted closed-set within-narrative author probes; crossed counterfactual styles and stance-change controls.

## Semantic screening

Matched accepted rows: 94; test: 24. Full seven-label primary comparison estimable: True. Automated checks are not independent human verification. Failure rates are in validation_failure_rates.csv. Invalid rewrites are never silently called preserved semantics.

## Results

 seed  n  accuracy  macro_f1      nll    brier  recall_Zionist  recall_Resistance  recall_Western  recall_Russian  recall_Ukrainian  recall_Right-wing  recall_Left-wing
   42 84  0.392857  0.390422 1.548263 0.736484        0.583333           0.333333        0.333333             0.0          0.583333           0.416667          0.500000
    7 84  0.380952  0.372712 1.533328 0.732096        0.416667           0.333333        0.416667             0.0          0.583333           0.333333          0.583333
  123 84  0.428571  0.417151 1.686731 0.777033        0.666667           0.333333        0.333333             0.0          0.666667           0.500000          0.500000

                                 scope train_condition test_condition  macro_f1_mean  macro_f1_std  accuracy_mean  accuracy_std  nll_mean  nll_std  brier_mean  brier_std
existing_deployed_overlap_not_disjoint        Existing     Formatting       0.843366           NaN       0.845238           NaN  0.520280      NaN    0.244109        NaN
existing_deployed_overlap_not_disjoint        Existing     Normalized       0.785716           NaN       0.785714           NaN  0.600821      NaN    0.295419        NaN
existing_deployed_overlap_not_disjoint        Existing       Original       0.856280           NaN       0.857143           NaN  0.468941      NaN    0.222271        NaN
existing_deployed_overlap_not_disjoint        Existing     Paraphrase       0.795099           NaN       0.797619           NaN  0.573999      NaN    0.292554        NaN
       fixed_all_generated_descriptive        Original     Formatting       0.385132      0.042748       0.392857      0.047619  1.593088 0.086350    0.748205   0.026569
       fixed_all_generated_descriptive        Original     Normalized       0.363198      0.023214       0.376984      0.024782  1.623744 0.073709    0.759736   0.020831
       fixed_all_generated_descriptive        Original       Original       0.393428      0.022372       0.400794      0.024782  1.589440 0.084586    0.748538   0.024775
       fixed_all_generated_descriptive        Original     Paraphrase       0.350418      0.008219       0.365079      0.006873  1.618636 0.077204    0.758333   0.022116
          fixed_matched_automated_pass        Original     Formatting       0.201587      0.013746       0.300000      0.000000  1.953593 0.050932    0.857005   0.011261
          fixed_matched_automated_pass        Original     Normalized       0.185714      0.000000       0.300000      0.000000  1.960905 0.059890    0.857112   0.011896
          fixed_matched_automated_pass        Original       Original       0.193651      0.013746       0.300000      0.000000  1.945859 0.048215    0.856565   0.011564
          fixed_matched_automated_pass        Original     Paraphrase       0.185714      0.000000       0.300000      0.000000  1.967999 0.064575    0.858125   0.012843
   fixed_matched_paraphrase_normalized        Original     Normalized       0.204762      0.008248       0.263889      0.024056  1.799029 0.024296    0.821785   0.001465
   fixed_matched_paraphrase_normalized        Original       Original       0.218896      0.032730       0.277778      0.048113  1.758391 0.041869    0.809222   0.007448
   fixed_matched_paraphrase_normalized        Original     Paraphrase       0.204762      0.008248       0.263889      0.024056  1.789030 0.029999    0.817903   0.003627
     retrain_all_generated_descriptive      Normalized     Normalized       0.369610      0.042574       0.380952      0.042923  1.681632 0.088082    0.778327   0.024527
     retrain_all_generated_descriptive      Normalized       Original       0.370158      0.041222       0.376984      0.045071  1.659049 0.099366    0.770250   0.029885
     retrain_all_generated_descriptive      Normalized     Paraphrase       0.341039      0.030877       0.353175      0.036370  1.679026 0.094860    0.777965   0.026351
     retrain_all_generated_descriptive        Original     Normalized       0.363198      0.023214       0.376984      0.024782  1.623744 0.073709    0.759736   0.020831
     retrain_all_generated_descriptive        Original       Original       0.393428      0.022372       0.400794      0.024782  1.589440 0.084586    0.748538   0.024775
     retrain_all_generated_descriptive        Original     Paraphrase       0.350418      0.008219       0.365079      0.006873  1.618636 0.077204    0.758333   0.022116
     retrain_all_generated_descriptive      Paraphrase     Normalized       0.357395      0.025140       0.365079      0.027493  1.665668 0.037953    0.772984   0.010570
     retrain_all_generated_descriptive      Paraphrase       Original       0.367833      0.029370       0.376984      0.027493  1.642688 0.041076    0.765762   0.011797
     retrain_all_generated_descriptive      Paraphrase     Paraphrase       0.354514      0.024981       0.365079      0.027493  1.664498 0.037612    0.773022   0.010705
        retrain_matched_automated_pass      Normalized     Normalized       0.083565      0.017206       0.166667      0.072169  1.943270 0.007723    0.855126   0.002748
        retrain_matched_automated_pass      Normalized       Original       0.093476      0.018292       0.180556      0.063647  1.936915 0.008784    0.853091   0.004666
        retrain_matched_automated_pass      Normalized     Paraphrase       0.084430      0.016734       0.166667      0.072169  1.941388 0.008167    0.854458   0.003415
        retrain_matched_automated_pass        Original     Normalized       0.092177      0.013361       0.208333      0.072169  1.939828 0.009098    0.853959   0.002227
        retrain_matched_automated_pass        Original       Original       0.088020      0.016586       0.194444      0.063647  1.930423 0.009313    0.851046   0.003626
        retrain_matched_automated_pass        Original     Paraphrase       0.087800      0.013881       0.194444      0.063647  1.937572 0.008148    0.853180   0.002189
        retrain_matched_automated_pass      Paraphrase     Normalized       0.076825      0.008589       0.208333      0.072169  1.935415 0.006964    0.853517   0.002594
        retrain_matched_automated_pass      Paraphrase       Original       0.082951      0.019460       0.208333      0.041667  1.930309 0.010807    0.851974   0.003886
        retrain_matched_automated_pass      Paraphrase     Paraphrase       0.073317      0.004140       0.194444      0.063647  1.933874 0.007594    0.853031   0.002816

## Interpretation

The all_generated_descriptive cohort includes rejected outputs and cannot establish a benefit from style-only intervention. The matched cohort, when estimable, is conditional on automated acceptance and still lacks human semantic gold validation. Same-account source labels are not independently annotated text narratives. StanceChanged is a manipulation attempt, not a verified seven-class narrative change; label flips alone do not demonstrate appropriate stance sensitivity.

## Limitations

Small stratified pilot; only one test author per class; single author split; pre-existing author identities already explored in this repository; weak local 0.5B generator; one generation draw; lexical guards can reject harmless paraphrases and miss changed agency/stance; binary NLI is not a factuality or framing oracle; automatic language selection; account not necessarily individual writer; semantic-near-duplicate thresholds are operational, not a guarantee against every latent variant. Reported seed variability is training variability, not uncertainty over unseen authors.

## Verdict

Style sensitivity: evaluate counterfactual_results.csv only among semantically accepted variants, with automated-only qualification. Author-information reduction: compare newly trained probes, not cross-domain probe transfer. Unseen-author benefit beyond paraphrase: interpret matched cohort only if all classes survive. Causality: NOT ESTABLISHED. LoRA/DoRA: not justified solely by this pilot; first improve generation/independent validation and enlarge untouched author evaluation.

## Reproduce

See README.md. All outputs are isolated under this experiment directory. No original model was overwritten.
