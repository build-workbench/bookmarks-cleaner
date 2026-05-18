# 参考文献

本页按“站点论证需要什么证据”来组织文献，而不是把参考资料当作装饰性阅读清单。每一组文献都对应一个明确的设计问题。

## 分类器融合与集成设计

1. **Kuncheva, L. I.** (2004). *Combining Pattern Classifiers: Methods and Algorithms*. Wiley-Interscience.  
   对本项目的意义：为“把融合当作一等设计问题”提供理论底座。
2. **Wolpert, D. H.** (1992). Stacked generalization. *Neural Networks*, 5(2), 241-259.  
   对本项目的意义：作为 weighted voting 的对照路线，使“为什么不直接 stacking”这件事有清晰参照。
3. **Zhou, Z.-H.** (2012). *Ensemble Methods: Foundations and Algorithms*. CRC Press.  
   对本项目的意义：帮助理解异构集成系统的权衡空间。

## 置信度与校准

4. **Zadrozny, B., & Elkan, C.** (2001). Obtaining calibrated probability estimates from decision trees and naive Bayesian classifiers. *ICML*, 609-616.  
   对本项目的意义：支撑“不同分类器原始分数不能直接比较”的论断。
5. **Platt, J.** (1999). Probabilistic outputs for support vector machines and comparisons to regularized likelihood methods. *Advances in Large Margin Classifiers*, 61-74.  
   对本项目的意义：为置信度整形与分数解释提供背景。

## 文本分类与语义增强

6. **Joulin, A., Grave, E., Bojanowski, P., & Mikolov, T.** (2017). Bag of tricks for efficient text classification. *EACL*, 427-431.  
   对本项目的意义：为轻量本地文本分类提供实用方法学背景。
7. **Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K.** (2019). BERT: Pre-training of deep bidirectional transformers for language understanding. *NAACL-HLT*, 4171-4186.  
   对本项目的意义：为超越域名规则的语义路径提供理论背景。
8. **Reimers, N., & Gurevych, I.** (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. *EMNLP-IJCNLP*, 3982-3992.  
   对本项目的意义：解释 embedding 语义层如何帮助处理困难书签样本。

## 软件架构与可维护性

9. **Martin, R. C.** (2017). *Clean Architecture: A Craftsman's Guide to Software Structure and Design*. Prentice Hall.  
   对本项目的意义：支撑仓库对边界、契约与低爆炸半径变更的重视。
10. **Fowler, M.** (2002). *Patterns of Enterprise Application Architecture*. Addison-Wesley.  
    对本项目的意义：为 façade、协调层与组合根等运行时词汇提供共享语义。
11. **Gamma, E., Helm, R., Johnson, R., & Vlissides, J.** (1994). *Design Patterns*. Addison-Wesley.  
    对本项目的意义：为 façade 等结构性选择提供通用模式语言。

## 实用资料与邻近系统

12. **scikit-learn Documentation.** 文本特征提取与模型接口。  
    对本项目的意义：本地分类实验的重要实现底座。
13. **Sentence Transformers Documentation.**  
    对本项目的意义：embedding 驱动语义增强的操作层参考。
14. **MDN Web Docs.** 浏览器书签与相关 Web 数据说明。  
    对本项目的意义：支撑输入层对导出格式边界的假设。

## 引用说明

当白皮书或架构页在正文中引用某个概念时，本页就是稳定的索引层。目标不是“列尽所有论文”，而是让站点中的关键论断都能找到可追溯的来源。
