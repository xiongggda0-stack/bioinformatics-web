from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Pipeline


def build_mock_pipelines() -> list[dict[str, Any]]:
    return [
        {
            "title": "Bulk RNA-seq 标准差异表达分析增强版",
            "description": "面向 bulk RNA-seq 项目的标准差异表达增强流程，覆盖实验设计、FASTQ 质控、STAR/Salmon 定量、DESeq2 统计建模、可视化、富集分析与结果交付。",
            "omics_type": "RNA-Seq",
            "dag_json": {
                "nodes": [
                    {"id": "design", "label": "实验设计与样本表"},
                    {"id": "raw_qc", "label": "FastQC/MultiQC 原始质控"},
                    {"id": "trim", "label": "fastp/Trim Galore 清洗"},
                    {"id": "quant_route", "label": "STAR+featureCounts 或 Salmon"},
                    {"id": "count_matrix", "label": "基因 count 矩阵"},
                    {"id": "sample_qc", "label": "PCA/相关性/离群样本"},
                    {"id": "deseq2", "label": "DESeq2 差异表达"},
                    {"id": "annotation", "label": "基因注释与 ID 转换"},
                    {"id": "enrichment", "label": "GO/KEGG/GSEA 富集"},
                    {"id": "report", "label": "报告与结果交付"},
                ],
                "edges": [
                    {"source": "design", "target": "raw_qc"},
                    {"source": "raw_qc", "target": "trim"},
                    {"source": "trim", "target": "quant_route"},
                    {"source": "quant_route", "target": "count_matrix"},
                    {"source": "count_matrix", "target": "sample_qc"},
                    {"source": "sample_qc", "target": "deseq2"},
                    {"source": "deseq2", "target": "annotation"},
                    {"source": "annotation", "target": "enrichment"},
                    {"source": "enrichment", "target": "report"},
                ],
            },
            "content": """# Bulk RNA-seq 标准差异表达分析增强版

## 一、适用场景

bulk RNA-seq 以样本为单位测量组织、细胞群或处理条件下的整体转录水平，最常见目标是寻找不同组之间的差异表达基因，并解释这些基因背后的通路和生物学过程。

本增强版适用于：

- 处理组 vs 对照组的标准差异表达分析。
- 多处理、多时间点、多组织的表达变化比较。
- 动植物、微生物、肿瘤、免疫、胁迫响应等常规转录组项目。
- 需要同时交付 count matrix、TPM、DEG、火山图、热图、PCA、富集分析和可复用报告的项目。

不适合直接套用的场景：

- 没有生物学重复的项目：只能做探索性分析，不建议做严格差异检验。
- 单细胞 RNA-seq：应走 scRNA-seq 专用流程。
- 长读长转录组：应优先考虑 Iso-Seq、FLAIR、TALON、StringTie2 等流程。
- 可变剪接为核心目标：应增加 rMATS、SUPPA2、MAJIQ 等模块。

## 二、bulk RNA-seq 分析类型

| 类型 | 主要问题 | 推荐方法 | 关键输出 |
| --- | --- | --- | --- |
| 基因表达定量 | 每个样本中每个基因表达量是多少？ | STAR + featureCounts 或 Salmon + tximport | raw count、TPM |
| 差异表达分析 | 处理组相对对照组哪些基因显著变化？ | DESeq2、edgeR、limma-voom | DEG table、log2FC、padj |
| 样本质量评估 | 样本是否聚类合理？是否有离群样本？ | PCA、样本相关性、距离热图 | PCA plot、correlation heatmap |
| 功能富集分析 | DEG 指向哪些功能和通路？ | clusterProfiler、fgsea、GSEA | GO/KEGG/GSEA 结果 |
| 表达模式聚类 | 多组/时间点基因如何动态变化？ | k-means、Mfuzz、maSigPro | gene clusters |
| 共表达网络 | 哪些基因模块与性状相关？ | WGCNA | module-trait relationship |
| 转录本层分析 | isoform 是否变化？ | Salmon/Kallisto + tximport、IsoformSwitchAnalyzeR | transcript abundance、isoform switch |

## 三、最佳实践路线

### 推荐主路线

对标准 bulk RNA-seq 差异表达，建议采用：

1. `FastQC + MultiQC` 汇总原始数据质量。
2. `fastp` 或 `Trim Galore` 去接头和过滤低质量 reads。
3. 选择一条定量路线：
   - 需要 BAM、基因组坐标和比对质控：`STAR + featureCounts`。
   - 追求速度、转录本定量和轻量流程：`Salmon + tximport`。
4. 使用 raw count 进入 `DESeq2`，不要用 TPM/FPKM 做 DESeq2 差异检验。
5. 使用 `vst` 或 `rlog` 做 PCA、样本距离和热图。
6. DEG 结果做基因注释、火山图、热图、GO/KEGG/GSEA。

### 方法选择建议

| 场景 | 推荐路线 | 理由 |
| --- | --- | --- |
| 常规有参考基因组物种 | STAR + featureCounts + DESeq2 | 结果直观，BAM 可复查 |
| 样本量很大，想快速完成表达定量 | Salmon + tximport + DESeq2 | 速度快，占用资源少 |
| 关注转录本/isoform | Salmon/Kallisto + tximport | 保留 transcript-level 信息 |
| 非模式物种且注释较弱 | HISAT2/STAR + StringTie | 可辅助转录本组装 |
| 无参考基因组 | Trinity + Salmon/RSEM | 需要 de novo transcriptome |

## 四、整体流程图

```mermaid
flowchart TD
    A[实验设计与样本信息表] --> B[原始 FASTQ]
    B --> C[FastQC / MultiQC]
    C --> D{质量是否合格?}
    D -- 否 --> E[fastp / Trim Galore 清洗]
    D -- 是 --> F[选择定量路线]
    E --> F
    F --> G1[STAR 比对]
    F --> G2[Salmon 准比对]
    G1 --> H1[featureCounts 基因计数]
    G2 --> H2[tximport 转为 gene-level count]
    H1 --> I[raw count matrix]
    H2 --> I
    I --> J[样本 QC: PCA / 相关性 / 离群样本]
    J --> K[DESeq2 建模与差异检验]
    K --> L[基因注释 / ID 转换]
    L --> M[火山图 / 热图 / MA plot]
    L --> N[GO / KEGG / GSEA]
    M --> O[结果报告]
    N --> O
```

## 五、项目目录建议

```text
bulk_rnaseq_project/
├── 00_metadata/
│   ├── sample_info.csv
│   └── contrasts.csv
├── 01_raw_data/
├── 02_qc_raw/
├── 03_clean_data/
├── 04_qc_clean/
├── 05_alignment/
│   ├── star_index/
│   ├── bam/
│   └── logs/
├── 06_counts/
├── 07_deseq2/
│   ├── tables/
│   ├── plots/
│   └── rds/
├── 08_enrichment/
└── report/
```

样本信息表 `sample_info.csv`：

| sample_id | condition | batch | replicate | fastq_1 | fastq_2 |
| --- | --- | --- | --- | --- | --- |
| Ctrl_1 | Ctrl | B1 | 1 | Ctrl_1_R1.fq.gz | Ctrl_1_R2.fq.gz |
| Ctrl_2 | Ctrl | B1 | 2 | Ctrl_2_R1.fq.gz | Ctrl_2_R2.fq.gz |
| Treat_1 | Treat | B1 | 1 | Treat_1_R1.fq.gz | Treat_1_R2.fq.gz |
| Treat_2 | Treat | B1 | 2 | Treat_2_R1.fq.gz | Treat_2_R2.fq.gz |

比较组表 `contrasts.csv`：

| contrast_name | numerator | denominator |
| --- | --- | --- |
| Treat_vs_Ctrl | Treat | Ctrl |

## 六、实验设计检查

差异表达的统计可靠性主要取决于实验设计。

| 检查项 | 推荐 |
| --- | --- |
| 生物学重复 | 每组至少 3 个，复杂设计建议更多 |
| 技术重复 | 通常先合并或作为 QC，不替代生物学重复 |
| 批次信息 | 必须记录，必要时进入设计公式 |
| 测序深度 | 常规 mRNA-seq 每样本 20-40M reads 可作为起点 |
| 配对设计 | 同一供体前后处理应写入设计公式 |

DESeq2 设计公式示例：

```r
design = ~ condition
design = ~ batch + condition
design = ~ donor + condition
design = ~ batch + time + condition + time:condition
```

解释原则：

- `condition` 是你真正关心的生物学变量。
- `batch`、`donor`、`sex` 等是需要控制的协变量。
- 不要把与 condition 完全混杂的 batch 强行加入模型，否则模型不可估。

## 七、FASTQ 质控与清洗

### 1. 原始数据质控

```bash
mkdir -p 02_qc_raw/fastqc 02_qc_raw/multiqc

fastqc -t 8 \
  -o 02_qc_raw/fastqc \
  01_raw_data/*.fq.gz

multiqc 02_qc_raw/fastqc \
  -o 02_qc_raw/multiqc
```

重点查看：

| 指标 | 关注点 |
| --- | --- |
| Per base sequence quality | 末端质量是否明显下降 |
| Adapter Content | 是否有接头污染 |
| Per sequence GC content | 是否有异常峰 |
| Sequence Duplication Levels | 重复率是否过高 |
| Overrepresented sequences | 是否有 rRNA、接头或污染序列 |

### 2. fastp 清洗

```bash
mkdir -p 03_clean_data 04_qc_clean/fastp

for sample in Ctrl_1 Ctrl_2 Ctrl_3 Treat_1 Treat_2 Treat_3
do
  fastp \
    -i 01_raw_data/${sample}_R1.fq.gz \
    -I 01_raw_data/${sample}_R2.fq.gz \
    -o 03_clean_data/${sample}_R1.clean.fq.gz \
    -O 03_clean_data/${sample}_R2.clean.fq.gz \
    --detect_adapter_for_pe \
    --cut_front \
    --cut_tail \
    --cut_window_size 4 \
    --cut_mean_quality 20 \
    --length_required 30 \
    --thread 8 \
    --html 04_qc_clean/fastp/${sample}.html \
    --json 04_qc_clean/fastp/${sample}.json
done

multiqc 04_qc_clean/fastp -o 04_qc_clean/multiqc
```

## 八、路线 A：STAR + featureCounts

### 1. 构建 STAR 索引

```bash
mkdir -p 05_alignment/star_index

STAR \
  --runThreadN 16 \
  --runMode genomeGenerate \
  --genomeDir 05_alignment/star_index \
  --genomeFastaFiles ref/genome.fa \
  --sjdbGTFfile ref/genes.gtf \
  --sjdbOverhang 149
```

`sjdbOverhang` 通常设为 read length - 1，例如 PE150 设置为 149。

### 2. STAR 比对

```bash
mkdir -p 05_alignment/bam 05_alignment/logs

for sample in Ctrl_1 Ctrl_2 Ctrl_3 Treat_1 Treat_2 Treat_3
do
  STAR \
    --runThreadN 16 \
    --genomeDir 05_alignment/star_index \
    --readFilesIn \
      03_clean_data/${sample}_R1.clean.fq.gz \
      03_clean_data/${sample}_R2.clean.fq.gz \
    --readFilesCommand zcat \
    --outFileNamePrefix 05_alignment/bam/${sample}_ \
    --outSAMtype BAM SortedByCoordinate \
    --quantMode GeneCounts \
    --outFilterMultimapNmax 10 \
    --outFilterMismatchNoverLmax 0.04

  samtools index 05_alignment/bam/${sample}_Aligned.sortedByCoord.out.bam
done
```

### 3. 汇总比对质量

```bash
mkdir -p 05_alignment/summary

echo "sample,total_reads,unique_mapping_rate,multi_mapping_rate" > 05_alignment/summary/star_mapping_summary.csv

for sample in Ctrl_1 Ctrl_2 Ctrl_3 Treat_1 Treat_2 Treat_3
do
  log=05_alignment/bam/${sample}_Log.final.out
  total=$(grep "Number of input reads" ${log} | awk '{print $6}')
  unique=$(grep "Uniquely mapped reads %" ${log} | awk '{print $6}' | sed 's/%//')
  multi=$(grep "% of reads mapped to multiple loci" ${log} | awk '{print $9}' | sed 's/%//')
  echo "${sample},${total},${unique},${multi}" >> 05_alignment/summary/star_mapping_summary.csv
done
```

### 4. featureCounts 基因计数

```bash
mkdir -p 06_counts

featureCounts \
  -T 12 \
  -p \
  -B \
  -C \
  -t exon \
  -g gene_id \
  -a ref/genes.gtf \
  -o 06_counts/gene_counts.txt \
  05_alignment/bam/*_Aligned.sortedByCoord.out.bam
```

提取 count matrix：

```bash
cut -f1,7- 06_counts/gene_counts.txt > 06_counts/count_matrix.raw.txt
```

## 九、路线 B：Salmon + tximport

如果项目更关注速度和转录本定量，可以使用 Salmon。

```bash
mkdir -p ref/salmon_index

salmon index \
  -t ref/transcripts.fa \
  -i ref/salmon_index \
  -p 12
```

```bash
mkdir -p 06_salmon

for sample in Ctrl_1 Ctrl_2 Ctrl_3 Treat_1 Treat_2 Treat_3
do
  salmon quant \
    -i ref/salmon_index \
    -l A \
    -1 03_clean_data/${sample}_R1.clean.fq.gz \
    -2 03_clean_data/${sample}_R2.clean.fq.gz \
    --validateMappings \
    --gcBias \
    --seqBias \
    -p 12 \
    -o 06_salmon/${sample}
done
```

tximport 导入：

```r
library(tximport)
library(readr)

sample_info <- read.csv("00_metadata/sample_info.csv")
files <- file.path("06_salmon", sample_info$sample_id, "quant.sf")
names(files) <- sample_info$sample_id

tx2gene <- read.delim("ref/tx2gene.tsv", header = TRUE)

txi <- tximport(
  files,
  type = "salmon",
  tx2gene = tx2gene,
  countsFromAbundance = "lengthScaledTPM"
)
```

## 十、DESeq2 差异表达分析

### 1. 读取 count matrix

STAR + featureCounts 路线：

```r
library(DESeq2)
library(tidyverse)
library(pheatmap)
library(ggrepel)

sample_info <- read.csv("00_metadata/sample_info.csv", row.names = 1)
count_data <- read.delim("06_counts/count_matrix.raw.txt", check.names = FALSE)

rownames(count_data) <- count_data$Geneid
count_data <- count_data[, -1, drop = FALSE]
colnames(count_data) <- gsub("_Aligned.sortedByCoord.out.bam", "", basename(colnames(count_data)))
count_data <- count_data[, rownames(sample_info)]
```

Salmon + tximport 路线：

```r
dds <- DESeqDataSetFromTximport(
  txi,
  colData = sample_info,
  design = ~ condition
)
```

featureCounts 路线：

```r
dds <- DESeqDataSetFromMatrix(
  countData = round(as.matrix(count_data)),
  colData = sample_info,
  design = ~ condition
)
```

### 2. 低表达过滤

```r
keep <- rowSums(counts(dds) >= 10) >= 3
dds <- dds[keep, ]
```

过滤原则：

- 至少在一个组的多数样本中有一定表达。
- 不要保留大量全零或极低表达基因，否则会降低多重检验效率。
- 阈值要结合样本数调整，例如每组 3 个重复可用 `>=10` 且至少 3 个样本。

### 3. 样本 QC

```r
vsd <- vst(dds, blind = FALSE)

pca_data <- plotPCA(vsd, intgroup = c("condition"), returnData = TRUE)
percent_var <- round(100 * attr(pca_data, "percentVar"))

p_pca <- ggplot(pca_data, aes(PC1, PC2, color = condition, label = name)) +
  geom_point(size = 4) +
  geom_text_repel(max.overlaps = 20) +
  xlab(paste0("PC1: ", percent_var[1], "% variance")) +
  ylab(paste0("PC2: ", percent_var[2], "% variance")) +
  theme_bw()

ggsave("07_deseq2/plots/PCA_samples.pdf", p_pca, width = 7, height = 5)
```

样本距离热图：

```r
sample_dist <- dist(t(assay(vsd)))
sample_dist_matrix <- as.matrix(sample_dist)

pheatmap(
  sample_dist_matrix,
  annotation_col = sample_info,
  filename = "07_deseq2/plots/sample_distance_heatmap.pdf",
  width = 7,
  height = 6
)
```

### 4. 差异检验

```r
dds <- DESeq(dds)

contrast_info <- read.csv("00_metadata/contrasts.csv")
dir.create("07_deseq2/tables", showWarnings = FALSE, recursive = TRUE)
dir.create("07_deseq2/plots", showWarnings = FALSE, recursive = TRUE)

results_list <- list()

for (i in seq_len(nrow(contrast_info))) {
  contrast_name <- contrast_info$contrast_name[i]
  numerator <- contrast_info$numerator[i]
  denominator <- contrast_info$denominator[i]

  res <- results(
    dds,
    contrast = c("condition", numerator, denominator),
    alpha = 0.05
  )

  res_shrink <- lfcShrink(
    dds,
    contrast = c("condition", numerator, denominator),
    res = res,
    type = "ashr"
  )

  res_df <- as.data.frame(res_shrink) |>
    tibble::rownames_to_column("gene_id") |>
    arrange(padj)

  res_df <- res_df |>
    mutate(
      regulation = case_when(
        padj < 0.05 & log2FoldChange >= 1 ~ "Up",
        padj < 0.05 & log2FoldChange <= -1 ~ "Down",
        TRUE ~ "Not significant"
      )
    )

  write.csv(
    res_df,
    file.path("07_deseq2/tables", paste0(contrast_name, "_DESeq2_all.csv")),
    row.names = FALSE
  )

  sig_df <- res_df |>
    filter(padj < 0.05, abs(log2FoldChange) >= 1)

  write.csv(
    sig_df,
    file.path("07_deseq2/tables", paste0(contrast_name, "_DESeq2_significant.csv")),
    row.names = FALSE
  )

  results_list[[contrast_name]] <- res_df
}
```

### 5. 火山图

```r
plot_volcano <- function(res_df, contrast_name) {
  plot_df <- res_df |>
    mutate(
      neg_log10_padj = -log10(ifelse(is.na(padj), 1, padj)),
      label = ifelse(padj < 0.05 & abs(log2FoldChange) >= 1, gene_id, NA)
    )

  top_label <- plot_df |>
    filter(!is.na(label)) |>
    arrange(padj) |>
    head(20)

  ggplot(plot_df, aes(log2FoldChange, neg_log10_padj, color = regulation)) +
    geom_point(alpha = 0.7, size = 1.4) +
    geom_vline(xintercept = c(-1, 1), linetype = "dashed", color = "grey50") +
    geom_hline(yintercept = -log10(0.05), linetype = "dashed", color = "grey50") +
    geom_text_repel(data = top_label, aes(label = label), size = 3, max.overlaps = 20) +
    scale_color_manual(values = c("Up" = "#d73027", "Down" = "#4575b4", "Not significant" = "#bdbdbd")) +
    theme_bw() +
    labs(title = contrast_name, x = "log2 fold change", y = "-log10 adjusted P")
}

for (contrast_name in names(results_list)) {
  p <- plot_volcano(results_list[[contrast_name]], contrast_name)
  ggsave(file.path("07_deseq2/plots", paste0(contrast_name, "_volcano.pdf")), p, width = 7, height = 6)
}
```

### 6. DEG 热图

```r
for (contrast_name in names(results_list)) {
  top_genes <- results_list[[contrast_name]] |>
    filter(padj < 0.05, abs(log2FoldChange) >= 1) |>
    arrange(padj) |>
    head(50) |>
    pull(gene_id)

  if (length(top_genes) >= 2) {
    mat <- assay(vsd)[top_genes, ]
    mat <- mat - rowMeans(mat)

    pheatmap(
      mat,
      annotation_col = sample_info,
      show_rownames = TRUE,
      filename = file.path("07_deseq2/plots", paste0(contrast_name, "_top50_heatmap.pdf")),
      width = 8,
      height = 10
    )
  }
}
```

## 十一、TPM 与表达矩阵交付

DESeq2 差异分析使用 raw count，但报告中常需要 TPM 方便展示表达量。

TPM 计算需要基因长度：

```r
counts_to_tpm <- function(counts, gene_length_bp) {
  rate <- counts / (gene_length_bp / 1000)
  t(t(rate) / colSums(rate) * 1e6)
}

gene_length <- read.delim("ref/gene_length.tsv")
gene_length <- gene_length[match(rownames(count_data), gene_length$gene_id), ]

tpm <- counts_to_tpm(as.matrix(count_data), gene_length$length)
write.csv(tpm, "06_counts/gene_tpm.csv")
```

注意：

- TPM 适合样本内和展示层面的表达量解释。
- DESeq2/edgeR/limma-voom 的差异检验应使用 count 或模型要求的输入。

## 十二、基因注释与 ID 转换

```r
library(AnnotationDbi)
library(org.Hs.eg.db)

annotate_genes <- function(res_df) {
  res_df$symbol <- mapIds(
    org.Hs.eg.db,
    keys = res_df$gene_id,
    column = "SYMBOL",
    keytype = "ENSEMBL",
    multiVals = "first"
  )

  res_df$entrez <- mapIds(
    org.Hs.eg.db,
    keys = res_df$gene_id,
    column = "ENTREZID",
    keytype = "ENSEMBL",
    multiVals = "first"
  )

  res_df
}
```

非人类物种需要替换对应 OrgDb，或使用自定义 GTF 注释表。

## 十三、GO/KEGG/GSEA 富集分析

### 1. ORA 富集

```r
library(clusterProfiler)
library(org.Hs.eg.db)

sig_genes <- results_list$Treat_vs_Ctrl |>
  filter(padj < 0.05, abs(log2FoldChange) >= 1) |>
  pull(gene_id)

sig_entrez <- mapIds(
  org.Hs.eg.db,
  keys = sig_genes,
  column = "ENTREZID",
  keytype = "ENSEMBL",
  multiVals = "first"
) |>
  na.omit()

ego <- enrichGO(
  gene = sig_entrez,
  OrgDb = org.Hs.eg.db,
  keyType = "ENTREZID",
  ont = "BP",
  pAdjustMethod = "BH",
  pvalueCutoff = 0.05,
  qvalueCutoff = 0.2
)

write.csv(as.data.frame(ego), "08_enrichment/Treat_vs_Ctrl_GO_BP.csv", row.names = FALSE)
```

### 2. GSEA

GSEA 使用全基因排序，不只依赖阈值筛出来的 DEG。

```r
res_df <- results_list$Treat_vs_Ctrl

gene_rank <- res_df$log2FoldChange
names(gene_rank) <- res_df$gene_id
gene_rank <- sort(gene_rank[!is.na(gene_rank)], decreasing = TRUE)

gsea_go <- gseGO(
  geneList = gene_rank,
  OrgDb = org.Hs.eg.db,
  keyType = "ENSEMBL",
  ont = "BP",
  minGSSize = 10,
  maxGSSize = 500,
  pvalueCutoff = 0.05
)
```

## 十四、结果解释原则

| 结果 | 解读建议 |
| --- | --- |
| `log2FoldChange` | 正值表示 numerator 组更高，负值表示 denominator 组更高 |
| `pvalue` | 原始显著性，不建议作为最终筛选标准 |
| `padj` | BH 多重检验校正后的 FDR，常用阈值 `< 0.05` |
| `baseMean` | 平均表达强度，极低表达基因的 fold change 要谨慎解释 |
| `lfcShrink` | 收缩低表达和高噪声基因的 log2FC，适合排序和可视化 |

常用 DEG 阈值：

```text
padj < 0.05
abs(log2FoldChange) >= 1
baseMean >= 10
```

不要只看差异倍数，也要结合表达量、重复一致性、功能背景和实验设计。

## 十五、常见问题与排查

| 问题 | 可能原因 | 处理建议 |
| --- | --- | --- |
| PCA 按批次分开 | 建库/测序批次效应 | 设计公式加入 batch，必要时做批次评估 |
| 某个样本远离同组 | 样本污染、标签错误、低质量 | 回看 FastQC、mapping rate、样本相关性 |
| DEG 数量极少 | 效应弱、重复少、批次噪声大 | 检查设计和统计功效，不要强行放宽阈值 |
| DEG 数量异常多 | 批次混杂、样本组差异过大、污染 | 检查 PCA 和样本信息 |
| 富集结果不稳定 | DEG 太少或 ID 转换损失严重 | 改用 GSEA 或检查注释版本 |
| TPM 与 DESeq2 结果不一致 | 输入尺度不同 | DESeq2 以 count 建模，TPM 用于展示 |

## 十六、主要交付物

- `multiqc_report.html`
- clean FASTQ 质控报告
- STAR BAM、mapping summary 或 Salmon `quant.sf`
- gene raw count matrix
- TPM matrix
- DESeq2 normalized count
- PCA plot
- sample distance heatmap
- 每个比较组的完整差异表
- 每个比较组的显著 DEG 表
- volcano plot
- top DEG heatmap
- GO/KEGG/GSEA 富集结果
- 可复用 R 脚本和最终分析报告

## 十七、参考资料

- DESeq2 官方 vignette：差异表达建模、size factor、dispersion、Wald test、LFC shrinkage。
- Bioconductor RNA-seq workflow：从 reads 到基因层统计分析的标准实践。
- STAR manual：剪接感知 RNA-seq 比对和 GeneCounts 输出。
- Subread featureCounts 文档：基因/外显子 read summarization。
- MultiQC 文档：多样本质控报告汇总。
""",
        },
        {
            "title": "可变剪接分析 rMATS/SUPPA2",
            "description": "面向 bulk RNA-seq 的可变剪接增强流程，覆盖实验设计、剪接事件类型、STAR 比对、rMATS 事件检测、SUPPA2 PSI/dPSI 分析、可视化和候选事件解释。",
            "omics_type": "RNA-Seq",
            "dag_json": {
                "nodes": [
                    {"id": "design", "label": "实验设计与分组文件"},
                    {"id": "qc", "label": "FASTQ 质控与清洗"},
                    {"id": "star", "label": "STAR 剪接感知比对"},
                    {"id": "bam_qc", "label": "BAM 与 junction QC"},
                    {"id": "rmats", "label": "rMATS 事件级差异剪接"},
                    {"id": "salmon", "label": "Salmon 转录本定量"},
                    {"id": "suppa", "label": "SUPPA2 PSI/dPSI 分析"},
                    {"id": "filter", "label": "事件过滤与交叉验证"},
                    {"id": "visual", "label": "Sashimi/PSI/火山图"},
                    {"id": "report", "label": "候选事件报告"},
                ],
                "edges": [
                    {"source": "design", "target": "qc"},
                    {"source": "qc", "target": "star"},
                    {"source": "star", "target": "bam_qc"},
                    {"source": "bam_qc", "target": "rmats"},
                    {"source": "qc", "target": "salmon"},
                    {"source": "salmon", "target": "suppa"},
                    {"source": "rmats", "target": "filter"},
                    {"source": "suppa", "target": "filter"},
                    {"source": "filter", "target": "visual"},
                    {"source": "visual", "target": "report"},
                ],
            },
            "content": """# 可变剪接分析 rMATS/SUPPA2

## 一、适用场景

可变剪接分析关注同一个基因在不同条件下是否使用了不同的外显子、剪接位点或转录本结构。它回答的问题不是“基因整体表达是否上调/下调”，而是“基因内部 isoform 使用比例是否改变”。

适用于：

- 处理组 vs 对照组的外显子跳跃、内含子滞留、可变 5'/3' 剪接位点分析。
- 疾病、突变体、胁迫处理、发育阶段中的 splicing regulation 研究。
- RNA-binding protein 敲除/过表达后的剪接调控事件发现。
- 与差异表达、转录因子、RBP motif、蛋白结构域变化联合解释。

前提建议：

- 每组至少 3 个生物学重复。
- 优先使用 paired-end RNA-seq。
- reads 长度建议 100 bp 或以上，越长越利于跨 junction 事件识别。
- rMATS 路线需要高质量 BAM；SUPPA2 路线需要可靠转录本注释和表达定量。

## 二、可变剪接事件类型

| 事件类型 | 英文缩写 | 生物学含义 | rMATS 输出 |
| --- | --- | --- | --- |
| 外显子跳跃 | SE | 一个 cassette exon 在两组间 inclusion 水平改变 | `SE.MATS.JC.txt` |
| 可变 5' 剪接位点 | A5SS | 使用不同 5' splice site | `A5SS.MATS.JC.txt` |
| 可变 3' 剪接位点 | A3SS | 使用不同 3' splice site | `A3SS.MATS.JC.txt` |
| 互斥外显子 | MXE | 两个外显子互斥使用 | `MXE.MATS.JC.txt` |
| 内含子滞留 | RI | intron 在成熟 RNA 中保留 | `RI.MATS.JC.txt` |
| 转录本 isoform 切换 | ISO | 主导转录本比例改变 | SUPPA2 transcript-level PSI |

## 三、最佳实践路线

建议同时准备两条互补路线：

1. `STAR + rMATS`：以 junction reads 和 exon body reads 为核心，适合标准事件级差异剪接。
2. `Salmon + SUPPA2`：以 transcript abundance 和注释事件为核心，适合快速计算 PSI 和 dPSI，也适合 isoform-level 解释。

两者互补：

| 工具 | 输入 | 优势 | 注意点 |
| --- | --- | --- | --- |
| rMATS | sorted BAM 或 FASTQ + GTF | 事件类型清晰，输出 inclusion level 和 FDR | 依赖 junction 支持，BAM 和 read length 要准确 |
| SUPPA2 | GTF + transcript TPM | 快速、适合多样本 PSI/dPSI 和 transcript-level 分析 | 依赖转录本注释和定量准确性 |

## 四、整体流程图

```mermaid
flowchart TD
    A[样本设计与分组] --> B[FASTQ 质控与清洗]
    B --> C[STAR two-pass 或剪接感知比对]
    C --> D[BAM sort/index 与 junction QC]
    D --> E[rMATS 检测 SE/A5SS/A3SS/MXE/RI]
    B --> F[Salmon 转录本定量]
    F --> G[SUPPA2 generateEvents]
    G --> H[SUPPA2 psiPerEvent]
    H --> I[SUPPA2 diffSplice]
    E --> J[显著事件过滤]
    I --> J
    J --> K[Sashimi plot / PSI 箱线图 / dPSI 火山图]
    K --> L[候选基因与事件报告]
```

## 五、项目目录建议

```text
alternative_splicing_project/
├── 00_metadata/
│   ├── sample_info.csv
│   ├── group1_bams.txt
│   └── group2_bams.txt
├── 01_raw_data/
├── 02_clean_data/
├── 03_star/
│   ├── bam/
│   └── logs/
├── 04_rmats/
│   ├── output/
│   └── tmp/
├── 05_salmon/
├── 06_suppa2/
│   ├── events/
│   ├── psi/
│   └── diff/
├── 07_visualization/
└── report/
```

`sample_info.csv` 示例：

| sample_id | group | batch | read1 | read2 |
| --- | --- | --- | --- | --- |
| Ctrl_1 | Ctrl | B1 | Ctrl_1_R1.fq.gz | Ctrl_1_R2.fq.gz |
| Ctrl_2 | Ctrl | B1 | Ctrl_2_R1.fq.gz | Ctrl_2_R2.fq.gz |
| Treat_1 | Treat | B1 | Treat_1_R1.fq.gz | Treat_1_R2.fq.gz |
| Treat_2 | Treat | B1 | Treat_2_R1.fq.gz | Treat_2_R2.fq.gz |

## 六、FASTQ 质控与清洗

```bash
mkdir -p 02_qc_raw/fastqc 02_qc_raw/multiqc

fastqc -t 8 \
  -o 02_qc_raw/fastqc \
  01_raw_data/*.fq.gz

multiqc 02_qc_raw/fastqc \
  -o 02_qc_raw/multiqc
```

```bash
mkdir -p 02_clean_data 02_qc_clean/fastp

for sample in Ctrl_1 Ctrl_2 Ctrl_3 Treat_1 Treat_2 Treat_3
do
  fastp \
    -i 01_raw_data/${sample}_R1.fq.gz \
    -I 01_raw_data/${sample}_R2.fq.gz \
    -o 02_clean_data/${sample}_R1.clean.fq.gz \
    -O 02_clean_data/${sample}_R2.clean.fq.gz \
    --detect_adapter_for_pe \
    --length_required 30 \
    --thread 8 \
    --html 02_qc_clean/fastp/${sample}.html \
    --json 02_qc_clean/fastp/${sample}.json
done
```

质控重点：

- 每个样本总 reads 数是否接近。
- 接头污染是否明显。
- GC 分布是否异常。
- paired-end 两端质量是否一致。
- 可变剪接项目要特别关注 read length，因为 junction-spanning reads 对事件识别很关键。

## 七、STAR 剪接感知比对

### 1. 构建索引

```bash
mkdir -p 03_star/index

STAR \
  --runThreadN 16 \
  --runMode genomeGenerate \
  --genomeDir 03_star/index \
  --genomeFastaFiles ref/genome.fa \
  --sjdbGTFfile ref/genes.gtf \
  --sjdbOverhang 149
```

`sjdbOverhang` 通常设置为 read length - 1，例如 PE150 设置为 149。

### 2. 比对并输出 sorted BAM

```bash
mkdir -p 03_star/bam 03_star/logs

for sample in Ctrl_1 Ctrl_2 Ctrl_3 Treat_1 Treat_2 Treat_3
do
  STAR \
    --runThreadN 16 \
    --genomeDir 03_star/index \
    --readFilesIn \
      02_clean_data/${sample}_R1.clean.fq.gz \
      02_clean_data/${sample}_R2.clean.fq.gz \
    --readFilesCommand zcat \
    --outFileNamePrefix 03_star/bam/${sample}_ \
    --outSAMtype BAM SortedByCoordinate \
    --outSAMstrandField intronMotif \
    --twopassMode Basic

  samtools index 03_star/bam/${sample}_Aligned.sortedByCoord.out.bam
done
```

建议：

- rMATS 可从 BAM 输入，BAM 应统一使用同一参考基因组和同一 GTF。
- 如果后续使用 IGV/Sashimi plot，保留 indexed BAM 很重要。
- `--twopassMode Basic` 有助于发现 novel junction，但项目中要记录是否开启，保证批次一致。

## 八、rMATS 差异剪接分析

### 1. 准备 BAM 分组文件

rMATS 的 `--b1` 和 `--b2` 接收逗号分隔的 BAM 路径。

```bash
ls 03_star/bam/Ctrl_*_Aligned.sortedByCoord.out.bam | paste -sd, - > 00_metadata/group1_bams.txt
ls 03_star/bam/Treat_*_Aligned.sortedByCoord.out.bam | paste -sd, - > 00_metadata/group2_bams.txt
```

文件内容示例：

```text
03_star/bam/Ctrl_1_Aligned.sortedByCoord.out.bam,03_star/bam/Ctrl_2_Aligned.sortedByCoord.out.bam,03_star/bam/Ctrl_3_Aligned.sortedByCoord.out.bam
```

### 2. 运行 rMATS

```bash
mkdir -p 04_rmats/output 04_rmats/tmp

python rmats.py \
  --b1 00_metadata/group1_bams.txt \
  --b2 00_metadata/group2_bams.txt \
  --gtf ref/genes.gtf \
  --od 04_rmats/output \
  --tmp 04_rmats/tmp \
  -t paired \
  --readLength 150 \
  --nthread 12 \
  --libType fr-unstranded
```

关键参数：

| 参数 | 含义 |
| --- | --- |
| `--b1` / `--b2` | 两个比较组的 BAM 列表 |
| `--gtf` | 注释文件，必须与比对参考版本一致 |
| `-t paired` | paired-end 数据；单端数据用 `single` |
| `--readLength` | read 长度，必须按实际数据填写 |
| `--libType` | 文库链特异性，如 `fr-unstranded`、`fr-firststrand`、`fr-secondstrand` |
| `--od` | 结果输出目录 |
| `--tmp` | 临时目录 |

### 3. rMATS 输出解读

常见结果文件：

| 文件 | 说明 |
| --- | --- |
| `SE.MATS.JC.txt` | exon skipping 事件，仅 junction counts |
| `SE.MATS.JCEC.txt` | exon skipping 事件，junction + exon counts |
| `A5SS.MATS.JC.txt` | alternative 5' splice site |
| `A3SS.MATS.JC.txt` | alternative 3' splice site |
| `MXE.MATS.JC.txt` | mutually exclusive exons |
| `RI.MATS.JC.txt` | retained intron |

重要字段：

| 字段 | 解释 |
| --- | --- |
| `IncLevel1` | group1 每个样本的 inclusion level |
| `IncLevel2` | group2 每个样本的 inclusion level |
| `IncLevelDifference` | group1 - group2 的 PSI 差异 |
| `PValue` | 原始 P 值 |
| `FDR` | 多重检验校正后的显著性 |
| `IJC_SAMPLE_1/2` | inclusion junction counts |
| `SJC_SAMPLE_1/2` | skipping junction counts |

## 九、rMATS 事件过滤与汇总

```python
import pandas as pd
from pathlib import Path

event_types = ["SE", "A5SS", "A3SS", "MXE", "RI"]
out_dir = Path("04_rmats/output")
summary = []

for event in event_types:
    path = out_dir / f"{event}.MATS.JC.txt"
    df = pd.read_csv(path, sep="\t")
    df["event_type"] = event

    sig = df[
        (df["FDR"] < 0.05)
        & (df["IncLevelDifference"].abs() >= 0.1)
    ].copy()

    sig.to_csv(out_dir / f"{event}.significant.tsv", sep="\t", index=False)

    summary.append({
        "event_type": event,
        "total_events": len(df),
        "significant_events": len(sig),
        "up_in_group1": (sig["IncLevelDifference"] > 0).sum(),
        "up_in_group2": (sig["IncLevelDifference"] < 0).sum(),
    })

pd.DataFrame(summary).to_csv(out_dir / "rmats_event_summary.tsv", sep="\t", index=False)
```

推荐阈值：

```text
FDR < 0.05
abs(IncLevelDifference) >= 0.1
mean junction count >= 10
```

`IncLevelDifference` 的方向要小心：

- rMATS 中通常是 `group1 - group2`。
- 如果 `--b1` 是 Ctrl，`--b2` 是 Treat，则正值表示 Ctrl inclusion 更高。
- 报告中必须写清楚方向。

## 十、SUPPA2 分析路线

SUPPA2 适合从 GTF 生成事件，再基于 transcript TPM 计算 PSI 和 differential splicing。

### 1. Salmon 转录本定量

```bash
mkdir -p 05_salmon ref/salmon_index

salmon index \
  -t ref/transcripts.fa \
  -i ref/salmon_index \
  -p 12

for sample in Ctrl_1 Ctrl_2 Ctrl_3 Treat_1 Treat_2 Treat_3
do
  salmon quant \
    -i ref/salmon_index \
    -l A \
    -1 02_clean_data/${sample}_R1.clean.fq.gz \
    -2 02_clean_data/${sample}_R2.clean.fq.gz \
    --validateMappings \
    --gcBias \
    --seqBias \
    -p 12 \
    -o 05_salmon/${sample}
done
```

### 2. 生成 transcript TPM 矩阵

```python
import pandas as pd
from pathlib import Path

samples = ["Ctrl_1", "Ctrl_2", "Ctrl_3", "Treat_1", "Treat_2", "Treat_3"]
tpm_tables = []

for sample in samples:
    quant = pd.read_csv(Path("05_salmon") / sample / "quant.sf", sep="\t")
    tpm = quant[["Name", "TPM"]].rename(columns={"TPM": sample})
    tpm_tables.append(tpm)

expr = tpm_tables[0]
for tpm in tpm_tables[1:]:
    expr = expr.merge(tpm, on="Name", how="outer")

expr = expr.fillna(0)
expr.to_csv("06_suppa2/transcript_tpm.tsv", sep="\t", index=False)
```

SUPPA2 表达矩阵第一列通常是 transcript ID，后面是样本 TPM。

### 3. 生成剪接事件

```bash
mkdir -p 06_suppa2/events

python suppa.py generateEvents \
  -i ref/genes.gtf \
  -o 06_suppa2/events/annotation \
  -e SE SS MX RI FL \
  -f ioe
```

常见事件：

| SUPPA2 类型 | 含义 |
| --- | --- |
| `SE` | skipped exon |
| `SS` | alternative splice site |
| `MX` | mutually exclusive exon |
| `RI` | retained intron |
| `FL` | alternative first/last exon |

### 4. 计算 PSI

```bash
mkdir -p 06_suppa2/psi

for event_file in 06_suppa2/events/*.ioe
do
  base=$(basename ${event_file} .ioe)

  python suppa.py psiPerEvent \
    -i ${event_file} \
    -e 06_suppa2/transcript_tpm.tsv \
    -o 06_suppa2/psi/${base}
done
```

### 5. 差异剪接分析

准备分组表达矩阵：

```python
import pandas as pd

expr = pd.read_csv("06_suppa2/transcript_tpm.tsv", sep="\t")

ctrl_cols = ["Name", "Ctrl_1", "Ctrl_2", "Ctrl_3"]
treat_cols = ["Name", "Treat_1", "Treat_2", "Treat_3"]

expr[ctrl_cols].to_csv("06_suppa2/ctrl_tpm.tsv", sep="\t", index=False)
expr[treat_cols].to_csv("06_suppa2/treat_tpm.tsv", sep="\t", index=False)
```

运行 `diffSplice`：

```bash
mkdir -p 06_suppa2/diff

python suppa.py diffSplice \
  -m empirical \
  -gc \
  -i 06_suppa2/events/annotation_SE_strict.ioe \
  -p 06_suppa2/psi/annotation_SE_strict.psi \
  -e 06_suppa2/ctrl_tpm.tsv 06_suppa2/treat_tpm.tsv \
  -o 06_suppa2/diff/SE_Ctrl_vs_Treat
```

## 十一、rMATS 与 SUPPA2 结果整合

整合思路：

| 层级 | rMATS | SUPPA2 |
| --- | --- | --- |
| 事件坐标 | 明确 genomic coordinate | 基于 transcript event |
| 显著性 | FDR | p-value / empirical model |
| 效应量 | IncLevelDifference | dPSI |
| 可视化 | Sashimi plot | PSI distribution |

优先级建议：

1. rMATS 中 `FDR < 0.05` 且 `abs(IncLevelDifference) >= 0.1` 的事件。
2. SUPPA2 中 `abs(dPSI) >= 0.1` 且显著的事件。
3. 两个工具方向一致的事件作为高置信候选。
4. 与差异表达、RBP motif、功能结构域相关的事件优先解释。

## 十二、可视化

### 1. dPSI 火山图

```r
library(tidyverse)
library(ggrepel)

se <- read.delim("04_rmats/output/SE.MATS.JC.txt")

plot_df <- se |>
  mutate(
    neg_log10_fdr = -log10(ifelse(FDR == 0, 1e-300, FDR)),
    regulation = case_when(
      FDR < 0.05 & IncLevelDifference >= 0.1 ~ "Higher inclusion in group1",
      FDR < 0.05 & IncLevelDifference <= -0.1 ~ "Higher inclusion in group2",
      TRUE ~ "Not significant"
    )
  )

ggplot(plot_df, aes(IncLevelDifference, neg_log10_fdr, color = regulation)) +
  geom_point(alpha = 0.7, size = 1.4) +
  geom_vline(xintercept = c(-0.1, 0.1), linetype = "dashed") +
  geom_hline(yintercept = -log10(0.05), linetype = "dashed") +
  theme_bw() +
  labs(x = "ΔPSI / IncLevelDifference", y = "-log10(FDR)")
```

### 2. PSI 箱线图

```r
library(tidyverse)

event_id <- 1
inc1 <- strsplit(se$IncLevel1[event_id], ",")[[1]] |> as.numeric()
inc2 <- strsplit(se$IncLevel2[event_id], ",")[[1]] |> as.numeric()

psi_df <- tibble(
  group = c(rep("Ctrl", length(inc1)), rep("Treat", length(inc2))),
  psi = c(inc1, inc2)
)

ggplot(psi_df, aes(group, psi, fill = group)) +
  geom_boxplot(width = 0.5, outlier.shape = NA) +
  geom_jitter(width = 0.08, size = 2) +
  theme_bw() +
  labs(y = "PSI", x = NULL)
```

### 3. Sashimi plot

推荐使用 IGV、rmats2sashimiplot 或 ggsashimi 对候选事件画 junction 支持图。

```bash
rmats2sashimiplot \
  --b1 00_metadata/group1_bams.txt \
  --b2 00_metadata/group2_bams.txt \
  -t SE \
  -e 04_rmats/output/SE.MATS.JC.txt \
  --l1 Ctrl \
  --l2 Treat \
  --exon_s 1 \
  --intron_s 5 \
  -o 07_visualization/sashimi_SE
```

## 十三、结果解释原则

| 指标 | 推荐解释 |
| --- | --- |
| `FDR` | 差异剪接显著性，常用 `< 0.05` |
| `IncLevelDifference` | PSI 差异，常用 `abs >= 0.1` |
| junction counts | 支撑事件的 reads 数，太低不可靠 |
| 事件类型 | SE、RI、A5SS 等类型的生物学意义不同 |
| 基因表达量 | 低表达基因的剪接事件要谨慎 |

注意：

- 可变剪接事件不一定伴随基因总表达变化。
- 需要区分“gene-level DEG”和“isoform/splicing-level change”。
- 报告中必须写清楚比较方向，例如 `Ctrl - Treat` 还是 `Treat - Ctrl`。
- 候选事件最好用 Sashimi plot 或 RT-PCR 进一步验证。

## 十四、常见问题与排查

| 问题 | 可能原因 | 处理建议 |
| --- | --- | --- |
| 显著事件很少 | reads 深度不足、重复少、剪接变化弱 | 检查 junction reads、降低解释预期 |
| RI 事件异常多 | intronic reads、pre-mRNA、rRNA 或比对问题 | 检查文库类型和 intronic mapping |
| 两组方向解释反了 | `--b1` / `--b2` 顺序混淆 | 在报告中固定方向并记录 |
| SUPPA2 与 rMATS 不一致 | 事件定义和输入层级不同 | 优先看高 read support 事件 |
| Sashimi plot 不支持结果 | BAM 未 index 或坐标版本不一致 | 检查 BAM bai、GTF 和参考版本 |
| FDR 显著但 PSI 很小 | 大样本下微弱变化显著 | 加入 `abs(dPSI)` 阈值 |

## 十五、主要交付物

- FASTQ/MultiQC 质控报告
- STAR sorted BAM 和 BAM index
- STAR junction/mapping summary
- rMATS 五类事件结果表
- rMATS significant event tables
- Salmon transcript TPM matrix
- SUPPA2 event annotation、PSI、dPSI 结果
- dPSI 火山图
- PSI 箱线图
- 候选事件 Sashimi plots
- 高置信差异剪接事件清单
- 与 DEG/功能注释联动的解释报告

## 十六、参考资料

- rMATS-turbo 官方仓库：提供 rMATS 构建、运行参数、输入输出和事件类型说明。
- SUPPA/SUPPA2 官方仓库与教程：提供 `generateEvents`、`psiPerEvent`、`diffSplice` 等命令说明。
- STAR 官方手册：用于 RNA-seq 剪接感知比对和 junction 支持。
- Salmon 官方文档：用于 transcript-level quantification。
""",
        },
        {
            "title": "WGCNA 共表达网络分析",
            "description": "面向 bulk RNA-seq 表达矩阵的 WGCNA 共表达网络流程，覆盖表达矩阵预处理、软阈值选择、模块识别、模块-性状相关、hub gene 挖掘、富集分析与可视化解释。",
            "omics_type": "RNA-Seq",
            "dag_json": {
                "nodes": [
                    {"id": "input", "label": "表达矩阵与性状表"},
                    {"id": "normalize", "label": "VST/TPM/log2 转换"},
                    {"id": "filter", "label": "低表达与低变异过滤"},
                    {"id": "outlier", "label": "样本聚类与离群检测"},
                    {"id": "soft_power", "label": "软阈值选择"},
                    {"id": "network", "label": "网络构建与 TOM"},
                    {"id": "modules", "label": "模块识别与合并"},
                    {"id": "trait", "label": "模块-性状相关"},
                    {"id": "hub", "label": "hub gene 筛选"},
                    {"id": "enrichment", "label": "富集与网络可视化"},
                ],
                "edges": [
                    {"source": "input", "target": "normalize"},
                    {"source": "normalize", "target": "filter"},
                    {"source": "filter", "target": "outlier"},
                    {"source": "outlier", "target": "soft_power"},
                    {"source": "soft_power", "target": "network"},
                    {"source": "network", "target": "modules"},
                    {"source": "modules", "target": "trait"},
                    {"source": "trait", "target": "hub"},
                    {"source": "hub", "target": "enrichment"},
                ],
            },
            "content": """# WGCNA 共表达网络分析

## 一、适用场景

WGCNA，全称 Weighted Gene Co-expression Network Analysis，是一种基于基因表达相关性构建加权共表达网络的方法。它的核心思想是：如果一批基因在多个样本中的表达模式高度一致，那么这些基因可能受到共同调控，或者参与同一类生物过程。

适用于：

- bulk RNA-seq、microarray、蛋白组、代谢组等连续表达矩阵。
- 寻找与表型、处理、时间、病理指标或生理指标相关的基因模块。
- 从大量表达基因中筛选模块 hub genes。
- 将差异表达分析从“单基因列表”扩展到“基因网络模块”层面。
- 多时间点、多组织、多处理组项目中的表达模式归纳。

不适合直接套用：

- 样本数过少。WGCNA 对样本数敏感，推荐至少 15 个样本，较稳定的网络通常需要 20-30 个以上样本。
- 没有连续表达变化或样本差异很小的项目。
- 只想做两组差异表达时，DESeq2/edgeR 更直接。
- 原始 count 未经过方差稳定转换时，不建议直接输入 WGCNA。

## 二、WGCNA 能回答什么问题

| 问题 | WGCNA 输出 | 怎么解释 |
| --- | --- | --- |
| 哪些基因表达模式相似？ | co-expression modules | 同一模块内基因具有相似表达趋势 |
| 哪些模块和性状最相关？ | module-trait correlation heatmap | 相关系数越高，模块越可能与性状相关 |
| 模块里的代表表达趋势是什么？ | module eigengene, ME | 可以理解为该模块的第一主成分 |
| 模块里最核心的基因是谁？ | hub genes | 模块内连接度高，且与性状相关的基因 |
| 模块代表什么生物功能？ | GO/KEGG/GSEA enrichment | 解释模块背后的通路和过程 |

## 三、关键概念图例

| 概念 | 类比 | 生信含义 |
| --- | --- | --- |
| Gene | 网络节点 | 一个基因 |
| Edge | 连线 | 两个基因表达相关 |
| Weight | 连线粗细 | 相关性强弱经过软阈值转换后的权重 |
| Module | 颜色社区 | 一组共表达基因，例如 turquoise、blue、brown |
| Module eigengene | 模块代表曲线 | 模块整体表达趋势 |
| Trait | 外部性状 | 处理组、表型值、时间点、临床指标 |
| Hub gene | 核心节点 | 模块内连接度高且与性状相关的候选关键基因 |

示意：

```text
Trait: drought severity
        |
        | corr = 0.82, p = 1e-05
        v
turquoise module eigengene
        |
        | high module membership
        v
Hub genes: NAC1, DREB2A, HSP70, ...
```

解释：如果 turquoise 模块和干旱程度高度正相关，且模块中的 `DREB2A` 同时具有较高 module membership 和 gene significance，那么它就是值得优先关注的候选 hub gene。

## 四、整体流程图

```mermaid
flowchart TD
    A[RNA-seq count / TPM matrix] --> B[VST / log2(TPM+1) 转换]
    B --> C[低表达和低变异基因过滤]
    C --> D[样本聚类检测离群样本]
    D --> E[选择 soft-threshold power]
    E --> F[构建 adjacency matrix]
    F --> G[计算 TOM similarity]
    G --> H[层次聚类识别 modules]
    H --> I[合并相似 modules]
    I --> J[计算 module eigengenes]
    J --> K[模块-性状相关热图]
    K --> L[筛选 hub genes]
    L --> M[GO/KEGG 富集和 Cytoscape 网络]
```

## 五、输入文件与目录建议

```text
wgcna_project/
├── 00_metadata/
│   └── traits.csv
├── 01_expression/
│   ├── raw_counts.csv
│   ├── vst_matrix.csv
│   └── filtered_expr.csv
├── 02_qc/
│   ├── sample_clustering.pdf
│   └── soft_power.pdf
├── 03_wgcna/
│   ├── network.RData
│   ├── module_genes.csv
│   ├── module_trait_correlation.csv
│   └── hub_genes.csv
├── 04_enrichment/
├── 05_cytoscape/
└── report/
```

表达矩阵格式：

| gene_id | Ctrl_1 | Ctrl_2 | Treat_1 | Treat_2 |
| --- | --- | --- | --- | --- |
| GeneA | 10.2 | 11.5 | 20.1 | 21.3 |
| GeneB | 3.2 | 2.9 | 1.1 | 1.4 |

WGCNA 的 R 输入通常要求：

```text
行 = 样本
列 = 基因
```

性状表 `traits.csv`：

| sample_id | condition | drought_score | biomass |
| --- | --- | --- | --- |
| Ctrl_1 | Ctrl | 0 | 12.3 |
| Ctrl_2 | Ctrl | 0 | 13.1 |
| Treat_1 | Treat | 8 | 6.5 |
| Treat_2 | Treat | 9 | 5.9 |

## 六、表达矩阵预处理

### 1. 从 DESeq2 count 生成 VST 矩阵

对于 RNA-seq raw count，推荐先用 DESeq2 做 VST 或 rlog 变换，让低表达和高表达基因的方差更稳定。

```r
library(DESeq2)
library(tidyverse)

count_data <- read.csv("01_expression/raw_counts.csv", row.names = 1, check.names = FALSE)
trait_data <- read.csv("00_metadata/traits.csv", row.names = 1)

count_data <- count_data[, rownames(trait_data)]

dds <- DESeqDataSetFromMatrix(
  countData = round(as.matrix(count_data)),
  colData = trait_data,
  design = ~ 1
)

keep <- rowSums(counts(dds) >= 10) >= 3
dds <- dds[keep, ]

vsd <- vst(dds, blind = TRUE)
vst_matrix <- assay(vsd)

write.csv(vst_matrix, "01_expression/vst_matrix.csv")
```

也可以使用 TPM：

```r
tpm <- read.csv("01_expression/tpm_matrix.csv", row.names = 1, check.names = FALSE)
log_tpm <- log2(tpm + 1)
write.csv(log_tpm, "01_expression/log2_tpm_matrix.csv")
```

建议：

- WGCNA 不建议直接输入 raw count。
- 如果是 DESeq2 流程，优先使用 `vst`。
- 如果只有 TPM/FPKM，可以使用 `log2(TPM + 1)`。
- 做 WGCNA 前应去掉低表达和低变异基因，减少噪音和计算量。

### 2. 过滤低变异基因

```r
expr <- read.csv("01_expression/vst_matrix.csv", row.names = 1, check.names = FALSE)

gene_mad <- apply(expr, 1, mad)
top_genes <- names(sort(gene_mad, decreasing = TRUE))[1:min(8000, length(gene_mad))]
expr_filtered <- expr[top_genes, ]

write.csv(expr_filtered, "01_expression/filtered_expr.csv")
```

常见策略：

| 策略 | 说明 |
| --- | --- |
| 保留 MAD 最高的 5000-10000 个基因 | 常用、稳定、适合样本数中等项目 |
| 保留表达量前 50% 的基因 | 简单但可能保留低变异 housekeeping genes |
| 保留差异基因再做 WGCNA | 可行但有偏，会只看差异相关网络 |

## 七、样本聚类与离群检测

WGCNA 对离群样本非常敏感，必须先做样本聚类。

```r
library(WGCNA)

options(stringsAsFactors = FALSE)
allowWGCNAThreads()

expr <- read.csv("01_expression/filtered_expr.csv", row.names = 1, check.names = FALSE)
datExpr <- as.data.frame(t(expr))

gsg <- goodSamplesGenes(datExpr, verbose = 3)
if (!gsg$allOK) {
  datExpr <- datExpr[gsg$goodSamples, gsg$goodGenes]
}

sample_tree <- hclust(dist(datExpr), method = "average")

pdf("02_qc/sample_clustering.pdf", width = 10, height = 6)
plot(sample_tree, main = "Sample clustering to detect outliers", sub = "", xlab = "")
dev.off()
```

如果某个样本明显远离所有同组样本，应回看：

- FastQC/MultiQC 质量。
- mapping rate。
- library size。
- 样本标签是否混淆。
- PCA 是否也显示离群。

不要因为结果“不好看”随意删除样本，必须有 QC 证据。

## 八、软阈值 soft-threshold power 选择

WGCNA 不用硬阈值把相关性切成 0/1，而是用软阈值把相关性转换为网络连接权重。

```r
powers <- c(1:10, seq(12, 30, by = 2))

sft <- pickSoftThreshold(
  datExpr,
  powerVector = powers,
  networkType = "signed",
  verbose = 5
)

pdf("02_qc/soft_power.pdf", width = 10, height = 5)
par(mfrow = c(1, 2))

plot(
  sft$fitIndices[, 1],
  -sign(sft$fitIndices[, 3]) * sft$fitIndices[, 2],
  xlab = "Soft Threshold power",
  ylab = "Scale Free Topology Model Fit, signed R^2",
  type = "n",
  main = "Scale independence"
)
text(
  sft$fitIndices[, 1],
  -sign(sft$fitIndices[, 3]) * sft$fitIndices[, 2],
  labels = powers,
  col = "red"
)
abline(h = 0.8, col = "red")

plot(
  sft$fitIndices[, 1],
  sft$fitIndices[, 5],
  xlab = "Soft Threshold power",
  ylab = "Mean connectivity",
  type = "n",
  main = "Mean connectivity"
)
text(sft$fitIndices[, 1], sft$fitIndices[, 5], labels = powers, col = "red")
dev.off()
```

选择原则：

| 指标 | 建议 |
| --- | --- |
| scale-free topology fit R² | 通常希望接近或超过 0.8 |
| mean connectivity | 不要过低，否则网络太稀疏 |
| signed network | 常用于保留正负相关方向，power 往往比 unsigned 更高 |
| 样本数较少 | 不要机械追求 R²，结合模块稳定性判断 |

示例解释：

```text
如果 power = 12 时 R² 达到 0.82，mean connectivity 仍然不低，
可以选择 softPower = 12。
如果 R² 一直达不到 0.8，选择曲线趋于平稳处，并在报告中说明。
```

## 九、构建网络和识别模块

### 1. 自动网络构建

```r
softPower <- 12

net <- blockwiseModules(
  datExpr,
  power = softPower,
  networkType = "signed",
  TOMType = "signed",
  minModuleSize = 30,
  reassignThreshold = 0,
  mergeCutHeight = 0.25,
  numericLabels = TRUE,
  pamRespectsDendro = FALSE,
  saveTOMs = TRUE,
  saveTOMFileBase = "03_wgcna/TOM",
  verbose = 3
)

moduleColors <- labels2colors(net$colors)
MEs <- net$MEs

save(datExpr, net, moduleColors, MEs, file = "03_wgcna/network.RData")
```

关键参数：

| 参数 | 说明 |
| --- | --- |
| `networkType = "signed"` | 保留正相关方向，更适合生物解释 |
| `TOMType = "signed"` | 基于 signed network 计算拓扑重叠 |
| `minModuleSize` | 最小模块大小，常用 30-50 |
| `mergeCutHeight` | 合并相似模块，0.25 表示 eigengene 相关性约 0.75 |
| `power` | 软阈值 |

### 2. 模块树图

```r
pdf("03_wgcna/gene_dendrogram_modules.pdf", width = 12, height = 6)
plotDendroAndColors(
  net$dendrograms[[1]],
  moduleColors[net$blockGenes[[1]]],
  "Module colors",
  dendroLabels = FALSE,
  hang = 0.03,
  addGuide = TRUE,
  guideHang = 0.05
)
dev.off()
```

图例解释：

```text
上方树状图：基因按照共表达相似性聚类。
下方颜色条：WGCNA 分配的模块颜色。
同一颜色中的基因表达模式更相似。
grey 模块通常表示未归入明确模块的基因。
```

## 十、模块-性状相关分析

### 1. 准备性状矩阵

```r
trait_data <- read.csv("00_metadata/traits.csv", row.names = 1)
trait_data <- trait_data[rownames(datExpr), ]

trait_data$condition_binary <- ifelse(trait_data$condition == "Treat", 1, 0)

numeric_traits <- trait_data |>
  dplyr::select(where(is.numeric))
```

### 2. 模块与性状相关热图

```r
MEs0 <- moduleEigengenes(datExpr, moduleColors)$eigengenes
MEs <- orderMEs(MEs0)

module_trait_cor <- cor(MEs, numeric_traits, use = "p")
module_trait_pvalue <- corPvalueStudent(module_trait_cor, nSamples = nrow(datExpr))

text_matrix <- paste(
  signif(module_trait_cor, 2),
  "\n(",
  signif(module_trait_pvalue, 1),
  ")",
  sep = ""
)
dim(text_matrix) <- dim(module_trait_cor)

pdf("03_wgcna/module_trait_heatmap.pdf", width = 9, height = 8)
labeledHeatmap(
  Matrix = module_trait_cor,
  xLabels = names(numeric_traits),
  yLabels = names(MEs),
  ySymbols = names(MEs),
  colorLabels = FALSE,
  colors = blueWhiteRed(50),
  textMatrix = text_matrix,
  setStdMargins = FALSE,
  cex.text = 0.8,
  zlim = c(-1, 1),
  main = "Module-trait relationships"
)
dev.off()

write.csv(module_trait_cor, "03_wgcna/module_trait_correlation.csv")
write.csv(module_trait_pvalue, "03_wgcna/module_trait_pvalue.csv")
```

热图读法：

| 示例 | 解释 |
| --- | --- |
| `MEturquoise` vs `drought_score`: `0.82 (1e-05)` | turquoise 模块和干旱程度显著正相关 |
| `MEblue` vs `biomass`: `-0.71 (0.002)` | blue 模块表达越高，biomass 越低 |
| `MEgrey` | 未归类基因模块，一般不作为重点解释 |

## 十一、筛选 hub genes

hub gene 通常同时满足：

1. 属于目标模块。
2. 与模块 eigengene 高相关，即 module membership 高。
3. 与目标性状高相关，即 gene significance 高。
4. 有合理生物学功能或文献支持。

```r
target_module <- "turquoise"
target_trait <- "drought_score"

module_genes <- moduleColors == target_module

MM <- as.data.frame(cor(datExpr, MEs, use = "p"))
MMPvalue <- as.data.frame(corPvalueStudent(as.matrix(MM), nrow(datExpr)))

GS <- as.data.frame(cor(datExpr, numeric_traits[[target_trait]], use = "p"))
GSPvalue <- as.data.frame(corPvalueStudent(as.matrix(GS), nrow(datExpr)))

gene_info <- data.frame(
  gene_id = colnames(datExpr),
  module = moduleColors,
  module_membership = MM[[paste0("ME", target_module)]],
  module_membership_pvalue = MMPvalue[[paste0("ME", target_module)]],
  gene_significance = GS[, 1],
  gene_significance_pvalue = GSPvalue[, 1]
)

hub_genes <- gene_info |>
  dplyr::filter(
    module == target_module,
    abs(module_membership) >= 0.8,
    abs(gene_significance) >= 0.5
  ) |>
  dplyr::arrange(desc(abs(module_membership)), desc(abs(gene_significance)))

write.csv(gene_info, "03_wgcna/all_gene_module_membership.csv", row.names = FALSE)
write.csv(hub_genes, "03_wgcna/hub_genes_turquoise.csv", row.names = FALSE)
```

### MM-GS 散点图

```r
library(ggplot2)
library(ggrepel)

plot_df <- gene_info |>
  dplyr::filter(module == target_module) |>
  dplyr::mutate(label = ifelse(row_number() <= 10, gene_id, NA))

ggplot(plot_df, aes(abs(module_membership), abs(gene_significance))) +
  geom_point(alpha = 0.7, color = target_module) +
  geom_text_repel(aes(label = label), max.overlaps = 20) +
  theme_bw() +
  labs(
    x = paste0("Module Membership in ", target_module),
    y = paste0("Gene Significance for ", target_trait),
    title = "Hub gene screening"
  )

ggsave("03_wgcna/MM_vs_GS_turquoise.pdf", width = 7, height = 6)
```

图例解释：

```text
x 轴越靠右：基因越能代表该模块。
y 轴越靠上：基因越和目标性状相关。
右上角基因：优先候选 hub genes。
```

## 十二、导出 Cytoscape 网络

如果需要给读者展示模块内部网络，可以导出 Cytoscape 文件。

```r
load("03_wgcna/network.RData")

target_module <- "turquoise"
module_genes <- moduleColors == target_module
module_expr <- datExpr[, module_genes]

TOM <- TOMsimilarityFromExpr(
  module_expr,
  power = softPower,
  networkType = "signed",
  TOMType = "signed"
)

dimnames(TOM) <- list(colnames(module_expr), colnames(module_expr))

exportNetworkToCytoscape(
  TOM,
  edgeFile = "05_cytoscape/turquoise_edges.txt",
  nodeFile = "05_cytoscape/turquoise_nodes.txt",
  weighted = TRUE,
  threshold = 0.08,
  nodeNames = colnames(module_expr),
  nodeAttr = target_module
)
```

Cytoscape 图例建议：

| 元素 | 建议含义 |
| --- | --- |
| 节点大小 | module membership 或 intramodular connectivity |
| 节点颜色 | gene significance 或 log2FC |
| 边粗细 | TOM weight |
| 标签 | top hub genes |

## 十三、模块功能富集

```r
library(clusterProfiler)
library(org.Hs.eg.db)

target_genes <- gene_info |>
  dplyr::filter(module == "turquoise") |>
  dplyr::pull(gene_id)

entrez <- mapIds(
  org.Hs.eg.db,
  keys = target_genes,
  column = "ENTREZID",
  keytype = "ENSEMBL",
  multiVals = "first"
) |>
  na.omit()

ego <- enrichGO(
  gene = entrez,
  OrgDb = org.Hs.eg.db,
  keyType = "ENTREZID",
  ont = "BP",
  pAdjustMethod = "BH",
  pvalueCutoff = 0.05
)

write.csv(as.data.frame(ego), "04_enrichment/turquoise_GO_BP.csv", row.names = FALSE)
```

解释方式：

- 如果 turquoise 模块与干旱强度正相关，且富集到 ABA response、water deprivation、oxidative stress，可以推测该模块参与干旱响应。
- 如果 blue 模块与 biomass 负相关，且富集到 defense response，可能说明胁迫防御激活伴随生长抑制。

## 十四、一个完整解释例子

假设得到下面结果：

| 模块 | 相关性最高性状 | cor | p-value | 富集功能 | 代表 hub gene |
| --- | --- | --- | --- | --- | --- |
| turquoise | drought_score | 0.82 | 1e-05 | response to water deprivation | DREB2A, HSP70 |
| blue | biomass | -0.71 | 0.002 | defense response | WRKY33, PR1 |
| brown | chlorophyll | 0.66 | 0.006 | photosynthesis | LHCA1, RBCS |

可以这样写结论：

```text
turquoise 模块与干旱评分显著正相关，说明该模块基因整体随干旱程度升高而上调。
该模块富集于水分胁迫和 ABA 响应通路，其中 DREB2A 同时具有较高 module membership 和 gene significance，
因此可作为后续验证的候选调控基因。
```

## 十五、常见问题与排查

| 问题 | 可能原因 | 建议 |
| --- | --- | --- |
| 模块数量很少 | 过滤太严格、样本差异弱、mergeCutHeight 太低 | 放宽过滤，调整 `minModuleSize` 和 `mergeCutHeight` |
| grey 模块过大 | 很多基因无法归入稳定模块 | 检查表达矩阵质量和低变异基因过滤 |
| soft power 无法达到 R² 0.8 | 样本数少、离群样本、批次效应 | 检查样本聚类，不要机械追求阈值 |
| 模块和性状全不相关 | 性状编码不合理或生物信号弱 | 检查 trait 表和样本顺序 |
| hub gene 全是 housekeeping genes | 输入基因过滤不合理 | 去掉低变异/低信息基因 |
| 网络太大难以画图 | 节点太多、边阈值太低 | 只导出目标模块 top edges |

## 十六、主要交付物

- VST/log2 transformed expression matrix
- 样本聚类树和离群样本检查图
- soft-threshold power 选择图
- gene dendrogram and module color 图
- module eigengene 表
- module-trait correlation heatmap
- 每个模块的基因清单
- 目标模块 hub gene 表
- MM-GS scatter plot
- 模块 GO/KEGG 富集结果
- Cytoscape network edge/node 文件
- 解释性报告和候选基因清单

## 十七、参考资料

- WGCNA 官方教程：网络构建、模块识别、模块-性状关系和 hub gene 筛选。
- WGCNA BMC Bioinformatics 原始论文：介绍 weighted correlation network、模块检测和拓扑性质。
- DESeq2 / Bioconductor RNA-seq workflow：用于 RNA-seq count 的 VST/rlog 方差稳定转换。
""",
        },
        {
            "title": "时间序列 RNA-seq 分析",
            "description": "面向多时间点 bulk RNA-seq 的动态表达分析流程，覆盖实验设计、DESeq2 LRT、maSigPro/ImpulseDE2、表达模式聚类、时间趋势可视化和功能解释。",
            "omics_type": "RNA-Seq",
            "dag_json": {
                "nodes": [
                    {"id": "design", "label": "时间序列实验设计"},
                    {"id": "qc", "label": "FASTQ/样本 QC"},
                    {"id": "count", "label": "表达定量与 count matrix"},
                    {"id": "normalize", "label": "VST/标准化"},
                    {"id": "lrt", "label": "DESeq2 LRT 时间效应"},
                    {"id": "trend", "label": "maSigPro/ImpulseDE2 趋势建模"},
                    {"id": "cluster", "label": "动态表达模式聚类"},
                    {"id": "enrichment", "label": "时间模块富集"},
                    {"id": "report", "label": "趋势图与报告"},
                ],
                "edges": [
                    {"source": "design", "target": "qc"},
                    {"source": "qc", "target": "count"},
                    {"source": "count", "target": "normalize"},
                    {"source": "normalize", "target": "lrt"},
                    {"source": "normalize", "target": "trend"},
                    {"source": "lrt", "target": "cluster"},
                    {"source": "trend", "target": "cluster"},
                    {"source": "cluster", "target": "enrichment"},
                    {"source": "enrichment", "target": "report"},
                ],
            },
            "content": """# 时间序列 RNA-seq 分析

## 一、适用场景

时间序列 RNA-seq 用于研究基因表达随时间变化的动态过程，例如发育阶段、药物处理后响应、病原感染过程、胁迫恢复过程或细胞分化诱导过程。它关注的不只是某个时间点的差异，而是完整的表达轨迹。

推荐场景：

| 场景 | 目标 | 推荐方法 |
| --- | --- | --- |
| 单一处理多时间点 | 找随时间变化的基因 | DESeq2 LRT、maSigPro |
| 处理组 vs 对照组多时间点 | 找时间和处理交互基因 | `~ condition + time + condition:time` |
| 非线性表达响应 | 捕捉脉冲、峰值和恢复 | ImpulseDE2、spline model |
| 表达模式归类 | 找早期/中期/晚期响应模块 | k-means、Mfuzz、TCseq |
| 功能解释 | 每类动态基因代表什么过程 | GO/KEGG/GSEA |

## 二、整体流程图

```mermaid
flowchart TD
    A[样本信息: condition/time/replicate] --> B[FASTQ QC 和表达定量]
    B --> C[raw count matrix]
    C --> D[DESeq2 VST / normalized count]
    D --> E[样本 PCA 与时间轨迹检查]
    E --> F[DESeq2 LRT 检测时间效应]
    E --> G[maSigPro / ImpulseDE2 建模趋势]
    F --> H[显著动态基因]
    G --> H
    H --> I[表达模式聚类]
    I --> J[模块趋势图]
    I --> K[GO/KEGG/GSEA 富集]
    J --> L[动态表达报告]
    K --> L
```

## 三、实验设计要点

| 设计项 | 建议 |
| --- | --- |
| 时间点 | 至少 3 个，越多越利于趋势建模 |
| 生物学重复 | 每个时间点每组至少 3 个 |
| 时间编码 | 可以作为 factor，也可以作为 numeric |
| 批次 | 多批建库必须记录 batch |
| 配对设计 | 同一对象重复采样时记录 subject |

样本表：

```text
sample_id,condition,time,batch,replicate
Ctrl_T0_1,Ctrl,0,B1,1
Ctrl_T6_1,Ctrl,6,B1,1
Treat_T0_1,Treat,0,B1,1
Treat_T6_1,Treat,6,B1,1
```

## 四、DESeq2 LRT 检测时间效应

LRT 适合回答“加入时间或交互项后模型是否显著更好”。

```r
library(DESeq2)
library(tidyverse)

counts <- read.csv("counts.csv", row.names = 1, check.names = FALSE)
coldata <- read.csv("sample_info.csv", row.names = 1)
counts <- counts[, rownames(coldata)]

coldata$time <- factor(coldata$time, levels = c("0", "6", "12", "24", "48"))
coldata$condition <- factor(coldata$condition)

dds <- DESeqDataSetFromMatrix(
  countData = round(as.matrix(counts)),
  colData = coldata,
  design = ~ condition + time + condition:time
)

keep <- rowSums(counts(dds) >= 10) >= 3
dds <- dds[keep, ]

dds_lrt <- DESeq(
  dds,
  test = "LRT",
  reduced = ~ condition + time
)

res_interaction <- results(dds_lrt)
dynamic_genes <- as.data.frame(res_interaction) |>
  rownames_to_column("gene_id") |>
  filter(padj < 0.05) |>
  arrange(padj)

write.csv(dynamic_genes, "time_condition_interaction_genes.csv", row.names = FALSE)
```

解释：

- full model: `condition + time + condition:time`
- reduced model: `condition + time`
- 显著基因说明处理组和对照组的时间变化轨迹不同。

## 五、趋势可视化

```r
vsd <- vst(dds, blind = FALSE)
expr <- assay(vsd)

plot_gene_trend <- function(gene_id) {
  df <- data.frame(
    expression = expr[gene_id, ],
    coldata
  )

  ggplot(df, aes(as.numeric(as.character(time)), expression, color = condition)) +
    stat_summary(fun = mean, geom = "line", linewidth = 1) +
    stat_summary(fun.data = mean_se, geom = "errorbar", width = 1) +
    geom_point(size = 2, alpha = 0.8) +
    theme_bw() +
    labs(x = "Time", y = "VST expression", title = gene_id)
}

plot_gene_trend(dynamic_genes$gene_id[1])
ggsave("top_dynamic_gene_trend.pdf", width = 6, height = 4)
```

## 六、maSigPro 动态建模

maSigPro 适合多时间点、多组别趋势建模。

```r
library(maSigPro)

expr_matrix <- expr[dynamic_genes$gene_id, ]
design <- make.design.matrix(
  data = data.frame(
    Time = as.numeric(as.character(coldata$time)),
    Replicate = coldata$replicate,
    Group = coldata$condition
  ),
  degree = 3
)

fit <- p.vector(expr_matrix, design, Q = 0.05)
tstep <- T.fit(fit, step.method = "backward")
sig_genes <- get.siggenes(tstep, rsq = 0.6, vars = "all")
```

## 七、表达模式聚类

```r
library(pheatmap)

selected <- head(dynamic_genes$gene_id, 1000)
mat <- expr[selected, ]
mat_z <- t(scale(t(mat)))

set.seed(123)
km <- kmeans(mat_z, centers = 6, nstart = 30)

cluster_df <- data.frame(
  gene_id = rownames(mat_z),
  cluster = km$cluster
)

write.csv(cluster_df, "time_series_gene_clusters.csv", row.names = FALSE)

pheatmap(
  mat_z,
  cluster_rows = TRUE,
  cluster_cols = FALSE,
  annotation_col = coldata[, c("condition", "time"), drop = FALSE],
  show_rownames = FALSE,
  filename = "time_series_dynamic_heatmap.pdf"
)
```

图例解释：

| 模式 | 含义 |
| --- | --- |
| Cluster 1 早期上升 | 可能是快速应答基因 |
| Cluster 2 晚期上升 | 可能是继发响应或发育后期通路 |
| Cluster 3 先升后降 | 可能是 transient response |
| Cluster 4 持续下降 | 可能是被处理抑制的过程 |

## 八、功能富集

```r
library(clusterProfiler)
library(org.Hs.eg.db)

for (k in sort(unique(cluster_df$cluster))) {
  genes <- cluster_df |>
    filter(cluster == k) |>
    pull(gene_id)

  entrez <- mapIds(
    org.Hs.eg.db,
    keys = genes,
    column = "ENTREZID",
    keytype = "ENSEMBL",
    multiVals = "first"
  ) |>
    na.omit()

  ego <- enrichGO(
    gene = entrez,
    OrgDb = org.Hs.eg.db,
    keyType = "ENTREZID",
    ont = "BP",
    pAdjustMethod = "BH",
    pvalueCutoff = 0.05
  )

  write.csv(as.data.frame(ego), paste0("cluster_", k, "_GO_BP.csv"), row.names = FALSE)
}
```

## 九、结果解释示例

```text
Cluster 1 在 0-6h 快速上升，随后恢复，富集到 inflammatory response。
这说明处理早期诱导了急性炎症通路。

Cluster 4 在 12-48h 持续下降，富集到 cell cycle。
这可能提示处理后细胞增殖逐步受抑。
```

## 十、主要交付物

- 样本 PCA 与时间轨迹图
- LRT 显著动态基因表
- 每个基因的趋势图
- 动态基因 heatmap
- 表达模式聚类表
- 每个 cluster 的 GO/KEGG/GSEA 富集
- 时间响应机制解释报告
""",
        },
        {
            "title": "lncRNA/circRNA/miRNA 非编码 RNA 分析",
            "description": "整合 lncRNA、circRNA 和 miRNA 的非编码 RNA 分析流程，覆盖数据类型判断、表达定量、差异分析、靶基因预测、ceRNA 网络和可视化解释。",
            "omics_type": "RNA-Seq",
            "dag_json": {
                "nodes": [
                    {"id": "design", "label": "非编码 RNA 类型判断"},
                    {"id": "qc", "label": "数据质控与接头过滤"},
                    {"id": "lncrna", "label": "lncRNA 鉴定/定量"},
                    {"id": "circrna", "label": "circRNA back-splice 检测"},
                    {"id": "mirna", "label": "miRNA 定量与 novel miRNA"},
                    {"id": "de", "label": "差异表达分析"},
                    {"id": "target", "label": "靶基因/宿主基因预测"},
                    {"id": "network", "label": "ceRNA/调控网络"},
                    {"id": "report", "label": "富集与报告"},
                ],
                "edges": [
                    {"source": "design", "target": "qc"},
                    {"source": "qc", "target": "lncrna"},
                    {"source": "qc", "target": "circrna"},
                    {"source": "qc", "target": "mirna"},
                    {"source": "lncrna", "target": "de"},
                    {"source": "circrna", "target": "de"},
                    {"source": "mirna", "target": "de"},
                    {"source": "de", "target": "target"},
                    {"source": "target", "target": "network"},
                    {"source": "network", "target": "report"},
                ],
            },
            "content": """# lncRNA/circRNA/miRNA 非编码 RNA 分析

## 一、适用场景

非编码 RNA 分析关注不直接编码蛋白、但具有调控作用的 RNA 分子。不同 RNA 类型的数据来源、建库方式和分析工具不同，必须先判断样本属于哪种测序类型。

| 类型 | 数据特点 | 常见目标 |
| --- | --- | --- |
| lncRNA-seq | 通常来自 rRNA depletion 或 strand-specific RNA-seq | 新 lncRNA 鉴定、差异表达、靶基因预测 |
| circRNA-seq | 常配合 rRNA depletion，有时 RNase R 处理 | back-splice junction 检测、差异 circRNA |
| miRNA-seq | small RNA，reads 很短，接头占比高 | known/novel miRNA 定量、靶基因预测 |

## 二、整体流程图

```mermaid
flowchart TD
    A[样本与建库类型] --> B[FASTQ QC 和 adapter trimming]
    B --> C{RNA 类型}
    C --> D[lncRNA: STAR/StringTie/FEELnc]
    C --> E[circRNA: CIRI2/find_circ/CIRCexplorer2]
    C --> F[miRNA: miRDeep2/miRge/sRNAbench]
    D --> G[差异 lncRNA]
    E --> H[差异 circRNA]
    F --> I[差异 miRNA]
    G --> J[顺式/反式靶基因]
    H --> K[宿主基因与 miRNA sponge]
    I --> L[miRNA target genes]
    J --> M[ceRNA/调控网络]
    K --> M
    L --> M
    M --> N[富集分析与报告]
```

## 三、lncRNA 分析路线

### 1. 比对和转录本组装

```bash
STAR \
  --runThreadN 16 \
  --genomeDir ref/star_index \
  --readFilesIn sample_R1.fq.gz sample_R2.fq.gz \
  --readFilesCommand zcat \
  --outSAMtype BAM SortedByCoordinate \
  --outFileNamePrefix star/sample_

stringtie star/sample_Aligned.sortedByCoord.out.bam \
  -G ref/genes.gtf \
  -o stringtie/sample.gtf \
  -p 12
```

### 2. 合并转录本并筛选候选 lncRNA

```bash
stringtie --merge \
  -G ref/genes.gtf \
  -o stringtie/merged.gtf \
  stringtie/gtf_list.txt

gffcompare \
  -r ref/genes.gtf \
  -o stringtie/merged_compare \
  stringtie/merged.gtf
```

筛选原则：

| 条件 | 建议 |
| --- | --- |
| transcript length | `>= 200 nt` |
| exon number | 通常 `>= 2` 更可靠 |
| coding potential | CPC2、CNCI、PLEK、CPAT 判定为 non-coding |
| 与已知蛋白编码重叠 | 根据 class code 过滤 |

## 四、circRNA 分析路线

circRNA 的核心证据是 back-splice junction。

```bash
bwa mem -T 19 ref/genome.fa sample_R1.fq.gz sample_R2.fq.gz > sample.sam

CIRI2.pl \
  -I sample.sam \
  -O circRNA/sample.ciri.txt \
  -F ref/genome.fa \
  -A ref/genes.gtf
```

也可以使用 STAR chimeric 输出：

```bash
STAR \
  --runThreadN 16 \
  --genomeDir ref/star_index \
  --readFilesIn sample_R1.fq.gz sample_R2.fq.gz \
  --readFilesCommand zcat \
  --chimSegmentMin 10 \
  --chimJunctionOverhangMin 10 \
  --outSAMtype BAM SortedByCoordinate \
  --outFileNamePrefix star_chim/sample_
```

circRNA 过滤建议：

- back-splice junction reads `>= 2` 或更高。
- 至少在多个样本中出现。
- 去除线粒体、低复杂度区域和明显重复区域。
- 重要候选建议做 divergent primer 验证。

## 五、miRNA 分析路线

small RNA 数据接头非常明显，必须先 trimming。

```bash
cutadapt \
  -a TGGAATTCTCGGGTGCCAAGG \
  -m 18 \
  -M 30 \
  -o clean/sample.clean.fq.gz \
  raw/sample.fq.gz
```

miRDeep2 示例：

```bash
mapper.pl clean/sample.clean.fq.gz \
  -e -h -j -l 18 -m \
  -p ref/bowtie_index \
  -s mirdeep/sample_collapsed.fa \
  -t mirdeep/sample_vs_genome.arf

miRDeep2.pl \
  mirdeep/sample_collapsed.fa \
  ref/genome.fa \
  mirdeep/sample_vs_genome.arf \
  mature_ref.fa \
  mature_other.fa \
  hairpin_ref.fa \
  -t hsa
```

## 六、差异表达分析

非编码 RNA 差异分析仍然可以使用 DESeq2。

```r
library(DESeq2)

count_data <- read.csv("noncoding_counts.csv", row.names = 1, check.names = FALSE)
sample_info <- read.csv("sample_info.csv", row.names = 1)

dds <- DESeqDataSetFromMatrix(
  countData = round(as.matrix(count_data)),
  colData = sample_info,
  design = ~ condition
)

dds <- dds[rowSums(counts(dds) >= 5) >= 3, ]
dds <- DESeq(dds)

res <- results(dds, contrast = c("condition", "Treat", "Ctrl"))
write.csv(as.data.frame(res), "noncoding_DESeq2_results.csv")
```

## 七、靶基因和 ceRNA 网络

| RNA 类型 | 靶标策略 |
| --- | --- |
| lncRNA | cis: 上下游 10-100 kb 蛋白编码基因；trans: 表达相关或数据库预测 |
| circRNA | 宿主基因、miRNA binding site、circRNA-miRNA-mRNA |
| miRNA | TargetScan、miRanda、RNAhybrid、miRTarBase |

ceRNA 网络示意：

```text
circRNA_001 ↑
    |
    | sponge
    v
miR-21 ↓
    |
    | repression relieved
    v
TargetGeneA ↑
```

解释：如果 circRNA 上调、miRNA 下调、靶 mRNA 上调，并且三者存在预测结合关系，可以构建候选 ceRNA 调控轴。

## 八、主要交付物

- lncRNA/circRNA/miRNA 表达矩阵
- 差异非编码 RNA 表
- novel lncRNA / novel miRNA 候选表
- circRNA back-splice junction 支持表
- miRNA target gene 表
- lncRNA cis/trans target 表
- circRNA-miRNA-mRNA 或 lncRNA-miRNA-mRNA 网络
- GO/KEGG 富集分析
- 关键调控轴图和报告
""",
        },
        {
            "title": "空间转录组 Visium 分析",
            "description": "面向 10x Genomics Visium 空间转录组的分析流程，覆盖 Space Ranger、组织切片 QC、空间聚类、空间差异表达、细胞类型解卷积和空间通讯解释。",
            "omics_type": "Spatial Transcriptomics",
            "dag_json": {
                "nodes": [
                    {"id": "spaceranger", "label": "Space Ranger count"},
                    {"id": "qc", "label": "组织图像与 spot QC"},
                    {"id": "seurat", "label": "Seurat/Squidpy 读入"},
                    {"id": "cluster", "label": "空间降维聚类"},
                    {"id": "spatial_markers", "label": "空间 marker"},
                    {"id": "deconv", "label": "细胞类型解卷积"},
                    {"id": "domain", "label": "空间区域解释"},
                    {"id": "communication", "label": "空间邻近通讯"},
                    {"id": "report", "label": "空间报告"},
                ],
                "edges": [
                    {"source": "spaceranger", "target": "qc"},
                    {"source": "qc", "target": "seurat"},
                    {"source": "seurat", "target": "cluster"},
                    {"source": "cluster", "target": "spatial_markers"},
                    {"source": "seurat", "target": "deconv"},
                    {"source": "spatial_markers", "target": "domain"},
                    {"source": "deconv", "target": "domain"},
                    {"source": "domain", "target": "communication"},
                    {"source": "communication", "target": "report"},
                ],
            },
            "content": """# 空间转录组 Visium 分析

## 一、适用场景

Visium 空间转录组在组织切片坐标上测量表达量，适合研究基因表达、细胞组成和组织结构之间的空间关系。它的基本单位是 spot，一个 spot 可能包含多个细胞。

适用于：

- 肿瘤微环境空间区域识别。
- 脑、胚胎、植物组织等结构化组织图谱。
- 某个基因或通路在组织中的空间分布。
- scRNA-seq 细胞类型映射到组织切片。
- 空间邻近的细胞通讯推断。

## 二、整体流程图

```mermaid
flowchart TD
    A[显微图像 + FASTQ] --> B[Space Ranger count]
    B --> C[filtered_feature_bc_matrix + tissue image]
    C --> D[Seurat/Scanpy/Squidpy 读入]
    D --> E[spot QC 和归一化]
    E --> F[PCA/UMAP/空间聚类]
    F --> G[空间区域 marker genes]
    D --> H[参考 scRNA-seq 注释]
    H --> I[细胞类型解卷积]
    G --> J[空间 domain 解释]
    I --> J
    J --> K[空间通讯/邻近分析]
    K --> L[报告]
```

## 三、Space Ranger 预处理

```bash
spaceranger count \
  --id=sample_visium \
  --transcriptome=/ref/refdata-gex-GRCh38-2024-A \
  --fastqs=/data/fastq/sample_visium \
  --sample=sample_visium \
  --image=/data/image/tissue_hires_image.tif \
  --slide=V19J01-123 \
  --area=A1 \
  --localcores=24 \
  --localmem=128
```

重点检查：

| 指标 | 说明 |
| --- | --- |
| tissue detection | spot 是否正确落在组织区域 |
| sequencing saturation | 是否测序足够 |
| median genes per spot | spot 表达复杂度 |
| fraction reads in spots | reads 是否有效落入组织 spot |
| image alignment | 图像和 spot 坐标是否对齐 |

## 四、Seurat 读入和基础分析

```r
library(Seurat)
library(ggplot2)

obj <- Load10X_Spatial(
  data.dir = "sample_visium/outs",
  filename = "filtered_feature_bc_matrix.h5",
  assay = "Spatial"
)

obj <- SCTransform(obj, assay = "Spatial", verbose = FALSE)
obj <- RunPCA(obj, assay = "SCT")
obj <- FindNeighbors(obj, reduction = "pca", dims = 1:30)
obj <- FindClusters(obj, resolution = 0.6)
obj <- RunUMAP(obj, reduction = "pca", dims = 1:30)

SpatialDimPlot(obj, label = TRUE, label.size = 3)
SpatialFeaturePlot(obj, features = c("MKI67", "COL1A1", "PTPRC"))
```

图例解释：

| 图 | 读法 |
| --- | --- |
| SpatialDimPlot | 不同颜色表示空间聚类或区域 |
| SpatialFeaturePlot | 颜色越深表示该 spot 表达越高 |
| UMAP | 看表达相似性，不保留真实组织空间 |

## 五、空间差异表达和区域 marker

```r
markers <- FindAllMarkers(
  obj,
  assay = "SCT",
  only.pos = TRUE,
  min.pct = 0.25,
  logfc.threshold = 0.25
)

write.csv(markers, "spatial_cluster_markers.csv", row.names = FALSE)
```

空间区域解释示例：

```text
Cluster 1 富集 EPCAM、KRT8，位于组织边缘，可能是上皮区域。
Cluster 3 富集 COL1A1、DCN，位于间质区域，可能是 fibroblast-rich domain。
Cluster 5 富集 PTPRC、LST1，呈灶状分布，可能是免疫浸润区域。
```

## 六、细胞类型解卷积

如果有 scRNA-seq 参考数据，可将细胞类型映射到 Visium spot。

```r
anchors <- FindTransferAnchors(
  reference = sc_obj,
  query = obj,
  normalization.method = "SCT"
)

predictions <- TransferData(
  anchorset = anchors,
  refdata = sc_obj$celltype,
  prediction.assay = TRUE,
  weight.reduction = obj[["pca"]]
)

obj[["predictions"]] <- predictions
SpatialFeaturePlot(obj, features = c("prediction.score.T_cell", "prediction.score.Fibroblast"))
```

也可以使用 RCTD、cell2location、Tangram、SPOTlight 等方法做比例解卷积。

## 七、Squidpy 空间邻域分析

```python
import scanpy as sc
import squidpy as sq

adata = sc.read_visium("sample_visium/outs")
adata.var_names_make_unique()

sc.pp.normalize_total(adata)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata)
sc.pp.pca(adata)
sc.pp.neighbors(adata)
sc.tl.leiden(adata, resolution=0.6)
sc.tl.umap(adata)

sq.gr.spatial_neighbors(adata)
sq.gr.nhood_enrichment(adata, cluster_key="leiden")
sq.pl.nhood_enrichment(adata, cluster_key="leiden")
```

## 八、空间通讯解释

空间通讯比普通 scRNA-seq 通讯更关注邻近关系。

```text
如果免疫区域与肿瘤区域相邻，并且 ligand 在免疫 spot 高表达、receptor 在肿瘤 spot 高表达，
则该 ligand-receptor pair 具有更强的空间解释价值。
```

常用组合：

- `CellChat` + spatial coordinates
- `Squidpy ligand-receptor`
- `NicheNet`
- `LIANA`

## 九、主要交付物

- Space Ranger `web_summary.html`
- tissue image + spot overlay
- spot QC 表
- SpatialDimPlot 空间聚类图
- SpatialFeaturePlot marker 空间图
- 空间区域 marker 表
- 细胞类型解卷积比例图
- 空间邻域富集图
- 候选 ligand-receptor 空间通讯图
- 空间生物学解释报告
""",
        },
        {
            "title": "单细胞高级下游：拟时序、通讯、RNA velocity",
            "description": "面向 scRNA-seq 的高级下游分析流程，覆盖拟时序轨迹、细胞通讯、RNA velocity、起点选择、结果交叉验证和生物学解释。",
            "omics_type": "scRNA-Seq",
            "dag_json": {
                "nodes": [
                    {"id": "input", "label": "已注释 scRNA-seq 对象"},
                    {"id": "subset", "label": "选择目标细胞群"},
                    {"id": "trajectory", "label": "Monocle3/Slingshot 拟时序"},
                    {"id": "communication", "label": "CellChat/NicheNet 通讯"},
                    {"id": "velocity", "label": "scVelo RNA velocity"},
                    {"id": "crosscheck", "label": "多结果交叉验证"},
                    {"id": "visual", "label": "轨迹/网络/velocity 图"},
                    {"id": "report", "label": "机制解释报告"},
                ],
                "edges": [
                    {"source": "input", "target": "subset"},
                    {"source": "subset", "target": "trajectory"},
                    {"source": "subset", "target": "communication"},
                    {"source": "subset", "target": "velocity"},
                    {"source": "trajectory", "target": "crosscheck"},
                    {"source": "communication", "target": "crosscheck"},
                    {"source": "velocity", "target": "crosscheck"},
                    {"source": "crosscheck", "target": "visual"},
                    {"source": "visual", "target": "report"},
                ],
            },
            "content": """# 单细胞高级下游：拟时序、通讯、RNA velocity

## 一、适用场景

基础 scRNA-seq 分析得到细胞类型和 marker 后，高级下游用于回答更深入的问题：

| 分析 | 主要问题 | 常用工具 |
| --- | --- | --- |
| 拟时序 | 细胞是否存在连续状态转换或分化轨迹？ | Monocle3、Slingshot、Palantir |
| 细胞通讯 | 细胞群之间可能通过哪些 ligand-receptor 互作？ | CellChat、NicheNet、LIANA |
| RNA velocity | 细胞状态变化方向是什么？ | velocyto、scVelo |

注意：这些方法都是推断，不能替代实验验证。结果必须结合 marker、样本背景、时间点和已知生物学知识解释。

## 二、整体流程图

```mermaid
flowchart TD
    A[Seurat/Scanpy 基础分析对象] --> B[选择目标细胞群]
    B --> C[重新降维聚类]
    C --> D[Monocle3 / Slingshot 拟时序]
    C --> E[CellChat / NicheNet 通讯]
    C --> F[velocyto + scVelo RNA velocity]
    D --> G[动态基因与分支基因]
    E --> H[ligand-receptor 网络]
    F --> I[velocity arrows 和 latent time]
    G --> J[交叉验证候选机制]
    H --> J
    I --> J
    J --> K[报告和实验验证候选]
```

## 三、拟时序 Monocle3

拟时序适合分析发育、分化、激活、疾病进展等连续状态。

```r
library(monocle3)
library(SeuratWrappers)

target <- subset(seurat_obj, subset = celltype %in% c("Progenitor", "Intermediate", "Mature"))

cds <- as.cell_data_set(target)
cds <- cluster_cells(cds)
cds <- learn_graph(cds)

cds <- order_cells(
  cds,
  root_cells = colnames(cds)[colData(cds)$celltype == "Progenitor"]
)

plot_cells(
  cds,
  color_cells_by = "pseudotime",
  label_cell_groups = FALSE,
  label_leaves = TRUE,
  label_branch_points = TRUE
)
```

关键点：

- 起点 root cells 需要根据生物学先验选择。
- 不要对完全无连续关系的细胞强行做拟时序。
- 分支点附近基因值得重点关注。

## 四、拟时序动态基因

```r
deg_pseudo <- graph_test(
  cds,
  neighbor_graph = "principal_graph",
  cores = 4
)

dynamic_genes <- deg_pseudo |>
  dplyr::filter(q_value < 0.05) |>
  dplyr::arrange(q_value)

write.csv(dynamic_genes, "monocle3_pseudotime_genes.csv")
```

解释示例：

```text
GeneA 在 pseudotime 早期高表达，随后下降，可能标记祖细胞状态。
GeneB 在分支 2 后持续升高，可能参与成熟细胞命运决定。
```

## 五、CellChat 细胞通讯

```r
library(CellChat)

data.input <- GetAssayData(seurat_obj, assay = "RNA", slot = "data")
meta <- seurat_obj@meta.data

cellchat <- createCellChat(
  object = data.input,
  meta = meta,
  group.by = "celltype"
)

cellchat@DB <- CellChatDB.human

cellchat <- subsetData(cellchat)
cellchat <- identifyOverExpressedGenes(cellchat)
cellchat <- identifyOverExpressedInteractions(cellchat)
cellchat <- computeCommunProb(cellchat)
cellchat <- filterCommunication(cellchat, min.cells = 10)
cellchat <- computeCommunProbPathway(cellchat)
cellchat <- aggregateNet(cellchat)

netVisual_circle(
  cellchat@net$count,
  vertex.weight = as.numeric(table(cellchat@idents)),
  weight.scale = TRUE,
  label.edge = FALSE
)
```

图例解释：

| 元素 | 含义 |
| --- | --- |
| 节点 | 细胞类型 |
| 节点大小 | 细胞数量 |
| 连线 | 推断的通讯关系 |
| 连线粗细 | ligand-receptor 互作数量或强度 |
| 方向 | sender 到 receiver |

## 六、NicheNet 配体活性分析

NicheNet 适合从 receiver 细胞的差异基因反推 upstream ligands。

```r
# 思路示意：
# 1. 定义 sender cell types
# 2. 定义 receiver cell type
# 3. 找 receiver 中处理组 vs 对照组 DEG
# 4. 用 NicheNet 预测哪些 ligand 最能解释这些 DEG
```

解释：

```text
如果 macrophage 表达 TGFB1，fibroblast 中 TGF-beta response genes 上调，
NicheNet 可能将 TGFB1 排为高活性 ligand。
```

## 七、RNA velocity scVelo

RNA velocity 需要 spliced/unspliced count，通常由 `velocyto` 或 `kallisto|bustools` 生成 loom/h5ad。

```bash
velocyto run10x \
  sample_cellranger_output \
  ref/genes.gtf
```

```python
import scvelo as scv
import scanpy as sc

adata = scv.read("sample.loom", cache=True)
scv.pp.filter_and_normalize(adata)
scv.pp.moments(adata, n_pcs=30, n_neighbors=30)

scv.tl.velocity(adata, mode="stochastic")
scv.tl.velocity_graph(adata)
scv.pl.velocity_embedding_stream(adata, basis="umap", color="celltype")

scv.tl.latent_time(adata)
scv.pl.scatter(adata, color="latent_time", color_map="gnuplot")
```

图例解释：

| 图 | 读法 |
| --- | --- |
| velocity stream | 箭头方向表示预测状态变化方向 |
| latent time | 越大表示越靠近推断终末状态 |
| phase portrait | spliced/unspliced 关系支持基因动态 |

## 八、三类结果如何交叉验证

| 发现 | 支持证据组合 |
| --- | --- |
| 分化方向 | Monocle3 pseudotime 与 scVelo arrows 方向一致 |
| 关键调控细胞 | CellChat 显示该细胞为强 sender，目标细胞沿拟时序变化 |
| 候选 ligand | sender 表达 ligand，receiver 有 receptor 且下游基因随 pseudotime 变化 |
| 关键基因 | 是动态基因、velocity gene，并出现在通路或通讯下游 |

示例结论：

```text
Monocle3 显示 monocyte 向 macrophage 状态连续过渡，scVelo 箭头方向与该轨迹一致。
CellChat 进一步提示 fibroblast 到 macrophage 的 CSF1-CSF1R 通讯增强。
因此可以假设 fibroblast-derived CSF1 参与推动 macrophage 状态转换。
```

## 九、常见问题

| 问题 | 可能原因 | 建议 |
| --- | --- | --- |
| 拟时序方向不合理 | root 选择错误或细胞群不连续 | 根据 marker 和时间点重新选择 root |
| 通讯结果过多 | 数据库互作多、阈值太宽 | 关注显著通路和组间变化 |
| RNA velocity 箭头混乱 | unspliced 信号弱、细胞周期影响 | 过滤低质量基因，分细胞群分析 |
| 三种结果不一致 | 方法假设不同 | 优先解释多证据支持的机制 |

## 十、主要交付物

- 目标细胞群重新聚类图
- pseudotime UMAP
- 分支和动态基因表
- ligand-receptor 通讯表
- 通讯 circle plot / bubble plot
- velocity stream plot
- latent time 图
- 多证据整合候选机制表
- 可验证候选 ligand、receptor、target gene 清单
""",
        },
        {
            "title": "多组学联合分析：RNA-seq + ATAC-seq/CUT&Tag",
            "description": "整合 RNA-seq 差异表达、ATAC-seq 开放染色质和 CUT&Tag 组蛋白修饰/转录因子结合信号，解释基因表达变化背后的调控机制。",
            "omics_type": "Multi-omics",
            "dag_json": {
                "nodes": [
                    {"id": "project", "label": "建立多组学项目目录"},
                    {"id": "metadata", "label": "样本配对与示例数据"},
                    {"id": "rna", "label": "RNA-seq DEG"},
                    {"id": "atac", "label": "ATAC/CUT&Tag peak"},
                    {"id": "annotate", "label": "peak 注释到基因"},
                    {"id": "integrate", "label": "DEG 与 peak 联合分型"},
                    {"id": "motif", "label": "motif/TF 富集"},
                    {"id": "tracks", "label": "基因座浏览图"},
                    {"id": "report", "label": "调控机制报告"},
                ],
                "edges": [
                    {"source": "project", "target": "metadata"},
                    {"source": "metadata", "target": "rna"},
                    {"source": "metadata", "target": "atac"},
                    {"source": "atac", "target": "annotate"},
                    {"source": "rna", "target": "integrate"},
                    {"source": "annotate", "target": "integrate"},
                    {"source": "integrate", "target": "motif"},
                    {"source": "integrate", "target": "tracks"},
                    {"source": "tracks", "target": "report"},
                ],
            },
            "content": """# 多组学联合分析：RNA-seq + ATAC-seq/CUT&Tag

## 一、项目目标

RNA-seq 告诉我们“哪些基因表达改变”，ATAC-seq/CUT&Tag 告诉我们“哪些调控区域状态改变”。多组学联合分析的目标是把两者串起来，解释基因表达变化背后的调控机制。

典型问题：

| 问题 | 数据证据 |
| --- | --- |
| 某个 DEG 为什么上调？ | 启动子/增强子 ATAC signal 上升，H3K27ac 上升 |
| 哪些 TF 可能驱动变化？ | 上调 peak 中 motif 富集，TF 自身表达上调 |
| 哪些 enhancer 可能调控目标基因？ | peak-to-gene 距离、相关性、同方向变化 |
| CUT&Tag mark 是否支持表达变化？ | H3K4me3/H3K27ac 与表达正相关，H3K27me3 与表达负相关 |

## 二、建立项目目录

```bash
mkdir -p multiomics_project/{00_metadata,01_rnaseq,02_atac_cuttag,03_peak_annotation,04_integration,05_motif,06_tracks,report}
mkdir -p multiomics_project/01_rnaseq/{counts,deg,plots}
mkdir -p multiomics_project/02_atac_cuttag/{peaks,bigwig,diffbind,plots}
```

推荐目录：

```text
multiomics_project/
├── 00_metadata/
│   ├── sample_info.csv
│   └── contrast_info.csv
├── 01_rnaseq/
│   ├── counts/
│   ├── deg/
│   └── plots/
├── 02_atac_cuttag/
│   ├── peaks/
│   ├── bigwig/
│   └── diffbind/
├── 03_peak_annotation/
├── 04_integration/
├── 05_motif/
├── 06_tracks/
└── report/
```

## 三、示例数据

`00_metadata/sample_info.csv`：

```text
sample_id,condition,assay,batch
Ctrl_RNA_1,Ctrl,RNA-seq,B1
Ctrl_RNA_2,Ctrl,RNA-seq,B1
Treat_RNA_1,Treat,RNA-seq,B1
Treat_RNA_2,Treat,RNA-seq,B1
Ctrl_ATAC_1,Ctrl,ATAC-seq,B1
Ctrl_ATAC_2,Ctrl,ATAC-seq,B1
Treat_ATAC_1,Treat,ATAC-seq,B1
Treat_ATAC_2,Treat,ATAC-seq,B1
```

`01_rnaseq/deg/Treat_vs_Ctrl_DEG.csv`：

```text
gene_id,symbol,log2FoldChange,padj
ENSG00000141510,TP53,1.8,0.0001
ENSG00000171862,PTEN,-1.2,0.003
ENSG00000136997,MYC,2.1,0.00001
```

`02_atac_cuttag/diffbind/Treat_vs_Ctrl_peaks.bed`：

```text
chr8	127735000	127736200	peak_MYC_enhancer	4.5
chr17	7668000	7669500	peak_TP53_promoter	3.2
chr10	87860000	87861500	peak_PTEN_enhancer	-2.7
```

## 四、整体流程图

```mermaid
flowchart TD
    A[RNA-seq DEG table] --> C[gene-level regulation]
    B[ATAC/CUT&Tag differential peaks] --> D[regulatory-region regulation]
    D --> E[annotate peaks to nearest genes]
    C --> F[merge DEG and peak annotations]
    E --> F
    F --> G[concordant genes: expression and chromatin same direction]
    F --> H[discordant genes: complex regulation]
    G --> I[motif enrichment and TF prioritization]
    I --> J[locus tracks and mechanism report]
```

## 五、peak 注释到基因

```r
library(ChIPseeker)
library(TxDb.Hsapiens.UCSC.hg38.knownGene)
library(org.Hs.eg.db)

peak_file <- "02_atac_cuttag/diffbind/Treat_vs_Ctrl_peaks.bed"
txdb <- TxDb.Hsapiens.UCSC.hg38.knownGene

peak_anno <- annotatePeak(
  peak_file,
  TxDb = txdb,
  tssRegion = c(-3000, 3000),
  annoDb = "org.Hs.eg.db"
)

peak_df <- as.data.frame(peak_anno)
write.csv(peak_df, "03_peak_annotation/Treat_vs_Ctrl_peak_annotation.csv", row.names = FALSE)
```

## 六、RNA 和 peak 联合分型

```r
library(tidyverse)

deg <- read.csv("01_rnaseq/deg/Treat_vs_Ctrl_DEG.csv")
peak <- read.csv("03_peak_annotation/Treat_vs_Ctrl_peak_annotation.csv")

peak_gene <- peak |>
  transmute(
    gene_id = geneId,
    peak_id = paste(seqnames, start, end, sep = "_"),
    annotation,
    distanceToTSS,
    peak_log2FC = score
  )

integrated <- deg |>
  left_join(peak_gene, by = "gene_id") |>
  mutate(
    pattern = case_when(
      log2FoldChange > 0 & peak_log2FC > 0 ~ "RNA_up_peak_up",
      log2FoldChange < 0 & peak_log2FC < 0 ~ "RNA_down_peak_down",
      log2FoldChange > 0 & peak_log2FC < 0 ~ "RNA_up_peak_down",
      log2FoldChange < 0 & peak_log2FC > 0 ~ "RNA_down_peak_up",
      TRUE ~ "other"
    )
  )

write.csv(integrated, "04_integration/RNA_ATAC_integrated_table.csv", row.names = FALSE)
```

图例解释：

| 模式 | 可能解释 |
| --- | --- |
| RNA_up_peak_up | 开放染色质/活性修饰增强，支持基因上调 |
| RNA_down_peak_down | 调控区域关闭，支持基因下调 |
| RNA_up_peak_down | 可能受远端 enhancer、TF、RNA 稳定性调控 |
| RNA_down_peak_up | 可能有抑制性 TF 或复杂 chromatin context |

## 七、motif 富集和 TF 优先级

```bash
findMotifsGenome.pl \
  04_integration/RNA_up_peak_up.bed \
  hg38 \
  05_motif/RNA_up_peak_up_motif \
  -size given
```

整合 TF：

```r
tf_expr <- deg |>
  filter(symbol %in% c("MYC", "JUN", "FOS", "STAT1", "IRF1")) |>
  select(symbol, log2FoldChange, padj)

motif <- read.delim("05_motif/RNA_up_peak_up_motif/knownResults.txt")

tf_priority <- motif |>
  select(Motif.Name, P.value, q.value) |>
  left_join(tf_expr, by = c("Motif.Name" = "symbol")) |>
  arrange(q.value, desc(log2FoldChange))
```

## 八、基因座图示例

```bash
computeMatrix reference-point \
  -S 02_atac_cuttag/bigwig/Ctrl.bw 02_atac_cuttag/bigwig/Treat.bw \
  -R 04_integration/RNA_up_peak_up.bed \
  --referencePoint center \
  -b 3000 -a 3000 \
  -o 06_tracks/ATAC_matrix.gz

plotHeatmap \
  -m 06_tracks/ATAC_matrix.gz \
  -out 06_tracks/ATAC_peak_heatmap.pdf
```

## 九、结果解释例子

```text
MYC 在 RNA-seq 中显著上调，附近 enhancer ATAC signal 和 H3K27ac signal 同时增强。
该 enhancer peak 中富集 AP-1 motif，且 JUN/FOS 表达上调。
因此可以提出假设：处理激活 AP-1 相关调控元件，进一步促进 MYC 表达。
```

## 十、交付物

- DEG 表和 differential peak 表
- peak 注释表
- RNA + chromatin 联合分型表
- motif 富集结果
- TF 优先级列表
- deepTools heatmap/profile
- IGV/locus tracks
- 候选 enhancer-gene-TF 调控轴报告
""",
        },
        {
            "title": "转录因子调控网络分析",
            "description": "从 RNA-seq、WGCNA 或单细胞结果中推断关键转录因子和 TF-target 网络，整合 DoRothEA/VIPER、ChEA3、TRRUST、motif 和表达相关性证据。",
            "omics_type": "Regulatory Network",
            "dag_json": {
                "nodes": [
                    {"id": "project", "label": "项目目录与输入基因集"},
                    {"id": "signature", "label": "构建表达 signature"},
                    {"id": "dorothea", "label": "DoRothEA/VIPER TF 活性"},
                    {"id": "chea3", "label": "ChEA3/TRRUST TF 富集"},
                    {"id": "motif", "label": "motif 支持证据"},
                    {"id": "network", "label": "TF-target 网络"},
                    {"id": "rank", "label": "关键 TF 排序"},
                    {"id": "report", "label": "调控机制报告"},
                ],
                "edges": [
                    {"source": "project", "target": "signature"},
                    {"source": "signature", "target": "dorothea"},
                    {"source": "signature", "target": "chea3"},
                    {"source": "signature", "target": "motif"},
                    {"source": "dorothea", "target": "network"},
                    {"source": "chea3", "target": "network"},
                    {"source": "motif", "target": "network"},
                    {"source": "network", "target": "rank"},
                    {"source": "rank", "target": "report"},
                ],
            },
            "content": """# 转录因子调控网络分析

## 一、项目目录

```bash
mkdir -p tf_network_project/{00_input,01_signature,02_tf_activity,03_tf_enrichment,04_motif,05_network,report}
```

```text
tf_network_project/
├── 00_input/
│   ├── deg_table.csv
│   ├── expression_matrix.csv
│   └── target_gene_set.txt
├── 01_signature/
├── 02_tf_activity/
├── 03_tf_enrichment/
├── 04_motif/
├── 05_network/
└── report/
```

## 二、示例数据

`00_input/deg_table.csv`：

```text
gene_symbol,log2FoldChange,padj
IL6,2.4,0.00001
CXCL8,2.1,0.0002
NFKBIA,1.8,0.0003
JUN,1.5,0.001
FOS,1.3,0.002
```

## 三、整体流程图

```mermaid
flowchart TD
    A[DEG / WGCNA module / scRNA marker] --> B[ranked gene signature]
    B --> C[DoRothEA + VIPER TF activity]
    B --> D[ChEA3 / TRRUST TF enrichment]
    B --> E[motif enrichment]
    C --> F[integrated TF ranking]
    D --> F
    E --> F
    F --> G[TF-target network]
    G --> H[核心 TF 机制解释]
```

## 四、构建 ranked signature

```r
library(tidyverse)

deg <- read.csv("00_input/deg_table.csv")

signature <- deg |>
  filter(!is.na(padj)) |>
  mutate(score = sign(log2FoldChange) * -log10(padj)) |>
  arrange(desc(score))

write.csv(signature, "01_signature/ranked_signature.csv", row.names = FALSE)
```

## 五、DoRothEA + VIPER 推断 TF 活性

```r
library(dorothea)
library(viper)
library(tidyverse)

expr <- read.csv("00_input/expression_matrix.csv", row.names = 1, check.names = FALSE)

data(dorothea_hs, package = "dorothea")
regulons <- dorothea_hs |>
  filter(confidence %in% c("A", "B", "C"))

regulon_list <- df2regulon(regulons)
tf_activity <- viper(as.matrix(expr), regulon_list, verbose = FALSE)

write.csv(tf_activity, "02_tf_activity/viper_tf_activity.csv")
```

解释：

```text
TF 自身表达不一定改变，但它的 target genes 可以整体上调或下调。
VIPER/DoRothEA 关注的是 regulon 活性，而不是只看 TF mRNA。
```

## 六、ChEA3/TRRUST 富集思路

输入上调基因和下调基因分别进行 TF enrichment。

```r
up_genes <- deg |>
  filter(log2FoldChange > 1, padj < 0.05) |>
  pull(gene_symbol)

down_genes <- deg |>
  filter(log2FoldChange < -1, padj < 0.05) |>
  pull(gene_symbol)

writeLines(up_genes, "03_tf_enrichment/up_genes.txt")
writeLines(down_genes, "03_tf_enrichment/down_genes.txt")
```

可将基因列表提交至 ChEA3，或用 TRRUST/Enrichr API 获取候选 TF。

## 七、整合多个证据排序 TF

```r
tf_viper <- read.csv("02_tf_activity/viper_tf_activity.csv", row.names = 1)
motif <- read.csv("04_motif/motif_results.csv")
chea3 <- read.csv("03_tf_enrichment/chea3_results.csv")

tf_rank <- chea3 |>
  transmute(tf = TF, chea3_rank = Rank) |>
  left_join(motif |> transmute(tf = MotifTF, motif_qvalue = qvalue), by = "tf") |>
  left_join(deg |> transmute(tf = gene_symbol, tf_log2FC = log2FoldChange, tf_padj = padj), by = "tf") |>
  mutate(
    evidence_score =
      -log10(motif_qvalue + 1e-300) +
      ifelse(!is.na(tf_padj), -log10(tf_padj + 1e-300), 0) +
      abs(tf_log2FC)
  ) |>
  arrange(desc(evidence_score))

write.csv(tf_rank, "05_network/integrated_tf_ranking.csv", row.names = FALSE)
```

## 八、TF-target 网络

```r
library(igraph)

edges <- regulons |>
  filter(tf %in% head(tf_rank$tf, 10)) |>
  select(from = tf, to = target, mor)

g <- graph_from_data_frame(edges, directed = TRUE)
write_graph(g, "05_network/tf_target_network.graphml", format = "graphml")
```

图例解释：

| 元素 | 含义 |
| --- | --- |
| TF 节点 | 候选调控因子 |
| target 节点 | 被调控基因 |
| 红色边 | 激活关系 |
| 蓝色边 | 抑制关系 |
| 节点大小 | DEG 显著性或网络度 |

## 九、结果解释示例

```text
NF-kB regulon 活性在处理组升高，NFKBIA、IL6、CXCL8 等 target genes 同时上调。
ChEA3 和 motif 富集也支持 RELA/NFKB1。
因此可以提出处理激活 NF-kB 炎症调控网络的假设。
```

## 十、交付物

- ranked gene signature
- TF activity matrix
- TF enrichment results
- motif enrichment results
- integrated TF ranking
- TF-target network graphml
- top TF 机制解释表
""",
        },
        {
            "title": "GSVA/ssGSEA 通路活性评分",
            "description": "将基因表达矩阵转换为样本级通路活性矩阵，支持 GSVA、ssGSEA、PROGENy、Hallmark gene sets 和组间通路比较。",
            "omics_type": "Pathway Analysis",
            "dag_json": {
                "nodes": [
                    {"id": "project", "label": "建立通路评分项目"},
                    {"id": "matrix", "label": "表达矩阵准备"},
                    {"id": "genesets", "label": "基因集选择"},
                    {"id": "gsva", "label": "GSVA/ssGSEA 评分"},
                    {"id": "compare", "label": "组间差异通路"},
                    {"id": "heatmap", "label": "通路热图/PCA"},
                    {"id": "report", "label": "通路活性报告"},
                ],
                "edges": [
                    {"source": "project", "target": "matrix"},
                    {"source": "matrix", "target": "genesets"},
                    {"source": "genesets", "target": "gsva"},
                    {"source": "gsva", "target": "compare"},
                    {"source": "compare", "target": "heatmap"},
                    {"source": "heatmap", "target": "report"},
                ],
            },
            "content": """# GSVA/ssGSEA 通路活性评分

## 一、项目目录

```bash
mkdir -p pathway_score_project/{00_input,01_genesets,02_scores,03_statistics,04_plots,report}
```

## 二、示例数据

`00_input/expression_tpm.csv`：

```text
gene_symbol,Ctrl_1,Ctrl_2,Treat_1,Treat_2
IL6,2.1,2.4,20.5,18.9
CXCL8,1.2,1.5,15.2,14.8
GAPDH,100,98,105,101
```

`00_input/sample_info.csv`：

```text
sample_id,condition
Ctrl_1,Ctrl
Ctrl_2,Ctrl
Treat_1,Treat
Treat_2,Treat
```

## 三、整体流程图

```mermaid
flowchart TD
    A[gene x sample expression matrix] --> B[log2(TPM+1) 或 VST]
    B --> C[MSigDB Hallmark / KEGG / Reactome gene sets]
    C --> D[GSVA / ssGSEA]
    D --> E[pathway x sample score matrix]
    E --> F[limma / Wilcoxon 组间比较]
    F --> G[通路热图和箱线图]
    G --> H[通路机制解释]
```

## 四、GSVA 评分

```r
library(GSVA)
library(msigdbr)
library(tidyverse)

expr <- read.csv("00_input/expression_tpm.csv", row.names = 1, check.names = FALSE)
expr_log <- log2(as.matrix(expr) + 1)

hallmark <- msigdbr(species = "Homo sapiens", category = "H") |>
  split(x = .$gene_symbol, f = .$gs_name)

gsva_scores <- gsva(
  expr_log,
  hallmark,
  method = "gsva",
  kcdf = "Gaussian",
  verbose = FALSE
)

write.csv(gsva_scores, "02_scores/gsva_hallmark_scores.csv")
```

## 五、ssGSEA 评分

```r
ssgsea_scores <- gsva(
  expr_log,
  hallmark,
  method = "ssgsea",
  kcdf = "Gaussian",
  abs.ranking = TRUE,
  verbose = FALSE
)

write.csv(ssgsea_scores, "02_scores/ssgsea_hallmark_scores.csv")
```

## 六、组间通路差异

```r
library(limma)

sample_info <- read.csv("00_input/sample_info.csv")
sample_info <- sample_info[match(colnames(gsva_scores), sample_info$sample_id), ]

design <- model.matrix(~ 0 + condition, data = sample_info)
colnames(design) <- levels(factor(sample_info$condition))

fit <- lmFit(gsva_scores, design)
contrast <- makeContrasts(Treat_vs_Ctrl = Treat - Ctrl, levels = design)
fit2 <- contrasts.fit(fit, contrast)
fit2 <- eBayes(fit2)

pathway_res <- topTable(fit2, number = Inf)
write.csv(pathway_res, "03_statistics/gsva_Treat_vs_Ctrl.csv")
```

## 七、可视化

```r
library(pheatmap)

top_pathways <- rownames(pathway_res)[1:30]

pheatmap(
  gsva_scores[top_pathways, ],
  scale = "row",
  annotation_col = data.frame(condition = sample_info$condition, row.names = sample_info$sample_id),
  filename = "04_plots/top_pathway_heatmap.pdf",
  width = 8,
  height = 10
)
```

箱线图：

```r
pathway <- "HALLMARK_INFLAMMATORY_RESPONSE"

plot_df <- data.frame(
  score = gsva_scores[pathway, ],
  sample_info
)

ggplot(plot_df, aes(condition, score, fill = condition)) +
  geom_boxplot(width = 0.5, outlier.shape = NA) +
  geom_jitter(width = 0.08, size = 2) +
  theme_bw() +
  labs(title = pathway, y = "GSVA score")
```

## 八、结果解释示例

```text
Treat 组 inflammatory response、TNFA signaling via NF-kB 和 interferon response 分数升高，
说明处理诱导免疫炎症相关通路活化。
与 DEG 富集不同，GSVA 可以在单个样本层面比较通路活性。
```

## 九、交付物

- GSVA score matrix
- ssGSEA score matrix
- 差异通路表
- 通路热图
- 重点通路箱线图
- 样本通路 PCA
- 通路机制解释报告
""",
        },
        {
            "title": "免疫浸润分析 CIBERSORT/xCell/ESTIMATE",
            "description": "基于 bulk RNA-seq 表达矩阵估计免疫细胞浸润和肿瘤微环境状态，覆盖 CIBERSORT/xCell/MCP-counter/ESTIMATE 多方法比较和可视化解释。",
            "omics_type": "Immunogenomics",
            "dag_json": {
                "nodes": [
                    {"id": "project", "label": "建立免疫浸润项目"},
                    {"id": "matrix", "label": "TPM 表达矩阵"},
                    {"id": "method", "label": "选择 CIBERSORT/xCell/ESTIMATE"},
                    {"id": "deconv", "label": "细胞比例/分数估计"},
                    {"id": "compare", "label": "组间比较"},
                    {"id": "cor", "label": "与基因/通路相关"},
                    {"id": "plot", "label": "堆叠图/热图/箱线图"},
                    {"id": "report", "label": "免疫微环境报告"},
                ],
                "edges": [
                    {"source": "project", "target": "matrix"},
                    {"source": "matrix", "target": "method"},
                    {"source": "method", "target": "deconv"},
                    {"source": "deconv", "target": "compare"},
                    {"source": "deconv", "target": "cor"},
                    {"source": "compare", "target": "plot"},
                    {"source": "cor", "target": "plot"},
                    {"source": "plot", "target": "report"},
                ],
            },
            "content": """# 免疫浸润分析 CIBERSORT/xCell/ESTIMATE

## 一、项目目录

```bash
mkdir -p immune_infiltration_project/{00_input,01_deconvolution,02_statistics,03_plots,report}
```

## 二、示例数据

免疫浸润通常使用 gene symbol 行名、样本列名的 TPM 矩阵。

`00_input/tpm_matrix.csv`：

```text
gene_symbol,Tumor_1,Tumor_2,Normal_1,Normal_2
CD3D,20.1,18.4,5.2,4.9
MS4A1,4.2,3.8,2.1,2.0
LYZ,30.2,35.1,12.5,13.1
```

`00_input/sample_info.csv`：

```text
sample_id,group
Tumor_1,Tumor
Tumor_2,Tumor
Normal_1,Normal
Normal_2,Normal
```

## 三、整体流程图

```mermaid
flowchart TD
    A[TPM expression matrix] --> B[gene symbol cleanup]
    B --> C[CIBERSORT / xCell / MCP-counter / ESTIMATE]
    C --> D[cell fraction or immune score matrix]
    D --> E[group comparison]
    D --> F[correlation with genes/pathways]
    E --> G[boxplot / stacked bar / heatmap]
    F --> G
    G --> H[TME interpretation report]
```

## 四、immunedeconv 多方法分析

```r
library(immunedeconv)
library(tidyverse)

expr <- read.csv("00_input/tpm_matrix.csv", row.names = 1, check.names = FALSE)
expr <- as.matrix(expr)

res_xcell <- deconvolute(expr, method = "xcell", arrays = FALSE)
res_mcp <- deconvolute(expr, method = "mcp_counter")
res_estimate <- deconvolute(expr, method = "estimate")

write.csv(res_xcell, "01_deconvolution/xcell_scores.csv", row.names = FALSE)
write.csv(res_mcp, "01_deconvolution/mcp_counter_scores.csv", row.names = FALSE)
write.csv(res_estimate, "01_deconvolution/estimate_scores.csv", row.names = FALSE)
```

CIBERSORT/CIBERSORTx 可使用官方 web 或本地授权脚本。输入通常是 TPM，不建议使用 log 转换矩阵。

## 五、组间比较

```r
scores <- read.csv("01_deconvolution/xcell_scores.csv")
sample_info <- read.csv("00_input/sample_info.csv")

score_long <- scores |>
  pivot_longer(-cell_type, names_to = "sample_id", values_to = "score") |>
  left_join(sample_info, by = "sample_id")

stat <- score_long |>
  group_by(cell_type) |>
  summarise(
    pvalue = wilcox.test(score[group == "Tumor"], score[group == "Normal"])$p.value,
    mean_tumor = mean(score[group == "Tumor"]),
    mean_normal = mean(score[group == "Normal"]),
    .groups = "drop"
  ) |>
  mutate(padj = p.adjust(pvalue, method = "BH"))

write.csv(stat, "02_statistics/xcell_group_comparison.csv", row.names = FALSE)
```

## 六、可视化

```r
library(ggplot2)

ggplot(score_long |> filter(cell_type %in% c("CD8+ T-cells", "Macrophages", "B-cells")),
       aes(group, score, fill = group)) +
  geom_boxplot(width = 0.5, outlier.shape = NA) +
  geom_jitter(width = 0.08, size = 2) +
  facet_wrap(~ cell_type, scales = "free_y") +
  theme_bw()

ggsave("03_plots/immune_cell_boxplot.pdf", width = 9, height = 5)
```

堆叠图：

```r
fraction <- score_long |>
  group_by(sample_id) |>
  mutate(prop = score / sum(score)) |>
  ungroup()

ggplot(fraction, aes(sample_id, prop, fill = cell_type)) +
  geom_col(width = 0.8) +
  theme_bw() +
  labs(x = "Sample", y = "Relative proportion")
```

## 七、与基因或通路相关

```r
gene <- "PDCD1"
gene_expr <- expr[gene, ]

cor_df <- score_long |>
  group_by(cell_type) |>
  summarise(
    cor = cor(score, gene_expr[sample_id], method = "spearman"),
    pvalue = cor.test(score, gene_expr[sample_id], method = "spearman")$p.value,
    .groups = "drop"
  ) |>
  mutate(padj = p.adjust(pvalue, method = "BH"))
```

## 八、结果解释示例

```text
Tumor 组 macrophage score 升高，同时 ESTIMATE immune score 升高。
CD8 T cell score 与 PDCD1 表达正相关，提示存在 T cell exhaustion 相关免疫状态。
如果与 GSVA 的 interferon response 分数一致升高，可以增强免疫激活解释。
```

## 九、注意事项

- CIBERSORT 输出是相对比例，总和通常为 1。
- xCell/MCP-counter 更偏 enrichment score，不一定能解释为绝对比例。
- 肿瘤组织细胞状态复杂，最好结合 scRNA-seq 或空间数据验证。
- 不同算法结果可能不完全一致，应看趋势一致的细胞类型。

## 十、交付物

- immune cell score/fraction matrix
- ESTIMATE immune/stromal score
- 组间比较统计表
- 细胞比例堆叠图
- 免疫细胞箱线图
- immune score 与基因/通路相关图
- 肿瘤微环境解释报告
""",
        },
        {
            "title": "肿瘤 RNA-seq 综合分析",
            "description": "面向肿瘤 bulk RNA-seq 的综合分析流程，整合 DEG、通路活性、免疫浸润、分型、预后、融合基因和候选机制解释。",
            "omics_type": "Cancer Transcriptomics",
            "dag_json": {
                "nodes": [
                    {"id": "project", "label": "建立肿瘤项目目录"},
                    {"id": "metadata", "label": "临床信息和表达矩阵"},
                    {"id": "deg", "label": "差异表达"},
                    {"id": "pathway", "label": "通路活性"},
                    {"id": "immune", "label": "免疫浸润"},
                    {"id": "survival", "label": "预后分析"},
                    {"id": "subtype", "label": "分型/聚类"},
                    {"id": "fusion", "label": "融合基因"},
                    {"id": "report", "label": "综合报告"},
                ],
                "edges": [
                    {"source": "project", "target": "metadata"},
                    {"source": "metadata", "target": "deg"},
                    {"source": "deg", "target": "pathway"},
                    {"source": "metadata", "target": "immune"},
                    {"source": "metadata", "target": "survival"},
                    {"source": "metadata", "target": "subtype"},
                    {"source": "metadata", "target": "fusion"},
                    {"source": "pathway", "target": "report"},
                    {"source": "immune", "target": "report"},
                    {"source": "survival", "target": "report"},
                    {"source": "subtype", "target": "report"},
                    {"source": "fusion", "target": "report"},
                ],
            },
            "content": """# 肿瘤 RNA-seq 综合分析

## 一、项目目录

```bash
mkdir -p tumor_rnaseq_project/{00_clinical,01_expression,02_deg,03_pathway,04_immune,05_survival,06_subtype,07_fusion,report}
```

## 二、示例数据

`00_clinical/clinical_info.csv`：

```text
sample_id,group,stage,OS_time,OS_status
Tumor_1,Tumor,III,520,1
Tumor_2,Tumor,II,900,0
Normal_1,Normal,NA,NA,NA
Normal_2,Normal,NA,NA,NA
```

`01_expression/tpm_matrix.csv`：

```text
gene_symbol,Tumor_1,Tumor_2,Normal_1,Normal_2
MKI67,50,45,5,6
PDCD1,8,10,1,1.2
EPCAM,100,120,30,28
```

## 三、整体流程图

```mermaid
flowchart TD
    A[expression + clinical metadata] --> B[DEG]
    A --> C[GSVA/ssGSEA pathway score]
    A --> D[immune infiltration]
    A --> E[survival analysis]
    A --> F[molecular subtype clustering]
    A --> G[fusion detection]
    B --> H[integrated tumor mechanism]
    C --> H
    D --> H
    E --> H
    F --> H
    G --> H
```

## 四、差异表达

```r
library(DESeq2)

counts <- read.csv("01_expression/raw_counts.csv", row.names = 1, check.names = FALSE)
clinical <- read.csv("00_clinical/clinical_info.csv", row.names = 1)

dds <- DESeqDataSetFromMatrix(
  countData = round(as.matrix(counts)),
  colData = clinical,
  design = ~ group
)

dds <- dds[rowSums(counts(dds) >= 10) >= 3, ]
dds <- DESeq(dds)
res <- results(dds, contrast = c("group", "Tumor", "Normal"))
write.csv(as.data.frame(res), "02_deg/Tumor_vs_Normal_DESeq2.csv")
```

## 五、通路活性

```r
library(GSVA)
library(msigdbr)

tpm <- read.csv("01_expression/tpm_matrix.csv", row.names = 1, check.names = FALSE)
expr_log <- log2(as.matrix(tpm) + 1)

hallmark <- msigdbr(species = "Homo sapiens", category = "H") |>
  split(x = .$gene_symbol, f = .$gs_name)

gsva_score <- gsva(expr_log, hallmark, method = "gsva", kcdf = "Gaussian")
write.csv(gsva_score, "03_pathway/hallmark_gsva_scores.csv")
```

## 六、免疫浸润

```r
library(immunedeconv)

immune_xcell <- deconvolute(as.matrix(tpm), method = "xcell", arrays = FALSE)
estimate_score <- deconvolute(as.matrix(tpm), method = "estimate")

write.csv(immune_xcell, "04_immune/xcell_scores.csv", row.names = FALSE)
write.csv(estimate_score, "04_immune/estimate_scores.csv", row.names = FALSE)
```

## 七、预后分析

```r
library(survival)
library(survminer)

gene <- "MKI67"
clinical$expr <- as.numeric(tpm[gene, rownames(clinical)])
clinical$risk_group <- ifelse(clinical$expr >= median(clinical$expr, na.rm = TRUE), "High", "Low")

fit <- survfit(Surv(OS_time, OS_status) ~ risk_group, data = clinical)

ggsurvplot(
  fit,
  data = clinical,
  pval = TRUE,
  risk.table = TRUE
)
```

## 八、分型/聚类

```r
library(pheatmap)

top_var <- names(sort(apply(expr_log, 1, mad), decreasing = TRUE))[1:1000]
mat <- expr_log[top_var, grepl("Tumor", colnames(expr_log))]

pheatmap(
  mat,
  scale = "row",
  show_rownames = FALSE,
  filename = "06_subtype/tumor_unsupervised_clustering.pdf"
)
```

## 九、融合基因检测

STAR-Fusion 示例：

```bash
STAR-Fusion \
  --genome_lib_dir ref/ctat_genome_lib \
  --left_fq tumor_R1.fq.gz \
  --right_fq tumor_R2.fq.gz \
  --CPU 16 \
  --output_dir 07_fusion/Tumor_1
```

Arriba 示例：

```bash
arriba \
  -x tumor.Aligned.sortedByCoord.out.bam \
  -g ref/genes.gtf \
  -a ref/genome.fa \
  -o 07_fusion/Tumor_1_fusions.tsv
```

## 十、综合解释示例

```text
Tumor 组中 MKI67 上调，cell cycle 通路 GSVA 分数升高，并且高 MKI67 表达组预后更差。
同时免疫浸润分析显示 macrophage score 升高，提示该肿瘤亚型可能具有高增殖和免疫抑制特征。
如果 fusion 检测发现 driver fusion，需要与 DEG 和通路结果联合解释。
```

## 十一、交付物

- DEG 表和火山图
- Hallmark/KEGG 通路活性矩阵
- 免疫浸润分数矩阵
- 生存曲线和 Cox 结果
- 肿瘤样本分型热图
- fusion candidates
- 综合机制解释报告
""",
        },
        {
            "title": "融合基因检测 STAR-Fusion/Arriba",
            "description": "面向肿瘤 RNA-seq 的融合基因检测流程，覆盖项目目录、示例 FASTQ、STAR-Fusion、Arriba、junction/spanning reads 解读、过滤和可视化。",
            "omics_type": "Cancer Transcriptomics",
            "dag_json": {
                "nodes": [
                    {"id": "project", "label": "建立 fusion 项目目录"},
                    {"id": "fastq", "label": "示例 FASTQ 与样本表"},
                    {"id": "qc", "label": "FASTQ QC"},
                    {"id": "starfusion", "label": "STAR-Fusion 检测"},
                    {"id": "arriba", "label": "Arriba 检测"},
                    {"id": "filter", "label": "候选融合过滤"},
                    {"id": "evidence", "label": "junction/spanning reads 证据"},
                    {"id": "visual", "label": "融合可视化"},
                    {"id": "report", "label": "候选 fusion 报告"},
                ],
                "edges": [
                    {"source": "project", "target": "fastq"},
                    {"source": "fastq", "target": "qc"},
                    {"source": "qc", "target": "starfusion"},
                    {"source": "qc", "target": "arriba"},
                    {"source": "starfusion", "target": "filter"},
                    {"source": "arriba", "target": "filter"},
                    {"source": "filter", "target": "evidence"},
                    {"source": "evidence", "target": "visual"},
                    {"source": "visual", "target": "report"},
                ],
            },
            "content": """# 融合基因检测 STAR-Fusion/Arriba

## 一、项目目录

```bash
mkdir -p fusion_project/{00_metadata,01_fastq,02_qc,03_starfusion,04_arriba,05_integration,06_visualization,report}
mkdir -p fusion_project/02_qc/{fastqc,multiqc}
```

```text
fusion_project/
├── 00_metadata/
│   └── sample_info.csv
├── 01_fastq/
├── 02_qc/
├── 03_starfusion/
├── 04_arriba/
├── 05_integration/
├── 06_visualization/
└── report/
```

## 二、示例数据

`00_metadata/sample_info.csv`：

```text
sample_id,condition,fastq_1,fastq_2
Tumor_1,Tumor,01_fastq/Tumor_1_R1.fq.gz,01_fastq/Tumor_1_R2.fq.gz
Tumor_2,Tumor,01_fastq/Tumor_2_R1.fq.gz,01_fastq/Tumor_2_R2.fq.gz
Normal_1,Normal,01_fastq/Normal_1_R1.fq.gz,01_fastq/Normal_1_R2.fq.gz
```

融合候选结果示例：

```text
fusion_name,junction_reads,spanning_frags,tool
EML4--ALK,24,18,STAR-Fusion
TMPRSS2--ERG,35,21,Arriba
```

## 三、整体流程图

```mermaid
flowchart TD
    A[paired-end RNA-seq FASTQ] --> B[FastQC/MultiQC]
    B --> C[STAR-Fusion]
    B --> D[STAR + Arriba]
    C --> E[fusion candidates]
    D --> E
    E --> F[filter artifacts and recurrent false positives]
    F --> G[junction reads / spanning reads evidence]
    G --> H[visualization: arriba draw_fusions / IGV]
    H --> I[clinical or mechanism report]
```

## 四、FASTQ 质控

```bash
fastqc -t 8 -o 02_qc/fastqc 01_fastq/*.fq.gz
multiqc 02_qc/fastqc -o 02_qc/multiqc
```

融合检测对 read 长度、paired-end 信息和测序深度敏感。肿瘤样本建议优先使用 paired-end 100/150 bp。

## 五、STAR-Fusion

STAR-Fusion 依赖 CTAT genome lib。

```bash
STAR-Fusion \
  --genome_lib_dir /ref/ctat_genome_lib_build_dir \
  --left_fq 01_fastq/Tumor_1_R1.fq.gz \
  --right_fq 01_fastq/Tumor_1_R2.fq.gz \
  --CPU 16 \
  --output_dir 03_starfusion/Tumor_1
```

批量运行：

```bash
tail -n +2 00_metadata/sample_info.csv | while IFS=, read sample condition fq1 fq2
do
  STAR-Fusion \
    --genome_lib_dir /ref/ctat_genome_lib_build_dir \
    --left_fq ${fq1} \
    --right_fq ${fq2} \
    --CPU 16 \
    --output_dir 03_starfusion/${sample}
done
```

关键输出：

| 文件 | 说明 |
| --- | --- |
| `star-fusion.fusion_predictions.tsv` | 主结果表 |
| `FusionName` | 融合基因名 |
| `JunctionReadCount` | 跨断点 reads |
| `SpanningFragCount` | 支持融合的 paired fragments |

## 六、Arriba

Arriba 通常基于 STAR chimeric alignment。

```bash
STAR \
  --runThreadN 16 \
  --genomeDir /ref/star_index \
  --readFilesIn 01_fastq/Tumor_1_R1.fq.gz 01_fastq/Tumor_1_R2.fq.gz \
  --readFilesCommand zcat \
  --outSAMtype BAM Unsorted \
  --outSAMunmapped Within \
  --chimSegmentMin 10 \
  --chimOutType WithinBAM HardClip \
  --chimJunctionOverhangMin 10 \
  --alignSJDBoverhangMin 10 \
  --alignMatesGapMax 100000 \
  --alignIntronMax 100000 \
  --chimSegmentReadGapMax 3 \
  --outFileNamePrefix 04_arriba/Tumor_1_
```

```bash
arriba \
  -x 04_arriba/Tumor_1_Aligned.out.bam \
  -o 04_arriba/Tumor_1_fusions.tsv \
  -O 04_arriba/Tumor_1_fusions.discarded.tsv \
  -a /ref/genome.fa \
  -g /ref/genes.gtf \
  -b /ref/blacklist_hg38_GRCh38.tsv.gz \
  -k /ref/known_fusions_hg38_GRCh38.tsv.gz \
  -t /ref/known_fusions_hg38_GRCh38.tsv.gz
```

可视化：

```bash
draw_fusions.R \
  --fusions=04_arriba/Tumor_1_fusions.tsv \
  --alignments=04_arriba/Tumor_1_Aligned.out.bam \
  --output=06_visualization/Tumor_1_fusions.pdf \
  --annotation=/ref/genes.gtf \
  --cytobands=/ref/cytobands_hg38_GRCh38.tsv
```

## 七、整合 STAR-Fusion 与 Arriba

```python
import pandas as pd
from pathlib import Path

sf = pd.read_csv("03_starfusion/Tumor_1/star-fusion.fusion_predictions.tsv", sep="\t")
arriba = pd.read_csv("04_arriba/Tumor_1_fusions.tsv", sep="\t")

sf_simple = sf.rename(columns={
    "FusionName": "fusion_name",
    "JunctionReadCount": "junction_reads",
    "SpanningFragCount": "spanning_reads"
})[["fusion_name", "junction_reads", "spanning_reads"]]
sf_simple["tool"] = "STAR-Fusion"

arriba_simple = arriba.rename(columns={
    "#gene1": "gene1",
    "gene2": "gene2",
    "split_reads1": "junction_reads",
    "discordant_mates": "spanning_reads"
})
arriba_simple["fusion_name"] = arriba_simple["gene1"] + "--" + arriba_simple["gene2"]
arriba_simple = arriba_simple[["fusion_name", "junction_reads", "spanning_reads"]]
arriba_simple["tool"] = "Arriba"

merged = pd.concat([sf_simple, arriba_simple], ignore_index=True)
summary = merged.groupby("fusion_name").agg(
    tools=("tool", lambda x: ";".join(sorted(set(x)))),
    max_junction_reads=("junction_reads", "max"),
    max_spanning_reads=("spanning_reads", "max"),
).reset_index()

summary.to_csv("05_integration/Tumor_1_fusion_integrated.tsv", sep="\t", index=False)
```

## 八、结果解释图例

| 证据 | 含义 |
| --- | --- |
| junction reads | reads 跨越融合断点，证据强 |
| spanning reads/frags | paired-end 两端分别落在两个基因，支持融合 |
| in-frame | 可能形成融合蛋白 |
| recurrent fusion | 文献/数据库中反复出现，可信度更高 |
| normal 样本存在 | 需警惕假阳性或 read-through |

## 九、候选过滤建议

```text
junction_reads >= 3
spanning_reads >= 5
至少一个工具 high confidence
优先保留已知 cancer fusion 或 in-frame fusion
去除 read-through、同源基因、线粒体、低复杂度区域假阳性
```

## 十、交付物

- STAR-Fusion 结果表
- Arriba 结果表
- integrated fusion candidate table
- junction/spanning reads 证据表
- fusion visualization PDF
- IGV 截图或断点浏览图
- 高可信融合基因解释报告
""",
        },
        {
            "title": "RNA editing 分析：A-to-I editing",
            "description": "面向神经、肿瘤和免疫 RNA-seq 的 A-to-I RNA editing 分析流程，覆盖 DNA/RNA 区分、REDItools/GIREMI、位点过滤、SnpEff/ANNOVAR 注释和功能解释。",
            "omics_type": "RNA-Seq",
            "dag_json": {
                "nodes": [
                    {"id": "project", "label": "建立 RNA editing 项目"},
                    {"id": "alignment", "label": "RNA-seq 比对与预处理"},
                    {"id": "dna_filter", "label": "DNA/SNP 数据过滤"},
                    {"id": "reditools", "label": "REDItools calling"},
                    {"id": "giremi", "label": "GIREMI 候选位点"},
                    {"id": "filter", "label": "A-to-I 位点过滤"},
                    {"id": "annotate", "label": "SnpEff/ANNOVAR 注释"},
                    {"id": "visual", "label": "editing level 可视化"},
                    {"id": "report", "label": "功能解释报告"},
                ],
                "edges": [
                    {"source": "project", "target": "alignment"},
                    {"source": "alignment", "target": "dna_filter"},
                    {"source": "alignment", "target": "reditools"},
                    {"source": "alignment", "target": "giremi"},
                    {"source": "dna_filter", "target": "filter"},
                    {"source": "reditools", "target": "filter"},
                    {"source": "giremi", "target": "filter"},
                    {"source": "filter", "target": "annotate"},
                    {"source": "annotate", "target": "visual"},
                    {"source": "visual", "target": "report"},
                ],
            },
            "content": """# RNA editing 分析：A-to-I editing

## 一、项目目录

```bash
mkdir -p rna_editing_project/{00_metadata,01_alignment,02_variant_filter,03_reditools,04_giremi,05_annotation,06_plots,report}
```

## 二、示例数据

`00_metadata/sample_info.csv`：

```text
sample_id,group,rna_bam,dna_vcf
Brain_1,Case,01_alignment/Brain_1.rna.bam,02_variant_filter/Brain_1.dna.vcf.gz
Brain_2,Control,01_alignment/Brain_2.rna.bam,02_variant_filter/Brain_2.dna.vcf.gz
```

候选 editing 位点示例：

```text
chrom,pos,ref,alt,gene,editing_level,coverage
chr1,100100,A,G,GRIA2,0.42,86
chr2,200500,T,C,AZIN1,0.31,65
```

## 三、整体流程图

```mermaid
flowchart TD
    A[RNA-seq FASTQ] --> B[STAR/HISAT2 比对]
    B --> C[sorted BAM + duplicates/QC]
    C --> D[REDItools / GIREMI calling]
    E[matched DNA VCF or SNP database] --> F[remove genomic SNPs]
    D --> F
    F --> G[keep A-to-G / T-to-C candidates]
    G --> H[coverage/editing level filters]
    H --> I[SnpEff / ANNOVAR annotation]
    I --> J[group comparison and plots]
    J --> K[editing report]
```

## 四、RNA-seq 比对

```bash
STAR \
  --runThreadN 16 \
  --genomeDir ref/star_index \
  --readFilesIn sample_R1.fq.gz sample_R2.fq.gz \
  --readFilesCommand zcat \
  --outSAMtype BAM SortedByCoordinate \
  --outFileNamePrefix 01_alignment/Brain_1_

samtools index 01_alignment/Brain_1_Aligned.sortedByCoord.out.bam
```

## 五、REDItools calling

```bash
python REDItoolDnaRna.py \
  -i 01_alignment/Brain_1_Aligned.sortedByCoord.out.bam \
  -f ref/genome.fa \
  -o 03_reditools/Brain_1 \
  -t 12 \
  -m 20 \
  -q 25 \
  -c 10
```

常用过滤含义：

| 参数 | 含义 |
| --- | --- |
| `-m` | mapping quality |
| `-q` | base quality |
| `-c` | minimum coverage |

## 六、GIREMI 思路

GIREMI 常用于在缺少 matched DNA 时利用 allelic linkage 和 RNA-seq 信息推断 editing 位点。

```bash
GIREMI \
  -f ref/genome.fa \
  -l known_snp.vcf \
  -o 04_giremi/Brain_1.giremi.txt \
  01_alignment/Brain_1_Aligned.sortedByCoord.out.bam
```

## 七、A-to-I 位点过滤

A-to-I 在正链表现为 A>G，在负链常表现为 T>C。

```python
import pandas as pd

df = pd.read_csv("03_reditools/Brain_1/reditools_table.tsv", sep="\t")

filtered = df[
    (df["coverage"] >= 10)
    & (df["editing_level"] >= 0.05)
    & (
        ((df["ref"] == "A") & (df["alt"] == "G"))
        | ((df["ref"] == "T") & (df["alt"] == "C"))
    )
].copy()

known_snp = pd.read_csv("02_variant_filter/known_snp_sites.tsv", sep="\t")
filtered = filtered.merge(
    known_snp[["chrom", "pos"]],
    on=["chrom", "pos"],
    how="left",
    indicator=True
)
filtered = filtered[filtered["_merge"] == "left_only"].drop(columns="_merge")

filtered.to_csv("03_reditools/Brain_1_AtoI_filtered.tsv", sep="\t", index=False)
```

## 八、SnpEff/ANNOVAR 注释

```bash
java -jar snpEff.jar \
  GRCh38.99 \
  03_reditools/Brain_1_AtoI_filtered.vcf \
  > 05_annotation/Brain_1_AtoI.snpeff.vcf
```

ANNOVAR：

```bash
table_annovar.pl \
  Brain_1_AtoI.avinput \
  humandb/ \
  -buildver hg38 \
  -out 05_annotation/Brain_1_AtoI \
  -remove \
  -protocol refGene,avsnp150,dbnsfp42a \
  -operation g,f,f \
  -nastring .
```

## 九、editing level 可视化

```r
library(tidyverse)

edit <- read.delim("03_reditools/Brain_1_AtoI_filtered.tsv")

ggplot(edit, aes(editing_level)) +
  geom_histogram(bins = 40, fill = "#2c7fb8", color = "white") +
  theme_bw() +
  labs(x = "Editing level", y = "Site count")
```

组间比较：

```r
editing_matrix <- read.csv("editing_level_matrix.csv", row.names = 1)
sample_info <- read.csv("00_metadata/sample_info.csv")

site <- "chr1:100100"
plot_df <- data.frame(
  editing_level = as.numeric(editing_matrix[site, sample_info$sample_id]),
  group = sample_info$group
)

ggplot(plot_df, aes(group, editing_level, fill = group)) +
  geom_boxplot(width = 0.5) +
  geom_jitter(width = 0.08, size = 2) +
  theme_bw()
```

## 十、结果解释图例

| 指标 | 解释 |
| --- | --- |
| coverage | 覆盖该位点的 reads 数 |
| editing level | alt reads / total reads |
| A>G / T>C | A-to-I editing 典型表现 |
| nonsynonymous | 可能改变蛋白序列 |
| Alu/repeat region | 人类 A-to-I editing 常见区域 |

## 十一、交付物

- RNA BAM QC
- REDItools/GIREMI 原始候选表
- 去 SNP 后 A-to-I editing 位点表
- editing level matrix
- SnpEff/ANNOVAR 注释表
- 组间差异 editing 位点
- editing level 分布图和箱线图
- 重点位点 IGV 截图和报告
""",
        },
        {
            "title": "长读长转录组 Iso-Seq/Nanopore",
            "description": "面向 PacBio Iso-Seq 和 Oxford Nanopore cDNA/direct RNA 的长读长转录组流程，覆盖 isoform discovery、FLAIR/TALON/StringTie2、alternative promoter/polyA 和表达定量。",
            "omics_type": "Long-read Transcriptomics",
            "dag_json": {
                "nodes": [
                    {"id": "project", "label": "建立长读长项目"},
                    {"id": "qc", "label": "reads QC"},
                    {"id": "align", "label": "minimap2 比对"},
                    {"id": "collapse", "label": "isoform collapse"},
                    {"id": "flair", "label": "FLAIR/TALON/StringTie2"},
                    {"id": "quant", "label": "isoform 定量"},
                    {"id": "apa", "label": "promoter/polyA 分析"},
                    {"id": "annotation", "label": "novel isoform 注释"},
                    {"id": "report", "label": "isoform 报告"},
                ],
                "edges": [
                    {"source": "project", "target": "qc"},
                    {"source": "qc", "target": "align"},
                    {"source": "align", "target": "collapse"},
                    {"source": "collapse", "target": "flair"},
                    {"source": "flair", "target": "quant"},
                    {"source": "flair", "target": "apa"},
                    {"source": "quant", "target": "annotation"},
                    {"source": "apa", "target": "annotation"},
                    {"source": "annotation", "target": "report"},
                ],
            },
            "content": """# 长读长转录组 Iso-Seq/Nanopore

## 一、项目目录

```bash
mkdir -p longread_tx_project/{00_metadata,01_reads,02_qc,03_alignment,04_isoforms,05_quant,06_annotation,07_polyA,report}
```

## 二、示例数据

`00_metadata/sample_info.csv`：

```text
sample_id,platform,condition,reads
Sample_1,PacBio_IsoSeq,Ctrl,01_reads/Sample_1.hifi.fastq.gz
Sample_2,ONT_cDNA,Treat,01_reads/Sample_2.fastq.gz
```

isoform 表示例：

```text
isoform_id,gene_id,category,length
PB.1.1,GENE1,known,2400
PB.1.2,GENE1,novel_exon_combination,3100
```

## 三、整体流程图

```mermaid
flowchart TD
    A[PacBio HiFi / ONT reads] --> B[read QC]
    B --> C[minimap2 splice alignment]
    C --> D[FLAIR correct/collapse 或 TALON]
    D --> E[isoform annotation]
    D --> F[isoform quantification]
    E --> G[novel isoform discovery]
    E --> H[alternative promoter/polyA]
    F --> I[differential isoform usage]
    G --> J[isoform report]
    H --> J
    I --> J
```

## 四、minimap2 比对

```bash
minimap2 -ax splice -uf -k14 \
  ref/genome.fa \
  01_reads/Sample_1.hifi.fastq.gz \
  | samtools sort -@ 8 -o 03_alignment/Sample_1.sorted.bam

samtools index 03_alignment/Sample_1.sorted.bam
```

ONT cDNA：

```bash
minimap2 -ax splice \
  ref/genome.fa \
  01_reads/Sample_2.fastq.gz \
  | samtools sort -@ 8 -o 03_alignment/Sample_2.sorted.bam
```

## 五、FLAIR 流程

```bash
flair correct \
  -q 03_alignment/Sample_1.sorted.bam \
  -g ref/genome.fa \
  -f ref/genes.gtf \
  -o 04_isoforms/Sample_1
```

```bash
flair collapse \
  -g ref/genome.fa \
  -r 01_reads/Sample_1.hifi.fastq.gz \
  -q 04_isoforms/Sample_1_all_corrected.bed \
  -f ref/genes.gtf \
  -o 04_isoforms/Sample_1_flair
```

```bash
flair quantify \
  -r reads_manifest.tsv \
  -i 04_isoforms/Sample_1_flair.isoforms.fa \
  -o 05_quant/flair_quant
```

## 六、TALON 思路

TALON 适合对长读长转录本进行注释分类。

```bash
talon_initialize_database \
  --f ref/genes.gtf \
  --g hg38 \
  --a gencode \
  --o 06_annotation/talon

talon \
  --f 03_alignment/Sample_1.sorted.bam \
  --db 06_annotation/talon.db \
  --build hg38 \
  --o 06_annotation/Sample_1_talon
```

## 七、StringTie2 长读长组装

```bash
stringtie \
  -L \
  -G ref/genes.gtf \
  -o 04_isoforms/Sample_1_stringtie2.gtf \
  03_alignment/Sample_1.sorted.bam
```

## 八、alternative promoter/polyA

长读长可以直接观察 transcript start site 和 polyA site。

```python
import pandas as pd

isoforms = pd.read_csv("06_annotation/isoform_annotation.tsv", sep="\t")

apa = isoforms.groupby("gene_id")["polyA_site"].nunique().reset_index()
apa = apa.rename(columns={"polyA_site": "polyA_site_count"})
apa = apa[apa["polyA_site_count"] >= 2]

apa.to_csv("07_polyA/genes_with_multiple_polyA.tsv", sep="\t", index=False)
```

## 九、图例解释

| 类别 | 含义 |
| --- | --- |
| full-splice match | 与已知转录本剪接结构完全匹配 |
| novel in catalog | 使用已知 splice junction 的新组合 |
| novel not in catalog | 包含新的 splice junction |
| alternative promoter | 同一基因使用不同 TSS |
| alternative polyA | 同一基因使用不同 polyA site |

## 十、交付物

- long-read QC 报告
- sorted BAM 和 index
- isoform GTF/FASTA
- isoform annotation table
- novel isoform list
- isoform count/TPM matrix
- alternative promoter/polyA 表
- differential isoform usage 结果
- 重点基因 isoform browser plot
""",
        },
        {
            "title": "Ribo-seq 翻译组分析",
            "description": "面向 ribosome profiling 的翻译组分析流程，覆盖 RPF 质控、rRNA/tRNA 去除、比对、P-site 校正、三核苷酸周期性、ORF 检测和翻译效率分析。",
            "omics_type": "Translatomics",
            "dag_json": {
                "nodes": [
                    {"id": "project", "label": "建立 Ribo-seq 项目"},
                    {"id": "trim", "label": "adapter trimming"},
                    {"id": "filter", "label": "rRNA/tRNA 过滤"},
                    {"id": "align", "label": "基因组/转录组比对"},
                    {"id": "periodicity", "label": "三核苷酸周期性"},
                    {"id": "psite", "label": "P-site 校正"},
                    {"id": "orf", "label": "ORF 检测"},
                    {"id": "te", "label": "翻译效率 TE"},
                    {"id": "report", "label": "翻译组报告"},
                ],
                "edges": [
                    {"source": "project", "target": "trim"},
                    {"source": "trim", "target": "filter"},
                    {"source": "filter", "target": "align"},
                    {"source": "align", "target": "periodicity"},
                    {"source": "periodicity", "target": "psite"},
                    {"source": "psite", "target": "orf"},
                    {"source": "psite", "target": "te"},
                    {"source": "orf", "target": "report"},
                    {"source": "te", "target": "report"},
                ],
            },
            "content": """# Ribo-seq 翻译组分析

## 一、项目目录

```bash
mkdir -p riboseq_project/{00_metadata,01_fastq,02_trimmed,03_filter_rrna,04_alignment,05_qc,06_counts,07_te,08_orf,report}
```

## 二、示例数据

```text
sample_id,assay,condition,fastq
Ctrl_Ribo_1,Ribo-seq,Ctrl,01_fastq/Ctrl_Ribo_1.fq.gz
Treat_Ribo_1,Ribo-seq,Treat,01_fastq/Treat_Ribo_1.fq.gz
Ctrl_RNA_1,RNA-seq,Ctrl,01_fastq/Ctrl_RNA_1_R1.fq.gz
Treat_RNA_1,RNA-seq,Treat,01_fastq/Treat_RNA_1_R1.fq.gz
```

## 三、整体流程图

```mermaid
flowchart TD
    A[Ribo-seq FASTQ] --> B[adapter trimming]
    B --> C[length filtering 26-34 nt]
    C --> D[remove rRNA/tRNA reads]
    D --> E[align to genome/transcriptome]
    E --> F[read length distribution and periodicity]
    F --> G[P-site offset correction]
    G --> H[RPF count matrix]
    H --> I[ORF detection]
    J[matched RNA-seq count] --> K[translation efficiency]
    H --> K
    I --> L[translation report]
    K --> L
```

## 四、接头过滤和长度筛选

```bash
cutadapt \
  -a CTGTAGGCACCATCAAT \
  -m 26 \
  -M 34 \
  -o 02_trimmed/Ctrl_Ribo_1.trimmed.fq.gz \
  01_fastq/Ctrl_Ribo_1.fq.gz
```

Ribo-seq footprints 通常集中在 28-32 nt 左右，不同物种和实验可能略有变化。

## 五、去除 rRNA/tRNA

```bash
bowtie \
  -p 8 \
  -v 2 \
  --un 03_filter_rrna/Ctrl_Ribo_1.no_rrna.fq \
  ref/rrna_trna_index \
  02_trimmed/Ctrl_Ribo_1.trimmed.fq.gz \
  > 03_filter_rrna/Ctrl_Ribo_1.rrna.sam
```

## 六、比对

```bash
STAR \
  --runThreadN 12 \
  --genomeDir ref/star_index \
  --readFilesIn 03_filter_rrna/Ctrl_Ribo_1.no_rrna.fq \
  --outSAMtype BAM SortedByCoordinate \
  --outFilterMultimapNmax 1 \
  --outFileNamePrefix 04_alignment/Ctrl_Ribo_1_

samtools index 04_alignment/Ctrl_Ribo_1_Aligned.sortedByCoord.out.bam
```

## 七、周期性和 P-site QC

```r
library(riboWaltz)

annotation_dt <- create_annotation(gtfpath = "ref/genes.gtf")

bam_list <- bamtolist(
  bamfolder = "04_alignment",
  annotation = annotation_dt
)

psite_offset <- psite(bam_list)

rlength_distr(bam_list, sample = "Ctrl_Ribo_1")
frame_psite_length(bam_list, sample = "Ctrl_Ribo_1")
```

图例解释：

| QC | 理想表现 |
| --- | --- |
| read length distribution | 28-32 nt 有明显峰 |
| trinucleotide periodicity | CDS 中 0 frame 富集 |
| metagene plot | start/stop codon 附近有合理分布 |

## 八、RPF count 和翻译效率 TE

```r
library(DESeq2)

ribo_counts <- read.csv("06_counts/ribo_counts.csv", row.names = 1)
rna_counts <- read.csv("06_counts/rna_counts.csv", row.names = 1)

combined <- cbind(ribo_counts, rna_counts)

sample_info <- data.frame(
  sample = colnames(combined),
  condition = rep(c("Ctrl", "Treat"), times = 2),
  assay = c(rep("Ribo", ncol(ribo_counts)), rep("RNA", ncol(rna_counts)))
)
rownames(sample_info) <- sample_info$sample

dds <- DESeqDataSetFromMatrix(
  countData = combined,
  colData = sample_info,
  design = ~ assay + condition + assay:condition
)

dds <- DESeq(dds, test = "LRT", reduced = ~ assay + condition)
res_te <- results(dds)
write.csv(as.data.frame(res_te), "07_te/translation_efficiency_DESeq2.csv")
```

解释：

```text
RNA-seq 上调 + Ribo-seq 上调：转录和翻译同步增强。
RNA-seq 不变 + Ribo-seq 上调：可能存在翻译效率增强。
RNA-seq 上调 + Ribo-seq 不变：转录变化未传递到翻译层面。
```

## 九、ORF 检测

常用工具包括 RiboTaper、RiboCode、ORFquant。

```bash
RiboCode \
  -a ref/transcripts.gtf \
  -c 04_alignment/config.txt \
  -l no \
  -g \
  -o 08_orf/ribocode_ORFs
```

## 十、交付物

- trimmed RPF reads
- rRNA/tRNA 过滤统计
- Ribo-seq BAM
- read length distribution
- 三核苷酸周期性图
- P-site offset 表
- RPF count matrix
- translation efficiency 结果
- ORF/uORF 候选表
- 翻译调控机制报告
""",
        },
        {
            "title": "De novo 转录组组装 Trinity",
            "description": "面向非模式物种无参考基因组的 Trinity de novo 转录组组装流程，覆盖 reads 质控、组装、去冗余、完整性评估、功能注释、表达定量和差异表达。",
            "omics_type": "De novo Transcriptomics",
            "dag_json": {
                "nodes": [
                    {"id": "project", "label": "建立 de novo 项目"},
                    {"id": "qc", "label": "reads QC/clean"},
                    {"id": "trinity", "label": "Trinity 组装"},
                    {"id": "quality", "label": "组装质量评估"},
                    {"id": "annotation", "label": "功能注释"},
                    {"id": "quant", "label": "Salmon/RSEM 定量"},
                    {"id": "de", "label": "差异表达"},
                    {"id": "enrichment", "label": "富集分析"},
                    {"id": "report", "label": "组装报告"},
                ],
                "edges": [
                    {"source": "project", "target": "qc"},
                    {"source": "qc", "target": "trinity"},
                    {"source": "trinity", "target": "quality"},
                    {"source": "quality", "target": "annotation"},
                    {"source": "trinity", "target": "quant"},
                    {"source": "quant", "target": "de"},
                    {"source": "annotation", "target": "enrichment"},
                    {"source": "de", "target": "enrichment"},
                    {"source": "enrichment", "target": "report"},
                ],
            },
            "content": """# De novo 转录组组装 Trinity

## 一、项目目录

```bash
mkdir -p trinity_denovo_project/{00_metadata,01_raw_data,02_clean_data,03_trinity,04_quality,05_annotation,06_quant,07_differential,08_enrichment,report}
```

## 二、示例数据

```text
sample_id,condition,fastq_1,fastq_2
Ctrl_1,Ctrl,01_raw_data/Ctrl_1_R1.fq.gz,01_raw_data/Ctrl_1_R2.fq.gz
Ctrl_2,Ctrl,01_raw_data/Ctrl_2_R1.fq.gz,01_raw_data/Ctrl_2_R2.fq.gz
Treat_1,Treat,01_raw_data/Treat_1_R1.fq.gz,01_raw_data/Treat_1_R2.fq.gz
Treat_2,Treat,01_raw_data/Treat_2_R1.fq.gz,01_raw_data/Treat_2_R2.fq.gz
```

## 三、整体流程图

```mermaid
flowchart TD
    A[raw FASTQ] --> B[fastp/FastQC/MultiQC]
    B --> C[Trinity de novo assembly]
    C --> D[TransRate / BUSCO / N50]
    C --> E[CD-HIT / Corset optional clustering]
    D --> F[TransDecoder ORF prediction]
    F --> G[BLAST/InterProScan/eggNOG annotation]
    C --> H[Salmon/RSEM quantification]
    H --> I[Differential expression]
    G --> J[GO/KEGG enrichment]
    I --> J
    J --> K[de novo transcriptome report]
```

## 四、质控和清洗

```bash
fastqc -t 8 -o 04_quality/raw_fastqc 01_raw_data/*.fq.gz

for sample in Ctrl_1 Ctrl_2 Treat_1 Treat_2
do
  fastp \
    -i 01_raw_data/${sample}_R1.fq.gz \
    -I 01_raw_data/${sample}_R2.fq.gz \
    -o 02_clean_data/${sample}_R1.clean.fq.gz \
    -O 02_clean_data/${sample}_R2.clean.fq.gz \
    --detect_adapter_for_pe \
    --thread 8 \
    --html 04_quality/${sample}.fastp.html
done

multiqc 04_quality -o 04_quality/multiqc
```

## 五、Trinity 组装

准备 reads 列表：

```bash
ls 02_clean_data/*_R1.clean.fq.gz | paste -sd, - > left_reads.txt
ls 02_clean_data/*_R2.clean.fq.gz | paste -sd, - > right_reads.txt
```

运行 Trinity：

```bash
Trinity \
  --seqType fq \
  --left $(cat left_reads.txt) \
  --right $(cat right_reads.txt) \
  --CPU 24 \
  --max_memory 150G \
  --output 03_trinity/trinity_out
```

输出：

```text
03_trinity/trinity_out/Trinity.fasta
```

## 六、组装质量评估

```bash
TrinityStats.pl 03_trinity/trinity_out/Trinity.fasta \
  > 04_quality/trinity_stats.txt
```

BUSCO：

```bash
busco \
  -i 03_trinity/trinity_out/Trinity.fasta \
  -l metazoa_odb10 \
  -m transcriptome \
  -o 04_quality/busco_trinity \
  -c 16
```

图例解释：

| 指标 | 含义 |
| --- | --- |
| N50 | contig/transcript 连续性指标，不是越高越好 |
| BUSCO Complete | 保守单拷贝基因完整性 |
| duplicated BUSCO | 可能来自 isoform 或冗余组装 |
| mapping rate | clean reads 回贴组装结果的比例 |

## 七、ORF 和功能注释

```bash
TransDecoder.LongOrfs \
  -t 03_trinity/trinity_out/Trinity.fasta

TransDecoder.Predict \
  -t 03_trinity/trinity_out/Trinity.fasta
```

BLAST 注释：

```bash
blastx \
  -query 03_trinity/trinity_out/Trinity.fasta \
  -db swissprot \
  -out 05_annotation/trinity_vs_swissprot.tsv \
  -evalue 1e-5 \
  -num_threads 16 \
  -outfmt 6
```

eggNOG-mapper：

```bash
emapper.py \
  -i 03_trinity/trinity_out/Trinity.fasta.transdecoder.pep \
  --itype proteins \
  -o 05_annotation/eggnog \
  --cpu 16
```

## 八、表达定量

```bash
salmon index \
  -t 03_trinity/trinity_out/Trinity.fasta \
  -i 06_quant/trinity_salmon_index \
  -p 12

for sample in Ctrl_1 Ctrl_2 Treat_1 Treat_2
do
  salmon quant \
    -i 06_quant/trinity_salmon_index \
    -l A \
    -1 02_clean_data/${sample}_R1.clean.fq.gz \
    -2 02_clean_data/${sample}_R2.clean.fq.gz \
    -p 12 \
    --validateMappings \
    -o 06_quant/${sample}
done
```

生成矩阵：

```bash
abundance_estimates_to_matrix.pl \
  --est_method salmon \
  --out_prefix 06_quant/trinity \
  --name_sample_by_basedir \
  06_quant/Ctrl_1/quant.sf \
  06_quant/Ctrl_2/quant.sf \
  06_quant/Treat_1/quant.sf \
  06_quant/Treat_2/quant.sf
```

## 九、差异表达

```bash
run_DE_analysis.pl \
  --matrix 06_quant/trinity.isoform.counts.matrix \
  --method DESeq2 \
  --samples_file 00_metadata/sample_info.txt \
  --output 07_differential/DESeq2
```

R 中进一步整理：

```r
library(DESeq2)

counts <- read.delim("06_quant/trinity.isoform.counts.matrix", row.names = 1)
sample_info <- read.delim("00_metadata/sample_info.txt", row.names = 1)

dds <- DESeqDataSetFromMatrix(
  countData = round(as.matrix(counts)),
  colData = sample_info,
  design = ~ condition
)

dds <- dds[rowSums(counts(dds) >= 10) >= 2, ]
dds <- DESeq(dds)
res <- results(dds, contrast = c("condition", "Treat", "Ctrl"))
write.csv(as.data.frame(res), "07_differential/Treat_vs_Ctrl_DESeq2.csv")
```

## 十、结果解释示例

```text
Trinity 组装得到 120,000 transcripts，BUSCO complete 为 86%。
Treat_vs_Ctrl 中 3,200 个 transcript 显著上调，富集到 phenylpropanoid biosynthesis。
由于没有参考基因组，应优先报告 transcript-level 结果，并对关键 transcript 做 BLAST/ORF 注释确认。
```

## 十一、交付物

- clean reads 和 MultiQC
- Trinity.fasta
- TrinityStats 和 BUSCO 报告
- TransDecoder ORF 结果
- BLAST/eggNOG/InterProScan 注释
- Salmon/RSEM expression matrix
- DEG transcript table
- GO/KEGG 富集结果
- 非模式物种转录组分析报告
""",
        },
        {
            "title": "RNA-seq Salmon + tximport + DESeq2",
            "description": "基于 Salmon 转录本准比对定量、tximport 基因层汇总和 DESeq2 差异表达分析的快速 RNA-seq 流程。",
            "omics_type": "RNA-Seq",
            "dag_json": {
                "nodes": [
                    {"id": "reference", "label": "下载参考转录组"},
                    {"id": "salmon_index", "label": "Salmon 构建索引"},
                    {"id": "salmon_quant", "label": "Salmon paired-end 定量"},
                    {"id": "tx2gene", "label": "GTF 生成 tx2gene"},
                    {"id": "tximport", "label": "tximport 基因层导入"},
                    {"id": "deseq2", "label": "DESeq2 差异分析"},
                    {"id": "visualization", "label": "火山图与热图"},
                ],
                "edges": [
                    {"source": "reference", "target": "salmon_index"},
                    {"source": "salmon_index", "target": "salmon_quant"},
                    {"source": "reference", "target": "tx2gene"},
                    {"source": "salmon_quant", "target": "tximport"},
                    {"source": "tx2gene", "target": "tximport"},
                    {"source": "tximport", "target": "deseq2"},
                    {"source": "deseq2", "target": "visualization"},
                ],
            },
            "content": """# RNA-seq Salmon + tximport + DESeq2

## 适用场景
适用于 bulk RNA-seq 项目中需要快速、轻量地完成转录本准比对定量和基因层差异表达分析的场景。Salmon 负责 transcript-level quantification，tximport 将转录本结果按 `tx2gene` 汇总到 gene-level，DESeq2 负责统计建模与差异分析。

本流程样本包括 `adc1-1`、`adc1-2`、`adc1-3`、`adc2-1`、`adc2-2`、`adc2-3`、`WT-1`、`WT-2`、`WT-3`，比较组包括 `adc1_vs_WT`、`adc2_vs_WT`、`adc2_vs_adc1`。

## 1. 下载参考转录组并构建 Salmon 索引
```bash
curl ftp://ftp.ensemblgenomes.org/pub/plants/release-28/fasta/arabidopsis_thaliana/cdna/Arabidopsis_thaliana.TAIR10.28.cdna.all.fa.gz \
  -o athal.fa.gz
```

```bash
REF_DIR="ref_genomic"
INDEX_DIR="ref_genomic_salmon"
THREADS=8

salmon index \
  -t ${REF_DIR}/Arabidopsis_thaliana.TAIR10.dna.toplevel.fa \
  -i ${INDEX_DIR} \
  --gencode \
  -p ${THREADS}

bsub -J salmon_index -n 8 -R "span[hosts=1]" -o %J.out -e %J.err -q normal "bash salmon_index.sh"
```

## 2. Salmon paired-end 定量
```bash
INDEX_DIR="ref_genomic_salmon"
RAW_DATA_DIR="02_clean_data"
QUANT_DIR="05_salmon"
THREADS=12
LOG_DIR="logs"

SAMPLES=("adc1-1" "adc1-2" "adc1-3" "adc2-1" "adc2-2" "adc2-3" "WT-1" "WT-2" "WT-3")

for sample in "${SAMPLES[@]}"
do
  SAMPLE_OUTDIR="${QUANT_DIR}/${sample}"
  mkdir -p ${SAMPLE_OUTDIR}

  salmon quant \
    -i ${INDEX_DIR} \
    -l A \
    -1 ${RAW_DATA_DIR}/${sample}_R1_paired.fq.gz \
    -2 ${RAW_DATA_DIR}/${sample}_R2_paired.fq.gz \
    -p ${THREADS} \
    --validateMappings \
    --gcBias \
    --seqBias \
    -o ${SAMPLE_OUTDIR} \
    > ${LOG_DIR}/salmon_${sample}.log 2>&1
done

bsub -J salmon -n 12 -R "span[hosts=1]" -o %J.out -e %J.err -q normal "bash salmon_quant_loop.sh"
```

## 3. 创建样本信息表
```r
sample_names <- c(
  "adc1-1", "adc1-2", "adc1-3",
  "adc2-1", "adc2-2", "adc2-3",
  "WT-1", "WT-2", "WT-3"
)

sample_info <- data.frame(
  sample_id = sample_names,
  condition = factor(c(rep("adc1", 3), rep("adc2", 3), rep("WT", 3))),
  stringsAsFactors = FALSE
)

sample_info$quant_file <- file.path("05_salmon_quant", sample_info$sample_id, "quant.sf")
all(file.exists(sample_info$quant_file))
```

## 4. 从 GTF 生成 tx2gene 并导入 Salmon 结果
```r
library(tximport)
library(DESeq2)
library(GenomicFeatures)
library(org.At.tair.db)

txdb <- makeTxDbFromGFF("Arabidopsis_thaliana.TAIR10.57.gtf", format = "gtf")

tx2gene <- select(
  txdb,
  keys = keys(txdb, "TXNAME"),
  keytype = "TXNAME",
  columns = "GENEID"
)

txi <- tximport(
  sample_info$quant_file,
  type = "salmon",
  tx2gene = tx2gene,
  countsFromAbundance = "lengthScaledTPM"
)

colnames(txi$counts) <- sample_names
colnames(txi$abundance) <- sample_names
colnames(txi$length) <- sample_names

tpm_data <- txi$abundance
write.csv(tpm_data, "05_salmon_quant/tables/tpm_data_all_genes.csv")
```

## 5. DESeq2 差异分析
```r
dds <- DESeqDataSetFromTximport(
  txi,
  colData = sample_info,
  design = ~ condition
)

keep <- rowSums(counts(dds) >= 10) >= 3
dds <- dds[keep, ]
dds <- DESeq(dds)

comparisons <- list(
  adc1_vs_WT = c("condition", "adc1", "WT"),
  adc2_vs_WT = c("condition", "adc2", "WT"),
  adc2_vs_adc1 = c("condition", "adc2", "adc1")
)
```

```r
add_gene_annotation <- function(gene_df) {
  gene_ids <- gene_df$gene
  gene_df$symbol <- mapIds(org.At.tair.db, keys = gene_ids, column = "SYMBOL", keytype = "TAIR", multiVals = "first")[gene_ids]
  gene_df$description <- mapIds(org.At.tair.db, keys = gene_ids, column = "GENENAME", keytype = "TAIR", multiVals = "first")[gene_ids]
  gene_df
}

normalized_counts <- counts(dds, normalized = TRUE)
tpm_filtered <- tpm_data[rownames(dds), ]

for (contrast_name in names(comparisons)) {
  contrast_dir <- file.path("05_salmon_quant/tables", contrast_name)
  dir.create(contrast_dir, showWarnings = FALSE, recursive = TRUE)

  res <- results(dds, contrast = comparisons[[contrast_name]], alpha = 0.05, lfcThreshold = 1)
  resLFC <- lfcShrink(dds, contrast = comparisons[[contrast_name]], type = "ashr", res = res)

  res_df <- as.data.frame(resLFC)
  res_df$gene <- rownames(res_df)
  res_df <- add_gene_annotation(res_df)

  norm_counts_df <- as.data.frame(normalized_counts)
  norm_counts_df$gene <- rownames(norm_counts_df)
  tpm_df <- as.data.frame(tpm_filtered)
  tpm_df$gene <- rownames(tpm_df)

  res_combined <- merge(res_df, norm_counts_df, by = "gene", all.x = TRUE)
  res_combined <- merge(res_combined, tpm_df, by = "gene", all.x = TRUE)

  sig_genes <- res_combined |>
    dplyr::filter(padj < 0.05 & abs(log2FoldChange) > 1) |>
    dplyr::arrange(padj, dplyr::desc(abs(log2FoldChange)))

  write.csv(res_combined, file.path(contrast_dir, paste0(contrast_name, "_full_results.csv")), row.names = FALSE, na = "")
  write.csv(sig_genes, file.path(contrast_dir, paste0(contrast_name, "_significant_genes.csv")), row.names = FALSE, na = "")
}
```

## 6. 火山图和热图
```r
library(ggplot2)
library(ggrepel)
library(pheatmap)
library(dplyr)

create_ggplot_volcano <- function(res_df, contrast_name, top_n = 20) {
  volcano_data <- res_df |>
    mutate(
      significance = case_when(
        padj < 0.05 & log2FoldChange > 1 ~ "Up",
        padj < 0.05 & log2FoldChange < -1 ~ "Down",
        TRUE ~ "Not significant"
      ),
      log10_padj = -log10(ifelse(is.na(padj), 1, padj))
    )

  top_genes <- volcano_data |>
    filter(significance %in% c("Up", "Down")) |>
    arrange(padj) |>
    head(top_n)

  ggplot(volcano_data, aes(x = log2FoldChange, y = log10_padj, color = significance)) +
    geom_point(alpha = 0.6, size = 1.5) +
    geom_hline(yintercept = -log10(0.05), linetype = "dashed", color = "red") +
    geom_vline(xintercept = c(-1, 1), linetype = "dashed", color = "red") +
    geom_text_repel(data = top_genes, aes(label = ifelse(!is.na(symbol) & symbol != "", symbol, gene))) +
    theme_minimal() +
    labs(title = paste("Volcano Plot -", contrast_name))
}
```

## 主要输出
- Salmon `quant.sf`
- gene-level count matrix
- TPM matrix
- DESeq2 full result tables
- significant gene tables
- volcano plots
- normalized counts and TPM heatmaps
""",
        },
        {
            "title": "RNA-seq STAR + featureCounts + DESeq2 + TPM",
            "description": "基于 STAR 基因组比对、featureCounts 基因计数、DESeq2 差异表达和 TPM/标准化计数整理的 RNA-seq 流程。",
            "omics_type": "RNA-Seq",
            "dag_json": {
                "nodes": [
                    {"id": "qc", "label": "FastQC/MultiQC 质控"},
                    {"id": "trim", "label": "Trimmomatic 裁剪"},
                    {"id": "star_index", "label": "STAR 构建基因组索引"},
                    {"id": "star_align", "label": "STAR 比对"},
                    {"id": "alignment_qc", "label": "比对率汇总"},
                    {"id": "featurecounts", "label": "featureCounts 定量"},
                    {"id": "deseq2", "label": "DESeq2 差异分析"},
                    {"id": "plots", "label": "PCA/火山图/热图"},
                ],
                "edges": [
                    {"source": "qc", "target": "trim"},
                    {"source": "trim", "target": "star_align"},
                    {"source": "star_index", "target": "star_align"},
                    {"source": "star_align", "target": "alignment_qc"},
                    {"source": "star_align", "target": "featurecounts"},
                    {"source": "featurecounts", "target": "deseq2"},
                    {"source": "deseq2", "target": "plots"},
                ],
            },
            "content": """# RNA-seq STAR + featureCounts + DESeq2 + TPM

## 适用场景
适用于需要基因组坐标级比对结果、后续可能查看 BAM、比对率、基因计数矩阵和标准 DESeq2 差异表达分析的 bulk RNA-seq 项目。该流程对剪接 reads、基因组定位、featureCounts 计数和样本层级 QC 更友好。

样本包括 `adc1-1`、`adc1-2`、`adc1-3`、`adc2-1`、`adc2-2`、`adc2-3`、`WT-1`、`WT-2`、`WT-3`。

## 1. FastQC 质控与 Trimmomatic 裁剪
```bash
bsub -J fastqc -n 1 -R "span[hosts=1]" -o %J.out -e %J.err -q normal "fastqc *.fq.gz"
bsub -J fastqc_wt -n 1 -R "span[hosts=1]" -o %J.out -e %J.err -q normal "fastqc WT-*"
multiqc .
```

```bash
for sample in WT-1 WT-2 WT-3 adc1-1 adc1-2 adc1-3 adc2-1 adc2-2 adc2-3
do
  java -jar $EBROOTTRIMMOMATIC/trimmomatic-0.32.jar PE -threads 10 -phred33 \
    01_raw_data/${sample}_R1.fq.gz \
    01_raw_data/${sample}_R2.fq.gz \
    02_clean_data/${sample}_R1_paired.fq.gz \
    02_clean_data/${sample}_R1_unpaired.fq.gz \
    02_clean_data/${sample}_R2_paired.fq.gz \
    02_clean_data/${sample}_R2_unpaired.fq.gz \
    HEADCROP:15
done
```

## 2. STAR 构建基因组索引
```bash
bsub -J gunzipgtf -n 1 -R "span[hosts=1]" -o %J.out -e %J.err -q normal "gunzip Arabidopsis_thaliana.TAIR10.57.gtf.gz"
```

```bash
STAR --runThreadN 8 \
  --runMode genomeGenerate \
  --genomeDir ./ref_genomic \
  --genomeFastaFiles ./ref_genomic/Arabidopsis_thaliana.TAIR10.dna.toplevel.fa.gz \
  --sjdbGTFfile ./ref_genomic/Arabidopsis_thaliana.TAIR10.57.gtf.gz \
  --sjdbOverhang 134 \
  --genomeSAindexNbases 12 \
  --genomeChrBinNbits 16 \
  > logs/02_star_index.log 2>&1
```

## 3. STAR 比对与 GeneCounts
```bash
for sample in adc1-1 adc1-2 adc1-3 adc2-1 adc2-2 adc2-3 WT-1 WT-2 WT-3
do
  STAR --runThreadN 12 \
    --genomeDir ref_genomic \
    --readFilesIn 02_clean_data/${sample}_R1_paired.fq.gz 02_clean_data/${sample}_R2_paired.fq.gz \
    --readFilesCommand zcat \
    --outFileNamePrefix 03_aligment_star/${sample}_ \
    --outSAMtype BAM SortedByCoordinate \
    --outFilterMultimapNmax 10 \
    --outFilterMismatchNoverLmax 0.03 \
    --alignIntronMax 5000 \
    --alignMatesGapMax 5000 \
    --quantMode GeneCounts
done

bsub -J star -n 12 -R "span[hosts=1]" -o %J.out -e %J.err -q normal "bash Star_alignment.sh"
```

## 4. 比对结果汇总
```bash
echo "样本,总reads,reads平均长度,唯一比对率,多比对率" > alignment_summary.csv

for sample in adc1-1 adc1-2 adc1-3 adc2-1 adc2-2 adc2-3 WT-1 WT-2 WT-3
do
  total=$(grep "Number of input reads" ${sample}_Log.final.out | awk '{print $6}')
  avg_length=$(grep "Average input read length" ${sample}_Log.final.out | awk '{print $6}')
  unique=$(grep "Uniquely mapped reads %" ${sample}_Log.final.out | awk '{print $6}' | sed 's/%//')
  multi=$(grep "% of reads mapped to multiple loci" ${sample}_Log.final.out | awk '{print $9}' | sed 's/%//')
  echo "${sample},${total},${avg_length},${unique},${multi}" >> alignment_summary.csv
done
```

## 5. featureCounts 基因定量
```bash
GTF_FILE="./ref_genomic/Arabidopsis_thaliana.TAIR10.57.gtf"
THREADS=12

featureCounts -T ${THREADS} \
  -p -B -C \
  -t exon \
  -g gene_id \
  -a ${GTF_FILE} \
  -o 04_featurecounts/featurecounts_gene_counts.txt \
  03_aligment_star/*.bam

bsub -J featureCounts -n 12 -R "span[hosts=1]" -o %J.out -e %J.err -q normal "bash featureCounts.sh"

cut -f1,7- 04_featurecounts/featurecounts_gene_counts.txt > 04_featurecounts/count_matrix.txt
```

## 6. DESeq2 差异表达分析
```r
library(DESeq2)
library(ggplot2)
library(pheatmap)
library(dplyr)
library(RColorBrewer)
library(ggrepel)
library(org.At.tair.db)

count_data <- read.table("count_matrix.txt", header = FALSE, row.names = 1, sep = "\t")
sample_names <- c("adc1-1", "adc1-2", "adc1-3", "adc2-1", "adc2-2", "adc2-3", "WT-1", "WT-2", "WT-3")
colnames(count_data) <- sample_names

sample_info <- data.frame(
  sample = sample_names,
  condition = factor(c(rep("adc1", 3), rep("adc2", 3), rep("WT", 3))),
  replicate = factor(rep(1:3, 3)),
  row.names = sample_names
)

dds <- DESeqDataSetFromMatrix(
  countData = as.matrix(count_data),
  colData = sample_info,
  design = ~ condition
)

keep <- rowSums(counts(dds) >= 10) >= 3
dds <- dds[keep, ]
dds <- DESeq(dds)
normalized_counts <- counts(dds, normalized = TRUE)
```

## 7. 比较组、注释与结果表
```r
contrasts <- list(
  adc1_vs_WT = c("condition", "adc1", "WT"),
  adc2_vs_WT = c("condition", "adc2", "WT"),
  adc2_vs_adc1 = c("condition", "adc2", "adc1")
)

add_gene_annotation <- function(gene_df) {
  gene_ids <- gene_df$gene
  gene_df$symbol <- mapIds(org.At.tair.db, keys = gene_ids, column = "SYMBOL", keytype = "TAIR", multiVals = "first")[gene_ids]
  gene_df$description <- mapIds(org.At.tair.db, keys = gene_ids, column = "GENENAME", keytype = "TAIR", multiVals = "first")[gene_ids]
  gene_df
}

dir.create("deseq2_results/tables", showWarnings = FALSE, recursive = TRUE)
results_list <- list()

for (contrast_name in names(contrasts)) {
  contrast_dir <- file.path("deseq2_results/tables", contrast_name)
  dir.create(contrast_dir, showWarnings = FALSE)

  res <- results(dds, contrast = contrasts[[contrast_name]], alpha = 0.05, lfcThreshold = 1)
  resLFC <- lfcShrink(dds, contrast = contrasts[[contrast_name]], type = "ashr", res = res)

  res_df <- as.data.frame(resLFC)
  res_df$gene <- rownames(res_df)
  res_df <- add_gene_annotation(res_df)

  norm_counts_df <- as.data.frame(normalized_counts)
  norm_counts_df$gene <- rownames(norm_counts_df)
  res_final <- merge(res_df, norm_counts_df, by = "gene", all.x = TRUE)

  sig_genes <- res_final |>
    filter(padj < 0.05 & abs(log2FoldChange) > 1) |>
    arrange(padj, desc(abs(log2FoldChange)))

  write.csv(res_final, file.path(contrast_dir, paste0(contrast_name, "_full_results.csv")), row.names = FALSE, na = "")
  write.csv(sig_genes, file.path(contrast_dir, paste0(contrast_name, "_significant_genes.csv")), row.names = FALSE, na = "")
  results_list[[contrast_name]] <- list(full_results = res_final, significant = sig_genes)
}
```

## 8. PCA、火山图和样本距离热图
```r
dir.create("deseq2_results/plots", showWarnings = FALSE, recursive = TRUE)

vsd <- vst(dds, blind = FALSE)
pcaData <- plotPCA(vsd, intgroup = "condition", returnData = TRUE)
percentVar <- round(100 * attr(pcaData, "percentVar"))

pca_plot <- ggplot(pcaData, aes(PC1, PC2, color = condition, label = name)) +
  geom_point(size = 4) +
  geom_text_repel(size = 3, max.overlaps = 20) +
  scale_color_brewer(palette = "Set1") +
  xlab(paste0("PC1: ", percentVar[1], "% variance")) +
  ylab(paste0("PC2: ", percentVar[2], "% variance")) +
  ggtitle("Principal Component Analysis") +
  theme_minimal()

ggsave("deseq2_results/plots/PCA_plot.png", pca_plot, width = 10, height = 8, dpi = 300)

sampleDists <- dist(t(assay(vsd)))
pheatmap(
  as.matrix(sampleDists),
  clustering_distance_rows = sampleDists,
  clustering_distance_cols = sampleDists,
  annotation_col = data.frame(Condition = sample_info$condition, row.names = rownames(sample_info)),
  main = "Sample Distance Matrix"
)
```

## 可选：GO 富集分析
```r
library(clusterProfiler)
library(org.At.tair.db)

sig_genes <- results_list$adc1_vs_WT$significant$gene

ego <- enrichGO(
  gene = sig_genes,
  OrgDb = org.At.tair.db,
  keyType = "TAIR",
  ont = "BP",
  pAdjustMethod = "BH",
  pvalueCutoff = 0.05
)
```

## 主要输出
- STAR sorted BAM
- STAR `Log.final.out` 比对率汇总
- featureCounts gene count matrix
- DESeq2 full result tables
- significant gene tables
- normalized counts
- PCA plot
- volcano plots
- sample distance heatmap
""",
        },
        {
            "title": "10x 单细胞基础降维聚类",
            "description": "面向 10x Genomics scRNA-seq 数据的综合分析流程，覆盖分析类型选择、Cell Ranger 预处理、Seurat v5/Scanpy 质控、整合、聚类、注释和下游解释。",
            "omics_type": "scRNA-Seq",
            "dag_json": {
                "nodes": [
                    {"id": "design", "label": "实验设计与类型判断"},
                    {"id": "cellranger", "label": "Cell Ranger 定量"},
                    {"id": "qc", "label": "细胞/基因质控"},
                    {"id": "doublet", "label": "双细胞与环境 RNA 评估"},
                    {"id": "normalize", "label": "SCTransform/NormalizeData"},
                    {"id": "integrate", "label": "多样本整合"},
                    {"id": "cluster", "label": "PCA/邻接图/UMAP/聚类"},
                    {"id": "annotation", "label": "Marker 与细胞类型注释"},
                    {"id": "downstream", "label": "差异/通路/拟时序/通讯"},
                ],
                "edges": [
                    {"source": "design", "target": "cellranger"},
                    {"source": "cellranger", "target": "qc"},
                    {"source": "qc", "target": "doublet"},
                    {"source": "doublet", "target": "normalize"},
                    {"source": "normalize", "target": "integrate"},
                    {"source": "integrate", "target": "cluster"},
                    {"source": "cluster", "target": "annotation"},
                    {"source": "annotation", "target": "downstream"},
                ],
            },
            "content": """# 10x 单细胞 RNA-seq 综合分析流程

## 一、单细胞分析的主要类型

单细胞分析不是单一流程，而是一组围绕细胞异质性的问题框架。建项目前先判断研究问题属于哪一类，这会直接影响质控阈值、整合策略和下游统计方法。

| 类型 | 典型问题 | 推荐方法 | 关键输出 |
| --- | --- | --- | --- |
| 基础细胞图谱 | 样本里有哪些细胞群？比例如何？ | Seurat v5 或 Scanpy 标准聚类流程 | UMAP、cluster、marker genes、细胞类型注释 |
| 多样本/多批次整合 | 不同样本、批次、处理组能否放在同一空间比较？ | Seurat `IntegrateLayers`、Harmony、RPCA、scVI | integrated embedding、整合后聚类 |
| 组间差异表达 | 某类细胞在处理组与对照组中哪些基因改变？ | pseudobulk 优先，其次 cell-level DE | cell type-specific DEG |
| 细胞比例变化 | 疾病或处理是否改变某类细胞占比？ | proportion test、Dirichlet-multinomial、Milo | 细胞组成差异 |
| 发育轨迹/拟时序 | 细胞是否存在连续分化路径？ | Monocle3、Slingshot、Palantir | trajectory、pseudotime、branch markers |
| 细胞通讯 | 细胞群之间可能通过哪些配体受体互作？ | CellChat、NicheNet、LIANA | ligand-receptor network |
| 自动注释/参考映射 | 新数据如何映射到已有 atlas？ | Azimuth、SingleR、CellTypist、scArches | predicted cell type labels |
| 多组学/空间扩展 | RNA + ATAC、CITE-seq 或空间转录组如何联合解释？ | Seurat WNN、Signac、Scanpy/Squidpy | multi-modal embedding、空间特征 |

## 二、最佳实践选择

### 推荐主流程

对 10x Genomics 3' 或 5' scRNA-seq 项目，MVP 阶段建议采用：

1. `Cell Ranger count` 生成表达矩阵和官方 QC 报告。
2. `Seurat v5 + SCTransform` 作为主分析流程。
3. 多样本项目使用 Seurat v5 `IntegrateLayers`，优先试 `RPCAIntegration` 或 `HarmonyIntegration`。
4. 大规模数据、跨平台 atlas 或 Python 团队可并行使用 `Scanpy + scVI`。
5. 差异表达建议按样本聚合做 pseudobulk，避免把细胞当作完全独立重复。

### 为什么这样选

- Seurat v5 文档覆盖质控、归一化、聚类、整合和参考映射，适合快速建立可复用分析模板。
- SCTransform 对测序深度差异更稳，适合多样本项目的归一化和高变基因建模。
- RPCA/Harmony 通常比强行 CCA 更保守，较不容易抹掉真实生物差异。
- Scanpy 适合 Python 工作流和大规模 AnnData 生态，后续可以接 scVI、CellTypist、Squidpy 等工具。

## 三、整体流程图

```mermaid
flowchart TD
    A[实验设计与样本信息] --> B[Cell Ranger count]
    B --> C[读取 filtered_feature_bc_matrix]
    C --> D[细胞与基因质控]
    D --> E[双细胞 doublet 评估]
    E --> F[环境 RNA / 低质量细胞检查]
    F --> G[SCTransform 或 NormalizeData]
    G --> H[高变基因 / PCA]
    H --> I{是否多样本或多批次?}
    I -- 是 --> J[IntegrateLayers / Harmony / scVI]
    I -- 否 --> K[FindNeighbors]
    J --> K
    K --> L[FindClusters]
    L --> M[UMAP / t-SNE 可视化]
    M --> N[Marker gene 鉴定]
    N --> O[细胞类型注释]
    O --> P[差异表达 / 富集 / 拟时序 / 通讯]
```

## 四、输入文件与目录建议

```text
single_cell_project/
├── 00_metadata/
│   └── sample_info.csv
├── 01_fastq/
│   ├── sampleA/
│   └── sampleB/
├── 02_cellranger/
│   ├── sampleA/outs/
│   └── sampleB/outs/
├── 03_seurat/
│   ├── rds/
│   ├── tables/
│   └── plots/
├── 04_annotation/
├── 05_downstream/
└── reports/
```

`sample_info.csv` 至少包含：

| 字段 | 说明 |
| --- | --- |
| `sample_id` | 样本 ID，必须与 Cell Ranger 输出目录一致 |
| `condition` | 实验分组，如 control、treatment |
| `batch` | 建库批次或测序批次 |
| `tissue` | 组织来源 |
| `fastq_dir` | FASTQ 所在目录 |

## 五、Cell Ranger 预处理

Cell Ranger 负责把 FASTQ 转换为基因表达矩阵。它的输出是后续 Seurat/Scanpy 分析的入口。

```bash
cellranger count \
  --id=sampleA \
  --transcriptome=/ref/refdata-gex-GRCh38-2024-A \
  --fastqs=/data/fastq/sampleA \
  --sample=sampleA \
  --localcores=24 \
  --localmem=128
```

多样本可写成循环：

```bash
REF=/ref/refdata-gex-GRCh38-2024-A
FASTQ_ROOT=/data/fastq
OUT_ROOT=02_cellranger

for sample in sampleA sampleB sampleC
do
  cellranger count \
    --id=${sample} \
    --transcriptome=${REF} \
    --fastqs=${FASTQ_ROOT}/${sample} \
    --sample=${sample} \
    --localcores=24 \
    --localmem=128

  mv ${sample} ${OUT_ROOT}/
done
```

重点检查 `outs/web_summary.html`：

| 指标 | 解释 | 风险信号 |
| --- | --- | --- |
| Estimated Number of Cells | 估计捕获细胞数 | 明显低于上样预期 |
| Mean Reads per Cell | 单细胞平均 reads 数 | 过低会影响基因检出 |
| Median Genes per Cell | 每个细胞检测基因数中位数 | 过低提示低质量或细胞破裂 |
| Fraction Reads in Cells | reads 落入有效细胞 barcode 的比例 | 过低提示背景 RNA 或空液滴多 |
| Sequencing Saturation | 测序饱和度 | 过低可考虑补测 |

## 六、Seurat v5 主分析流程

### 1. 读取数据并创建对象

```r
library(Seurat)
library(dplyr)
library(ggplot2)
library(patchwork)

sample_info <- read.csv("00_metadata/sample_info.csv")

seurat_list <- lapply(seq_len(nrow(sample_info)), function(i) {
  sample_id <- sample_info$sample_id[i]
  matrix_dir <- file.path("02_cellranger", sample_id, "outs", "filtered_feature_bc_matrix")

  counts <- Read10X(data.dir = matrix_dir)
  obj <- CreateSeuratObject(
    counts = counts,
    project = sample_id,
    min.cells = 3,
    min.features = 200
  )

  obj$sample_id <- sample_id
  obj$condition <- sample_info$condition[i]
  obj$batch <- sample_info$batch[i]
  obj$tissue <- sample_info$tissue[i]
  obj[["percent.mt"]] <- PercentageFeatureSet(obj, pattern = "^MT-")
  obj[["percent.ribo"]] <- PercentageFeatureSet(obj, pattern = "^RP[SL]")
  obj
})

names(seurat_list) <- sample_info$sample_id
```

### 2. 质控阈值设置

常用 QC 指标：

| 指标 | 含义 | 常见处理 |
| --- | --- | --- |
| `nFeature_RNA` | 每个细胞检测到的基因数 | 过低为空液滴或低质量，过高可能是 doublet |
| `nCount_RNA` | 每个细胞 UMI 总数 | 极高可能是 doublet，极低可能低质量 |
| `percent.mt` | 线粒体基因比例 | 高比例通常提示细胞应激或破裂 |
| `percent.ribo` | 核糖体基因比例 | 可辅助判断细胞状态 |

阈值不要机械套用，应先画图再定：

```r
qc_plot <- VlnPlot(
  seurat_list[[1]],
  features = c("nFeature_RNA", "nCount_RNA", "percent.mt"),
  ncol = 3,
  pt.size = 0.1
)
ggsave("03_seurat/plots/qc_violin_sampleA.pdf", qc_plot, width = 12, height = 4)
```

初始经验阈值：

```r
filter_one <- function(obj) {
  subset(
    obj,
    subset =
      nFeature_RNA > 300 &
      nFeature_RNA < 6000 &
      nCount_RNA > 500 &
      percent.mt < 15
  )
}

seurat_list <- lapply(seurat_list, filter_one)
```

经验解释：

- PBMC 等免疫细胞常用 `percent.mt < 10-15`。
- 肿瘤、组织样本或冷冻样本线粒体比例可能更高，需要结合分布决定。
- 神经元、肌肉、肝脏等组织的基因数范围可能显著不同，不能直接照搬 PBMC 阈值。

### 3. 双细胞和环境 RNA

双细胞 doublet 会导致两个细胞类型的 marker 同时出现，影响聚类和注释。建议至少做一次 doublet 评估。

可选工具：

| 工具 | 生态 | 说明 |
| --- | --- | --- |
| DoubletFinder | R/Seurat | Seurat 用户常用 |
| scDblFinder | Bioconductor | 自动化程度高 |
| Scrublet | Python | Scanpy 工作流常用 |

示意代码：

```r
# DoubletFinder 参数需要根据数据量和预期 doublet rate 调整。
# MVP 阶段建议先标记 doublet，再比较去除前后的 UMAP 和 marker 表。
```

环境 RNA 可用 SoupX、DecontX 等工具评估。若样本有明显红细胞、上皮裂解或坏死背景，建议在正式分析前处理。

### 4. SCTransform 归一化

```r
seurat_list <- lapply(seurat_list, function(obj) {
  SCTransform(
    obj,
    vars.to.regress = "percent.mt",
    verbose = FALSE
  )
})
```

如果是单样本初步探索，也可以使用经典 LogNormalize：

```r
obj <- NormalizeData(obj)
obj <- FindVariableFeatures(obj, selection.method = "vst", nfeatures = 2000)
obj <- ScaleData(obj, vars.to.regress = c("percent.mt"))
```

### 5. 多样本整合

Seurat v5 推荐使用 layer-based integration。示例：

```r
combined <- merge(
  seurat_list[[1]],
  y = seurat_list[-1],
  add.cell.ids = names(seurat_list)
)

combined[["RNA"]] <- split(combined[["RNA"]], f = combined$sample_id)
combined <- NormalizeData(combined)
combined <- FindVariableFeatures(combined)
combined <- ScaleData(combined)
combined <- RunPCA(combined)

combined <- IntegrateLayers(
  object = combined,
  method = RPCAIntegration,
  orig.reduction = "pca",
  new.reduction = "integrated.rpca",
  verbose = FALSE
)
```

方法选择建议：

| 方法 | 适用场景 | 风险 |
| --- | --- | --- |
| RPCAIntegration | 同平台、多样本、差异较温和 | 可能保留部分批次效应 |
| HarmonyIntegration | 批次变量明确、速度快 | 参数不当可能过校正 |
| CCAIntegration | 细胞类型共享度较高 | 数据差异大时可能过度混合 |
| scVIIntegration | 大规模、复杂批次、Python 环境成熟 | 依赖环境更重 |

### 6. 降维、邻接图和聚类

```r
combined <- FindNeighbors(combined, reduction = "integrated.rpca", dims = 1:30)
combined <- FindClusters(combined, resolution = 0.4)
combined <- FindClusters(combined, resolution = 0.8)
combined <- RunUMAP(combined, reduction = "integrated.rpca", dims = 1:30)

p1 <- DimPlot(combined, group.by = "sample_id")
p2 <- DimPlot(combined, group.by = "seurat_clusters", label = TRUE)
ggsave("03_seurat/plots/umap_sample_cluster.pdf", p1 + p2, width = 12, height = 5)
```

分辨率选择建议：

- `0.2-0.4`：粗粒度细胞类型。
- `0.6-1.0`：常规探索。
- `>1.2`：寻找细胞亚群，但要警惕过度切分。

### 7. Marker gene 鉴定

```r
combined <- PrepSCTFindMarkers(combined)

markers <- FindAllMarkers(
  combined,
  only.pos = TRUE,
  min.pct = 0.25,
  logfc.threshold = 0.25
)

write.csv(markers, "03_seurat/tables/all_cluster_markers.csv", row.names = FALSE)
```

常见免疫细胞 marker 示例：

| 细胞类型 | 常用 marker |
| --- | --- |
| T cells | `CD3D`, `CD3E`, `TRAC` |
| CD4 T | `IL7R`, `CCR7`, `LTB` |
| CD8 T | `CD8A`, `CD8B`, `GZMK` |
| NK cells | `NKG7`, `GNLY`, `KLRD1` |
| B cells | `MS4A1`, `CD79A`, `CD74` |
| Plasma cells | `MZB1`, `JCHAIN`, `IGHG1` |
| Monocytes | `LYZ`, `S100A8`, `S100A9` |
| Dendritic cells | `FCER1A`, `CST3`, `CLEC10A` |
| Platelets | `PPBP`, `PF4` |

### 8. 细胞类型注释

推荐组合：

1. 手动 marker 注释：最可靠，但需要领域知识。
2. 参考数据库自动注释：SingleR、CellTypist、Azimuth。
3. 回看样本来源和文献 marker：避免把技术 cluster 误判为新细胞类型。

手动注释示例：

```r
new_ids <- c(
  "0" = "CD4 T cells",
  "1" = "CD14 Monocytes",
  "2" = "B cells",
  "3" = "CD8 T cells",
  "4" = "NK cells"
)

combined$celltype <- plyr::mapvalues(
  x = combined$seurat_clusters,
  from = names(new_ids),
  to = as.vector(new_ids)
)

DimPlot(combined, group.by = "celltype", label = TRUE)
ggsave("03_seurat/plots/umap_celltype.pdf", width = 8, height = 6)
```

### 9. 组间差异表达：优先 pseudobulk

单细胞中每个细胞不是完全独立生物学重复。如果有多个样本，建议按 `sample_id + celltype` 聚合，再用 DESeq2/edgeR 做差异分析。

```r
counts_by_celltype <- AggregateExpression(
  combined,
  group.by = c("celltype", "sample_id"),
  assays = "RNA",
  slot = "counts",
  return.seurat = FALSE
)
```

后续思路：

1. 对每个 cell type 提取 sample-level count matrix。
2. 构建 `condition` 设计矩阵。
3. 用 DESeq2 做 `~ condition`。
4. 分别输出每类细胞的 DEG 和富集结果。

### 10. 下游分析选择

| 下游方向 | 推荐工具 | 适合问题 |
| --- | --- | --- |
| 通路富集 | clusterProfiler、fgsea、GSEApy | DEG 指向哪些通路 |
| 拟时序 | Monocle3、Slingshot、Palantir | 发育、分化、状态转换 |
| RNA velocity | scVelo、velocyto | 细胞状态变化方向 |
| 细胞通讯 | CellChat、NicheNet、LIANA | 哪些细胞群可能相互作用 |
| CNV 推断 | inferCNV、copyKAT | 肿瘤单细胞恶性细胞识别 |
| TCR/BCR | scRepertoire、immunarch | 克隆扩增和免疫受体谱 |

## 七、Scanpy 备用流程

Python 团队或大规模数据可使用 Scanpy：

```python
import scanpy as sc

adata = sc.read_10x_mtx(
    "02_cellranger/sampleA/outs/filtered_feature_bc_matrix",
    var_names="gene_symbols",
    cache=True,
)

adata.var["mt"] = adata.var_names.str.startswith("MT-")
sc.pp.calculate_qc_metrics(adata, qc_vars=["mt"], inplace=True)

adata = adata[
    (adata.obs["n_genes_by_counts"] > 300)
    & (adata.obs["n_genes_by_counts"] < 6000)
    & (adata.obs["pct_counts_mt"] < 15),
    :
]

sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=2000)
adata = adata[:, adata.var.highly_variable]
sc.pp.scale(adata, max_value=10)
sc.tl.pca(adata)
sc.pp.neighbors(adata, n_pcs=30)
sc.tl.leiden(adata, resolution=0.8)
sc.tl.umap(adata)
sc.tl.rank_genes_groups(adata, "leiden", method="wilcoxon")

adata.write("03_scanpy/sampleA_processed.h5ad")
```

## 八、关键质控图

建议每个项目至少输出：

- Cell Ranger `web_summary.html`
- 每个样本的 `nFeature_RNA` / `nCount_RNA` / `percent.mt` 小提琴图
- QC 前后细胞数统计表
- UMAP 按 `sample_id` 着色
- UMAP 按 `condition` 着色
- UMAP 按 `cluster` 和 `celltype` 着色
- 每个 cluster 的 top marker 热图
- 注释后的细胞比例堆叠图

细胞比例图示例：

```r
prop_df <- combined@meta.data |>
  dplyr::count(sample_id, condition, celltype) |>
  dplyr::group_by(sample_id) |>
  dplyr::mutate(prop = n / sum(n))

ggplot(prop_df, aes(x = sample_id, y = prop, fill = celltype)) +
  geom_col(width = 0.8) +
  facet_grid(. ~ condition, scales = "free_x", space = "free_x") +
  theme_bw() +
  labs(x = "Sample", y = "Cell proportion")
```

## 九、常见问题与排查

| 问题 | 可能原因 | 处理建议 |
| --- | --- | --- |
| 细胞数远低于预期 | 细胞活性差、上样不足、组织解离失败 | 查看 Cell Ranger summary，回看实验记录 |
| 线粒体比例整体偏高 | 细胞破裂、组织应激、冷冻样本 | 分样本设阈值，不要一刀切 |
| UMAP 按样本分开 | 批次效应或真实组间差异 | 先判断 marker，再尝试 RPCA/Harmony |
| 聚类过碎 | resolution 太高，PC 太多 | 降低 resolution，检查 clustree |
| marker 不清晰 | 低质量细胞、doublet、注释层级不合适 | 去 doublet，重新聚类或合并相近 cluster |
| 差异基因过多 | 把细胞当重复、批次未控制 | 使用 pseudobulk，设计矩阵加入批次 |

## 十、主要输出

- `filtered_feature_bc_matrix`
- Seurat `.rds` 或 Scanpy `.h5ad`
- QC summary table
- UMAP/t-SNE 图
- cluster marker gene 表
- 细胞类型注释表
- 每个样本/组别的细胞比例表
- cell type-specific DEG
- 富集分析结果
- 可选：拟时序、通讯、RNA velocity、CNV 推断结果

## 十一、参考资料

- Seurat v5 官方 Getting Started：标准无监督聚类流程包含 QC、过滤、高变基因、降维、图聚类和 marker 鉴定。
- Seurat v5 Integration 官方文档：`IntegrateLayers` 支持 CCA、RPCA、Harmony、FastMNN、scVI 等整合方法。
- Scanpy 官方 preprocessing and clustering tutorial：提供 Python 生态的过滤、归一化、HVG、PCA、neighbors、Leiden、UMAP 和 marker 流程。
- 10x Genomics Cell Ranger 文档：用于从 FASTQ 生成表达矩阵和 `web_summary.html` 质控报告。
""",
        },
        {
            "title": "WGS 变异检测流程",
            "description": "从全基因组测序 reads 到 SNV/Indel 变异集合的标准检测流程。",
            "omics_type": "WGS",
            "dag_json": {
                "nodes": [
                    {"id": "qc", "label": "reads 质控"},
                    {"id": "bwa", "label": "BWA-MEM 比对"},
                    {"id": "markdup", "label": "重复标记"},
                    {"id": "bqsr", "label": "BQSR 校正"},
                    {"id": "haplotype", "label": "GATK HaplotypeCaller"},
                ],
                "edges": [
                    {"source": "qc", "target": "bwa"},
                    {"source": "bwa", "target": "markdup"},
                    {"source": "markdup", "target": "bqsr"},
                    {"source": "bqsr", "target": "haplotype"},
                ],
            },
            "content": """# WGS 变异检测流程

## 适用场景
适用于人类或模式物种全基因组测序数据，用于检测 SNV 与小 Indel。

## 核心步骤
1. 对原始 FASTQ 进行质量评估。
2. 使用 BWA-MEM 将 reads 比对到参考基因组。
3. 使用 Picard 或 GATK MarkDuplicates 标记 PCR duplicates。
4. 使用 GATK 进行碱基质量分数重校正。
5. 使用 HaplotypeCaller 生成样本级 GVCF，并进行联合分型。

## 主要输出
- 排序后的 BAM 文件
- 变异检测 VCF
- 变异质控统计
- 可进入注释环节的候选变异集合
""",
        },
        {
            "title": "CUT&Tag T2T 基因组差异结合分析",
            "description": "面向 CUT&Tag 数据的 T2T 基因组比对、CPM 标准化、SEACR 搜峰、DiffBind 差异 Peak 与 GO 富集分析流程。",
            "omics_type": "CUT&Tag",
            "dag_json": {
                "nodes": [
                    {"id": "qc", "label": "Trim Galore/FastQC 质控"},
                    {"id": "index", "label": "Bowtie2 构建 T2T 索引"},
                    {"id": "mapping", "label": "T2T 基因组严格双端比对"},
                    {"id": "spikein", "label": "Spike-in 诊断"},
                    {"id": "coverage", "label": "CPM BedGraph 生成"},
                    {"id": "seacr", "label": "SEACR 精确搜峰"},
                    {"id": "diffbind", "label": "DiffBind 差异 Peak"},
                    {"id": "annotation", "label": "ChIPseeker/GO 注释"},
                ],
                "edges": [
                    {"source": "qc", "target": "index"},
                    {"source": "index", "target": "mapping"},
                    {"source": "mapping", "target": "spikein"},
                    {"source": "mapping", "target": "coverage"},
                    {"source": "coverage", "target": "seacr"},
                    {"source": "seacr", "target": "diffbind"},
                    {"source": "diffbind", "target": "annotation"},
                ],
            },
            "content": """# CUT&Tag T2T 基因组差异结合分析

## 适用场景
适用于 CUT&Tag 或 CUT&RUN 染色质结合数据，尤其是使用 T2T 级别参考基因组、需要比较处理组与对照组蛋白结合重分布的项目。

本流程来自 Zeocin vs Control 的 TOP1 CUT&Tag 分析场景：使用拟南芥 Col-PEK T2T 基因组进行 Bowtie2 比对，结合 Spike-in 诊断、CPM 标准化、SEACR 搜峰、DiffBind 差异结合分析、ChIPseeker 注释和 GO 富集，解释 DNA 损伤诱导的 TOP1 全基因组重分布。

## 样本设计
| SampleID | Condition | Replicate | BAM | Peak |
| --- | --- | --- | --- | --- |
| C1 | Control | 1 | `C1_T2T.sorted.bam` | `C1_seacr.stringent.bed` |
| C2 | Control | 2 | `C2_T2T.sorted.bam` | `C2_seacr.stringent.bed` |
| C3 | Control | 3 | `C3_T2T.sorted.bam` | `C3_seacr.stringent.bed` |
| Z1 | Zeocin | 1 | `Z1_T2T.sorted.bam` | `Z1_seacr.stringent.bed` |
| Z2 | Zeocin | 2 | `Z2_T2T.sorted.bam` | `Z2_seacr.stringent.bed` |
| Z3 | Zeocin | 3 | `Z3_T2T.sorted.bam` | `Z3_seacr.stringent.bed` |

## 1. 原始 reads 质控与接头过滤
```bash
WORKDIR="<YOUR_PROJECT_DIR>"
RAW_DIR="${WORKDIR}/01_raw_data"
OUT_DIR="${WORKDIR}/03_trimmed_data"

for sample in C1 C2 C3 Z1 Z2 Z3
do
  trim_galore \
    --paired \
    --quality 20 \
    --phred33 \
    --fastqc \
    --cores 4 \
    --gzip \
    -o ${OUT_DIR} \
    ${RAW_DIR}/${sample}_R1.fq.gz \
    ${RAW_DIR}/${sample}_R2.fq.gz
done
```

## 2. 构建 T2T 基因组 Bowtie2 索引
```bash
WORKDIR="<YOUR_PROJECT_DIR>"
REF_DIR="${WORKDIR}/ref_genenic"

bowtie2-build \
  --threads 4 \
  ${REF_DIR}/Arabidopsis_thaliana_Col-PEK.genomic.fa \
  ${REF_DIR}/Col_PEK_T2T
```

## 3. 比对到 T2T 基因组并过滤多重比对
```bash
WORKDIR="<YOUR_PROJECT_DIR>"
TRIM_DIR="${WORKDIR}/03_trimmed_data"
ALN_DIR="${WORKDIR}/04_alignment"
REF_INDEX="${WORKDIR}/ref_genenic/Col_PEK_T2T"

for sample in C1 C2 C3 Z1 Z2 Z3
do
  bowtie2 \
    --end-to-end \
    --very-sensitive \
    --no-mixed \
    --no-discordant \
    --phred33 \
    -I 10 \
    -X 700 \
    -p 8 \
    -x ${REF_INDEX} \
    -1 ${TRIM_DIR}/${sample}_R1_val_1.fq.gz \
    -2 ${TRIM_DIR}/${sample}_R2_val_2.fq.gz \
    -S ${ALN_DIR}/${sample}_T2T.sam

  samtools view -bS -q 20 -@ 8 ${ALN_DIR}/${sample}_T2T.sam | \
    samtools sort -@ 8 -o ${ALN_DIR}/${sample}_T2T.sorted.bam

  samtools index ${ALN_DIR}/${sample}_T2T.sorted.bam
  rm ${ALN_DIR}/${sample}_T2T.sam
done
```

## 4. Spike-in 诊断与归一化策略
| Group | Samples | Spike-in rate |
| --- | --- | --- |
| Control | C1, C2, C3 | ~6.63% |
| Zeocin | Z1, Z2, Z3 | ~1.45% |

Zeocin 处理组 Spike-in 比对率相较对照组出现约 4.5 倍下降，同时拟南芥基因组比对 reads 明显上升。这说明处理组中真实靶序列发生大规模扩增，外源 Spike-in 被物理稀释。

**关键判断：** 对于这种全局剧烈变化的 CUT&Tag 实验，不应直接使用外源 Spike-in scale factor 强行放大处理组信号，否则容易造成全基因组背景假阳性。这里采用 CPM 或 DESeq2 内部相对定量，重点寻找特异性重分布靶点。

## 5. 生成 CPM 标准化 BedGraph
```bash
WORKDIR="<YOUR_PROJECT_DIR>"
ALN_DIR="${WORKDIR}/04_alignment"
PEAK_DIR="${WORKDIR}/05_peaks"
mkdir -p ${PEAK_DIR}

for sample in C1 C2 C3 Z1 Z2 Z3
do
  bamCoverage \
    -b ${ALN_DIR}/${sample}_T2T.sorted.bam \
    -o ${PEAK_DIR}/${sample}.bedgraph \
    --outFileFormat bedgraph \
    --normalizeUsing CPM \
    --binSize 10 \
    -p 8
done
```

## 6. SEACR 无 IgG 模式搜峰
SEACR 适合 CUT&Tag 的窄峰/稀疏信号场景。对于无 IgG 对照的实验，可以使用 stringent 模式获得更干净的候选峰。

```bash
wget https://github.com/FredHutch/SEACR/raw/master/SEACR_1.3.sh
wget https://github.com/FredHutch/SEACR/raw/master/SEACR_1.3.R

bash SEACR_1.3.sh C1.bedgraph 0.01 non stringent C1_seacr
```

## 7. DiffBind 差异 Peak 定量
```r
library(DiffBind)

cut_tag <- dba(sampleSheet = "sample_sheet.csv")
cut_tag <- dba.count(cut_tag, bUseSummarizeOverlaps = TRUE)
cut_tag <- dba.contrast(cut_tag, categories = DBA_CONDITION, minMembers = 2)
cut_tag <- dba.analyze(cut_tag)

res_deseq <- dba.report(cut_tag, method = DBA_DESEQ2, contrast = 1, th = 0.05)
write.csv(as.data.frame(res_deseq), file = "Zeocin_vs_Control_DiffPeaks.csv")

dba.plotPCA(cut_tag, DBA_CONDITION, label = DBA_ID)
dba.plotVolcano(cut_tag)
```

## 8. T2T 注释、TAIR 名称转换与 GO 富集
```r
library(ChIPseeker)
library(GenomicFeatures)
library(GenomicRanges)
library(txdbmaker)

txdb <- makeTxDbFromGFF("Arabidopsis_thaliana_Col-PEK.genomic.gff", format = "gff3")
diff_peaks <- read.csv("Zeocin_vs_Control_DiffPeaks.csv")

peak_gr <- GRanges(
  seqnames = diff_peaks$seqnames,
  ranges = IRanges(start = diff_peaks$start, end = diff_peaks$end),
  strand = diff_peaks$strand
)
mcols(peak_gr) <- diff_peaks[, c("Fold", "FDR")]

peak_anno <- annotatePeak(peak_gr, tssRegion = c(-3000, 3000), TxDb = txdb)
write.csv(as.data.frame(peak_anno), "Zeocin_vs_Control_Annotated_DiffPeaks.csv", row.names = FALSE)
```

```r
library(clusterProfiler)
library(org.At.tair.db)

diff_genes <- read.csv("Zeocin_vs_Control_TAIR_Ready.csv")
diff_genes <- diff_genes[grep("^AT[1-5]G\\d{5}$", diff_genes$tairId), ]

genes_up <- unique(diff_genes$tairId[diff_genes$Fold > 0])
genes_down <- unique(diff_genes$tairId[diff_genes$Fold < 0])

go_up <- enrichGO(gene = genes_up, OrgDb = org.At.tair.db, keyType = "TAIR", ont = "BP")
go_down <- enrichGO(gene = genes_down, OrgDb = org.At.tair.db, keyType = "TAIR", ont = "ALL")
```

## 生物学解释
正常状态下，TOP1 更集中地占据启动子或活跃转录区，形成清晰的局部高峰；Zeocin 诱导 DNA 损伤后，TOP1 发生全基因组重分布，更多 reads 映射到拟南芥基因组，但局部孤立峰可能减少，呈现“高原化”的广泛结合模式。

## 主要输出
- Trim Galore/FastQC 质控报告
- T2T 基因组比对 BAM 与索引
- Spike-in 诊断统计
- CPM 标准化 BedGraph
- SEACR peak BED 文件
- DiffBind 差异 Peak 表
- ChIPseeker 注释结果
- TAIR ID 转换表与 GO 富集图
""",
        },
        {
            "title": "BSA-seq 突变位点定位分析",
            "description": "面向 Bulked Segregant Analysis 的变异检测和候选区间定位流程，覆盖数据下载、质控、比对、GATK SNP calling、过滤、SNP-index 与 ED5 下游分析。",
            "omics_type": "BSA-seq",
            "dag_json": {
                "nodes": [
                    {"id": "download", "label": "测序数据下载"},
                    {"id": "qc", "label": "FastQC/Trimmomatic 质控"},
                    {"id": "align", "label": "BWA-MEM 比对 TAIR10"},
                    {"id": "markdup", "label": "GATK MarkDuplicates"},
                    {"id": "haplotype", "label": "HaplotypeCaller GVCF"},
                    {"id": "combine", "label": "CombineGVCFs/GenotypeGVCFs"},
                    {"id": "filter", "label": "SNP/INDEL 硬过滤"},
                    {"id": "qtlseq", "label": "SNP-index/ED5 下游定位"},
                ],
                "edges": [
                    {"source": "download", "target": "qc"},
                    {"source": "qc", "target": "align"},
                    {"source": "align", "target": "markdup"},
                    {"source": "markdup", "target": "haplotype"},
                    {"source": "haplotype", "target": "combine"},
                    {"source": "combine", "target": "filter"},
                    {"source": "filter", "target": "qtlseq"},
                ],
            },
            "content": """# BSA-seq 突变位点定位分析

## 适用场景
适用于 Bulked Segregant Analysis（BSA）或 QTL-seq 类型项目：将极端表型个体混池测序，与亲本或对照样本比较等位基因频率差异，从而定位候选突变区间。

本流程来自拟南芥 BSA 分析记录，参考基因组使用 `TAIR10_chr_all.fas`，核心样本包括 `1-37`、`27-3-1`、`27N`、`Neg`、`top1α-10`。流程前半段使用 BWA/GATK 产出高质量 VCF，后半段在 R 中计算 SNP-index、ΔSNP-index 和 ED5，并绘制候选区间图。

## 样本与分组
| Sample | Role | Notes |
| --- | --- | --- |
| `1-37` | bulk / segregant | 用于 37 组合分析 |
| `27-3-1` | bulk / segregant | 用于 27 组合分析 |
| `27N` | normal/control | 27 组合对照 |
| `Neg` | wild type/control | 37 组合对照 |
| `top1α-10` | parent/reference mutant | 亲本或参考突变材料 |

## 1. 下载原始数据
```bash
./lnd login -u <YOUR_USERNAME> -p <YOUR_PASSWORD>

./lnd cp -d \
  <YOUR_OSS_RAW_DATA_URI> \
  ../../../01_raw_data/
```

## 2. FastQC 质控与 Trimmomatic 裁剪
```bash
module load FastQC/0.11.9

bsub -J fastqc1-37 -n 1 -R "span[hosts=1]" -o %J.out -e %J.err -q normal "fastqc 1-37_*"
bsub -J fastqc27-3 -n 1 -R "span[hosts=1]" -o %J.out -e %J.err -q normal "fastqc 27-3*"
bsub -J fastqc27N -n 1 -R "span[hosts=1]" -o %J.out -e %J.err -q normal "fastqc 27N*"
bsub -J fastqcNeg -n 1 -R "span[hosts=1]" -o %J.out -e %J.err -q normal "fastqc Neg*"
bsub -J fastqctop1 -n 1 -R "span[hosts=1]" -o %J.out -e %J.err -q normal "fastqc top1α*"
```

```bash
for sample in 1-37 27-3-1 27N Neg top1α-10
do
  trimmomatic.sh PE -threads 10 -phred33 \
    01_raw_data/${sample}_1.fq.gz \
    01_raw_data/${sample}_2.fq.gz \
    02_clean_data/${sample}_R1_paired.fq.gz \
    02_clean_data/${sample}_R1_unpaired.fq.gz \
    02_clean_data/${sample}_R2_paired.fq.gz \
    02_clean_data/${sample}_R2_unpaired.fq.gz \
    HEADCROP:2
done
```

## 3. BWA-MEM 比对到 TAIR10
```bash
REF="./ref_genomic/TAIR10_chr_all.fas"

for sample in 1-37 27-3-1 27N Neg top1α-10
do
  bwa mem -M -t 8 \
    -R "@RG\tID:${sample}\tSM:${sample}" \
    ${REF} \
    02_clean_data/${sample}_R1_paired.fq.gz \
    02_clean_data/${sample}_R2_paired.fq.gz | \
    samtools sort -@ 8 -o 03_alignment/${sample}.sorted.bam -

  samtools flagstat 03_alignment/${sample}.sorted.bam > 03_alignment/${sample}_flagstat.log
  samtools index 03_alignment/${sample}.sorted.bam
done
```

## 4. GATK MarkDuplicates 去重
```bash
for sample in 1-37 27-3-1 27N Neg top1α-10
do
  gatk MarkDuplicates \
    -I 03_alignment/${sample}.sorted.bam \
    -M 03_alignment/${sample}.markup_metrics.txt \
    -O 03_alignment/${sample}.sorted.markup.bam

  samtools index 03_alignment/${sample}.sorted.markup.bam
done
```

## 5. HaplotypeCaller 生成 GVCF
```bash
REF="./ref_genomic/TAIR10_chr_all.fas"

for sample in 1-37 27-3-1 27N Neg top1α-10
do
  gatk --java-options "-Xmx10G" HaplotypeCaller \
    -R ${REF} \
    -I 03_alignment/${sample}.sorted.markup.bam \
    -O 04_snp_calling/${sample}.g.vcf.gz \
    -ERC GVCF \
    -stand-call-conf 10
done
```

## 6. 合并 GVCF 与联合分型
```bash
REF="./ref_genomic/TAIR10_chr_all.fas"

gatk CombineGVCFs \
  -R ${REF} \
  -V 04_snp_calling/1-37.g.vcf.gz \
  -V 04_snp_calling/Neg.g.vcf.gz \
  -V 04_snp_calling/top1α-10.g.vcf.gz \
  -O 04_snp_calling/BSA-37.gvcf.gz

gatk CombineGVCFs \
  -R ${REF} \
  -V 04_snp_calling/27-3-1.g.vcf.gz \
  -V 04_snp_calling/27N.g.vcf.gz \
  -V 04_snp_calling/top1α-10.g.vcf.gz \
  -O 04_snp_calling/BSA-27.gvcf.gz

gatk GenotypeGVCFs \
  -R ${REF} \
  -V 04_snp_calling/BSA-27.gvcf.gz \
  -O 05_snp/BSA_no_filter-27.HC.vcf
```

## 7. SNP/INDEL 硬过滤
```bash
gatk SelectVariants \
  -R ./ref_genomic/TAIR10_chr_all.fas \
  -V 05_snp/BSA_no_filter-27.HC.vcf \
  -select-type SNP \
  -O 05_snp/SNPs-27.vcf

gatk VariantFiltration \
  -V 05_snp/SNPs-27.vcf \
  --filter-expression "MQ < 30.0" \
  --filter-name "MQ_filter_SNP" \
  --filter-expression "QD < 2.0" \
  --filter-name "QD_filter_SNP" \
  -O 05_snp/SNPs_filter-27.vcf

grep -E '^#|PASS' 05_snp/SNPs_filter-27.vcf > 05_snp/BSA_SNPs_filterPASSED-27.vcf
```

INDEL 可继续使用 `SelectVariants -select-type INDEL` 后按 `MQ`、`SOR`、`QD`、`FS` 进行硬过滤，并与 SNP 结果合并为最终 VCF。

## 8. R 下游：SNP-index 与 ED5 定位
```r
library(QTLseqr)
library(vcfR)
library(ggplot2)
library(dplyr)

vcf <- read.vcfR("BSA_SNPs_filterPASSED-27.vcf")
chrom <- getCHROM(vcf)
pos <- getPOS(vcf)
ref <- getREF(vcf)
alt <- getALT(vcf)
ad <- extract.gt(vcf, "AD")
gt <- extract.gt(vcf, "GT")

ref_split <- masplit(ad, record = 1, sort = 0)
alt_split <- masplit(ad, record = 2, sort = 0)

df <- data.frame(
  CHROM = chrom,
  POS = pos,
  REF = ref,
  ALT = alt,
  AD_REF.1_37 = ref_split[, 1],
  AD_ALT.1_37 = alt_split[, 1],
  AD_REF.Neg = ref_split[, 2],
  AD_ALT.Neg = alt_split[, 2],
  AD_REF.top1 = ref_split[, 3],
  AD_ALT.top1 = alt_split[, 3],
  P_Top1 = gt[, "top1α-10"],
  son_1_37 = gt[, "1-37"],
  son_Neg = gt[, "Neg"]
)

df <- df %>%
  filter(
    nchar(as.character(REF)) == 1,
    nchar(as.character(ALT)) == 1,
    !is.na(P_Top1),
    (AD_REF.1_37 + AD_ALT.1_37) >= 10,
    (AD_REF.Neg + AD_ALT.Neg) >= 10,
    (AD_REF.top1 + AD_ALT.top1) >= 10
  )
```

```r
df_result <- df %>%
  mutate(
    SNPindex.L = AD_ALT.1_37 / (AD_REF.1_37 + AD_ALT.1_37),
    SNPindex.S = AD_ALT.Neg / (AD_REF.Neg + AD_ALT.Neg),
    deltaSNP = SNPindex.L - SNPindex.S
  )

delta_extreme_points <- df_result %>%
  filter(deltaSNP > 0.5 | deltaSNP < -0.5)

ggplot(df_result, aes(x = POS / 1e6, y = deltaSNP)) +
  geom_point(color = "#000000", size = 0.5, alpha = 0.6) +
  geom_point(
    data = delta_extreme_points,
    aes(color = ifelse(deltaSNP > 0, "Positive", "Negative")),
    size = 1.2,
    alpha = 0.8
  ) +
  geom_hline(yintercept = c(-0.5, 0.5), linetype = "dashed") +
  facet_wrap(~ CHROM, scales = "free_x", nrow = 3) +
  labs(x = "Genomic Position (Mb)", y = "Delta SNP-index")
```

```r
valid_rows <- complete.cases(df) &
  df$AD_REF.1_37 + df$AD_ALT.1_37 > 0 &
  df$AD_REF.Neg + df$AD_ALT.Neg > 0

df_filtered <- df[valid_rows, ]

ED_values <- apply(df_filtered, 1, function(row) {
  ref_mutant <- as.numeric(row["AD_REF.1_37"])
  alt_mutant <- as.numeric(row["AD_ALT.1_37"])
  ref_wild <- as.numeric(row["AD_REF.Neg"])
  alt_wild <- as.numeric(row["AD_ALT.Neg"])

  depth_mutant <- ref_mutant + alt_mutant
  depth_wild <- ref_wild + alt_wild

  freq_ref_mutant <- ref_mutant / depth_mutant
  freq_alt_mutant <- alt_mutant / depth_mutant
  freq_ref_wild <- ref_wild / depth_wild
  freq_alt_wild <- alt_wild / depth_wild

  freq_diff <- sqrt(
    (freq_ref_wild - freq_ref_mutant)^2 +
      (freq_alt_wild - freq_alt_mutant)^2
  )

  freq_diff^5
})

result_df <- data.frame(
  CHROM = df_filtered$CHROM,
  POS = df_filtered$POS,
  ED = ED_values
)
```

## 关键质控与解释
- FASTQ 阶段关注碱基质量、接头残留和头部异常碱基，当前流程使用 `HEADCROP:2`。
- 比对阶段保留 read group，方便 GATK 正确识别样本。
- GVCF 阶段采用每个样本单独 HaplotypeCaller，再按组合合并和联合分型。
- SNP 过滤至少包含 `MQ >= 30` 与 `QD >= 2`；INDEL 过滤可加入 `SOR` 和 `FS`。
- 下游定位同时看 `Delta SNP-index` 和 `ED5`，比只看单一指标更稳。

## 主要输出
- FastQC 质控报告
- Trimmomatic clean reads
- 排序和去重后的 BAM
- 样本级 GVCF
- 合并分型 VCF
- 过滤后的 SNP/INDEL VCF
- SNP-index / Delta SNP-index 图
- ED5 全基因组定位图
""",
        },
    ]


PIPELINE_CATEGORIES: dict[str, str] = {
    "basic": "转录组基础与表达变化",
    "structure": "转录组结构与网络",
    "mechanism": "机制解释与多组学调控",
    "cancer": "肿瘤转录组与临床应用",
    "advanced-transcriptomics": "长读长、翻译组与非模式物种",
    "single-spatial": "单细胞与空间组学",
    "variant": "基因组变异与定位",
    "epigenomics": "表观调控实验",
    "other": "其他分析流程",
}


def infer_pipeline_category(item: dict[str, Any]) -> tuple[str, str]:
    title = str(item["title"])
    omics_type = str(item["omics_type"])

    if omics_type in {"scRNA-Seq", "Spatial Transcriptomics"}:
        category_key = "single-spatial"
    elif omics_type in {"WGS", "BSA-seq"}:
        category_key = "variant"
    elif omics_type == "CUT&Tag":
        category_key = "epigenomics"
    elif omics_type == "Cancer Transcriptomics":
        category_key = "cancer"
    elif omics_type in {"Long-read Transcriptomics", "Translatomics", "De novo Transcriptomics"}:
        category_key = "advanced-transcriptomics"
    elif omics_type in {"Multi-omics", "Regulatory Network", "Pathway Analysis", "Immunogenomics"}:
        category_key = "mechanism"
    elif (
        "WGCNA" in title
        or "rMATS" in title
        or "SUPPA2" in title
        or "RNA editing" in title
    ):
        category_key = "structure"
    elif omics_type == "RNA-Seq":
        category_key = "basic"
    else:
        category_key = "other"

    return category_key, PIPELINE_CATEGORIES[category_key]


def infer_pipeline_metadata(item: dict[str, Any]) -> dict[str, Any]:
    title = str(item["title"])
    omics_type = str(item["omics_type"])
    content = str(item["content"])

    advanced_keywords = [
        "多组学",
        "肿瘤",
        "长读长",
        "Ribo",
        "RNA editing",
        "融合基因",
        "单细胞高级",
    ]
    intermediate_keywords = [
        "WGCNA",
        "rMATS",
        "SUPPA2",
        "时间序列",
        "lncRNA",
        "circRNA",
        "miRNA",
        "GSVA",
        "免疫浸润",
        "Visium",
    ]

    if any(keyword in title for keyword in advanced_keywords):
        difficulty = "高级"
        estimated_time = "3-5 天"
    elif any(keyword in title for keyword in intermediate_keywords):
        difficulty = "中级"
        estimated_time = "1-3 天"
    else:
        difficulty = "入门"
        estimated_time = "0.5-1 天"

    tool_keywords = [
        "DESeq2",
        "STAR",
        "featureCounts",
        "Salmon",
        "tximport",
        "WGCNA",
        "rMATS",
        "SUPPA2",
        "maSigPro",
        "ImpulseDE2",
        "StringTie",
        "CIRI2",
        "miRDeep2",
        "Space Ranger",
        "Seurat",
        "Squidpy",
        "Monocle3",
        "CellChat",
        "scVelo",
        "DoRothEA",
        "VIPER",
        "ChEA3",
        "GSVA",
        "ssGSEA",
        "CIBERSORT",
        "xCell",
        "ESTIMATE",
        "STAR-Fusion",
        "Arriba",
        "REDItools",
        "GIREMI",
        "SnpEff",
        "ANNOVAR",
        "Iso-Seq",
        "Nanopore",
        "FLAIR",
        "TALON",
        "RiboCode",
        "Trinity",
    ]
    tools = []
    searchable_text = f"{title}\n{content}"
    for tool in tool_keywords:
        if tool == "ESTIMATE":
            if "ESTIMATE immune" in searchable_text or "estimate_score" in searchable_text:
                tools.append(tool)
            continue

        if tool.lower() in searchable_text.lower():
            tools.append(tool)

    inputs: list[str] = []
    for candidate in ["FASTQ", "BAM", "VCF", "GTF", "count matrix", "TPM", "expression matrix", "scRNA-seq object", "Visium image"]:
        if candidate.lower() in content.lower() or candidate.lower() in title.lower():
            inputs.append(candidate)

    outputs: list[str] = []
    output_candidates = [
        "DEG table",
        "heatmap",
        "volcano plot",
        "hub genes",
        "fusion candidates",
        "editing sites",
        "isoform annotation",
        "ORF table",
        "transcript assembly",
        "pathway score",
        "immune score",
        "Sashimi plot",
        "UMAP",
        "report",
    ]
    for candidate in output_candidates:
        if candidate.lower() in content.lower() or candidate.lower() in title.lower():
            outputs.append(candidate)

    scenario_by_type = {
        "RNA-Seq": "转录组分析",
        "scRNA-Seq": "单细胞分析",
        "Spatial Transcriptomics": "空间转录组",
        "Multi-omics": "多组学机制解释",
        "Regulatory Network": "调控网络",
        "Pathway Analysis": "通路活性",
        "Immunogenomics": "免疫微环境",
        "Cancer Transcriptomics": "肿瘤转录组",
        "Long-read Transcriptomics": "长读长转录组",
        "Translatomics": "翻译组",
        "De novo Transcriptomics": "非模式物种",
        "CUT&Tag": "表观调控",
        "WGS": "基因组变异",
        "BSA-seq": "遗传定位",
    }

    return {
        "difficulty": difficulty,
        "tools": tools[:8],
        "inputs": inputs[:6],
        "outputs": outputs[:6],
        "estimated_time": estimated_time,
        "scenario": scenario_by_type.get(omics_type, omics_type),
    }


def seed_pipelines(db: Session) -> None:
    # Pipeline Hub 的 Mock 数据按标题 upsert，便于迭代时追加 CUT&Tag 等新流程。
    legacy_titles = {
        "Bulk RNA-seq 标准差异表达分析增强版": ["RNA-Seq 差异表达分析"],
    }

    for item in build_mock_pipelines():
        item["metadata_json"] = item.get("metadata_json") or infer_pipeline_metadata(item)
        item["category_key"], item["category_name"] = infer_pipeline_category(item)
        pipeline = db.scalar(select(Pipeline).where(Pipeline.title == item["title"]))
        if pipeline is None:
            for legacy_title in legacy_titles.get(item["title"], []):
                pipeline = db.scalar(select(Pipeline).where(Pipeline.title == legacy_title))
                if pipeline is not None:
                    break

        if pipeline is None:
            db.add(Pipeline(**item))
            continue

        pipeline.title = item["title"]
        pipeline.description = item["description"]
        pipeline.omics_type = item["omics_type"]
        pipeline.category_key = item["category_key"]
        pipeline.category_name = item["category_name"]
        pipeline.dag_json = item["dag_json"]
        pipeline.metadata_json = item["metadata_json"]
        pipeline.content = item["content"]

    db.commit()
