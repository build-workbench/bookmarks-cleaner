# References

This bibliography is organized around the arguments made across the site. Each cluster answers a specific design question rather than serving as a decorative reading list.

## Classifier Fusion and Ensemble Design

1. **Kuncheva, L. I.** (2004). *Combining Pattern Classifiers: Methods and Algorithms*. Wiley-Interscience.  
   Why it matters here: grounds the decision to treat fusion as a first-class design concern rather than an afterthought.
2. **Wolpert, D. H.** (1992). Stacked generalization. *Neural Networks*, 5(2), 241-259.  
   Why it matters here: provides the counterpoint to weighted voting, making the site's "why not stacking" argument explicit.
3. **Zhou, Z.-H.** (2012). *Ensemble Methods: Foundations and Algorithms*. CRC Press.  
   Why it matters here: frames the trade-off space for heterogeneous ensemble systems.

## Confidence and Calibration

4. **Zadrozny, B., & Elkan, C.** (2001). Obtaining calibrated probability estimates from decision trees and naive Bayesian classifiers. *ICML*, 609-616.  
   Why it matters here: supports the claim that raw classifier scores are not directly comparable.
5. **Platt, J.** (1999). Probabilistic outputs for support vector machines and comparisons to regularized likelihood methods. *Advances in Large Margin Classifiers*, 61-74.  
   Why it matters here: useful background for confidence shaping and score interpretation.

## Text Classification and Semantic Enrichment

6. **Joulin, A., Grave, E., Bojanowski, P., & Mikolov, T.** (2017). Bag of tricks for efficient text classification. *EACL*, 427-431.  
   Why it matters here: practical grounding for lightweight local text classification approaches.
7. **Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K.** (2019). BERT: Pre-training of deep bidirectional transformers for language understanding. *NAACL-HLT*, 4171-4186.  
   Why it matters here: background for semantic analysis paths that go beyond domain rules.
8. **Reimers, N., & Gurevych, I.** (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. *EMNLP-IJCNLP*, 3982-3992.  
   Why it matters here: explains the semantic embedding layer that helps recover hard bookmark cases.

## Software Architecture and Maintainability

9. **Martin, R. C.** (2017). *Clean Architecture: A Craftsman's Guide to Software Structure and Design*. Prentice Hall.  
   Why it matters here: supports the repository's emphasis on boundaries, contracts, and low blast radius changes.
10. **Fowler, M.** (2002). *Patterns of Enterprise Application Architecture*. Addison-Wesley.  
    Why it matters here: useful vocabulary for façade, coordination, and composition-root thinking in the runtime.
11. **Gamma, E., Helm, R., Johnson, R., & Vlissides, J.** (1994). *Design Patterns*. Addison-Wesley.  
    Why it matters here: provides the shared pattern language behind façade and other structural choices.

## Practical Documentation and Adjacent Systems

12. **scikit-learn Documentation.** Text feature extraction and model interfaces.  
    Why it matters here: practical implementation substrate for local classifier experiments.
13. **Sentence Transformers Documentation.**  
    Why it matters here: operational reference for embedding-backed semantic enrichment.
14. **MDN Web Docs.** Browser bookmark and web data references.  
    Why it matters here: supports the format-boundary assumptions made at the input layer.

## Citation Guidance

When the whitepaper cites a concept inline, treat this page as the stable reference index. The goal is not exhaustive scholarship, but a transparent bridge between the site's claims and the literature that informed them.
