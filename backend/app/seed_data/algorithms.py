from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Algorithm


ALGORITHM_METADATA_OVERRIDES: dict[str, dict[str, str]] = {
    "STAR": {
        "official_docs_url": "https://github.com/alexdobin/STAR",
        "version": "2.7.11b（校验于 2026-06-01；执行前请以官方稳定版为准）",
        "installation": "Bioconda: mamba install -c bioconda star",
    },
    "Salmon": {
        "official_docs_url": "https://salmon.readthedocs.io/en/latest/",
        "version": "1.11.4（校验于 2026-06-01；执行前请以官方稳定版为准）",
        "installation": "Bioconda: mamba install -c bioconda salmon",
    },
    "featureCounts": {
        "official_docs_url": "https://subread.sourceforge.net/featureCounts.html",
        "version": "Subread 2.1.1（校验于 2026-06-01；执行前请以官方稳定版为准）",
        "installation": "Bioconda: mamba install -c bioconda subread",
    },
    "DESeq2": {
        "official_docs_url": "https://bioconductor.org/packages/release/bioc/html/DESeq2.html",
        "version": "1.52.0（校验于 2026-06-01；执行前请以官方稳定版为准）",
        "installation": 'Bioconductor: BiocManager::install("DESeq2")',
    },
    "Cell Ranger": {
        "official_docs_url": "https://www.10xgenomics.com/support/software/cell-ranger",
        "version": "10.0（校验于 2026-06-01；执行前请以官方稳定版为准）",
        "installation": "Download and install the official 10x Genomics tarball",
    },
    "Seurat v5": {
        "official_docs_url": "https://satijalab.org/seurat/",
        "version": "5.5.0（校验于 2026-06-01；执行前请以官方稳定版为准）",
        "installation": 'CRAN: install.packages("Seurat")',
    },
}


def infer_algorithm_metadata(item: dict[str, Any]) -> dict[str, Any]:
    override = ALGORITHM_METADATA_OVERRIDES.get(str(item["name"]), {})
    data_types = [str(value) for value in item.get("inputs", [])]

    return {
        "validation_status": "文档校验",
        "last_reviewed_at": "2026-06-01",
        "difficulty": "进阶",
        "official_docs_url": override.get("official_docs_url"),
        "version": override.get("version", "请以官方文档最新稳定版为准"),
        "installation": override.get(
            "installation",
            "优先使用官方安装说明或 Bioconda/Conda 环境隔离安装",
        ),
        "applicability": {
            "species": ["Human", "Mouse", "Plant"],
            "data_types": data_types or [str(item["category"])],
            "experiment_types": [str(item["category_name"])],
        },
        "disclaimer": (
            "软件版本和默认参数可能变化。正式分析前请结合官方文档、"
            "数据规模和实验设计复核配置。"
        ),
    }


def build_performance_json(
    x_axis: list[str],
    time_data: list[float],
    memory_data: list[float],
    time_unit: str,
    environment: str,
) -> dict[str, Any]:
    return {
        "x_axis": x_axis,
        "series": [
            {
                "name": "时间消耗",
                "unit": time_unit,
                "y_axis": "time",
                "data": time_data,
            },
            {
                "name": "峰值内存",
                "unit": "GB",
                "y_axis": "memory",
                "data": memory_data,
            },
        ],
        "environment": environment,
    }


def build_markdown_docs(
    title: str,
    positioning: str,
    core_idea: str,
    command: str,
    inputs: list[str],
    outputs: list[str],
    cautions: list[str],
    language: str = "bash",
) -> str:
    input_rows = "\n".join(f"| {item} | 上游分析输入 |" for item in inputs)
    output_rows = "\n".join(f"| {item} | 下游解读结果 |" for item in outputs)
    caution_lines = "\n".join(f"{index}. {item}" for index, item in enumerate(cautions, 1))

    return f"""# {title}

## 工具定位
{positioning}

## 核心思想
{core_idea}

## 输入与输出
| 数据对象 | 说明 |
| --- | --- |
{input_rows}
{output_rows}

## 示例命令
```{language}
{command}
```

## 解读要点
{caution_lines}
"""


def build_detailed_algorithm_docs() -> dict[str, str]:
    return {
        "STAR": """# STAR RNA-seq 比对器

## 工具定位
STAR 是 RNA-seq 中最常用的 splice-aware aligner 之一，负责把 reads 精确比对到参考基因组，并识别 exon-exon junction。它常作为 bulk RNA-seq、可变剪接 rMATS、融合基因 STAR-Fusion/Arriba 的上游基础。

## 适用场景
- 适合：bulk RNA-seq、poly(A) RNA-seq、ribo-depleted RNA-seq、融合基因检测前处理、剪接分析前处理。
- 不适合：只想快速得到转录本丰度且不关心 BAM 的项目，此时 Salmon/Kallisto 更轻量。

## 输入与输出
| 类型 | 文件 | 说明 |
| --- | --- | --- |
| 输入 | `genome.fa` | 参考基因组 |
| 输入 | `genes.gtf` | 基因注释，决定 junction 和 feature 的解释 |
| 输入 | `sample_R1.fq.gz`, `sample_R2.fq.gz` | 双端 RNA-seq FASTQ |
| 输出 | `Aligned.sortedByCoord.out.bam` | 排序后的 BAM |
| 输出 | `SJ.out.tab` | splice junction 结果 |
| 输出 | `Log.final.out` | 比对率、唯一比对率、多重比对率等 QC |

## 安装方式
```bash
mamba create -n rnaseq-star -c bioconda -c conda-forge star samtools fastqc multiqc
conda activate rnaseq-star
STAR --version
```

## 推荐项目目录
```text
project_star/
├── 00_rawdata/
├── 01_qc/
├── 02_reference/
│   ├── genome.fa
│   └── genes.gtf
├── 03_star_index/
├── 04_bam/
├── 05_logs/
└── scripts/
```

## 最小可运行示例
```bash
mkdir -p 03_star_index 04_bam 05_logs

STAR --runThreadN 16 \\
  --runMode genomeGenerate \\
  --genomeDir 03_star_index \\
  --genomeFastaFiles 02_reference/genome.fa \\
  --sjdbGTFfile 02_reference/genes.gtf \\
  --sjdbOverhang 149

STAR --runThreadN 16 \\
  --genomeDir 03_star_index \\
  --readFilesIn 00_rawdata/sample_R1.fq.gz 00_rawdata/sample_R2.fq.gz \\
  --readFilesCommand zcat \\
  --outSAMtype BAM SortedByCoordinate \\
  --outFileNamePrefix 04_bam/sample.

samtools index 04_bam/sample.Aligned.sortedByCoord.out.bam
```

## 常用参数表
| 参数 | 含义 | 推荐值 | 注意事项 |
| --- | --- | --- | --- |
| `--runThreadN` | 线程数 | 8-32 | 线程越多越快，但受磁盘 IO 限制 |
| `--runMode genomeGenerate` | 构建索引模式 | 构建索引时使用 | 只需对同一参考构建一次 |
| `--genomeDir` | STAR 索引目录 | `03_star_index` | 比对时必须和建索引目录一致 |
| `--sjdbGTFfile` | 注释文件 | GENCODE/Ensembl GTF | 强烈建议提供 |
| `--sjdbOverhang` | read length - 1 | PE150 用 149 | 影响 junction 索引 |
| `--readFilesCommand` | 读取压缩文件命令 | `zcat` | `.fq.gz` 必填 |
| `--outSAMtype` | 输出 BAM/SAM 格式 | `BAM SortedByCoordinate` | 方便直接接 featureCounts |
| `--quantMode` | 同时输出计数 | `GeneCounts` 可选 | 简单计数可用，但正式 DEG 更常用 featureCounts |

## 结果解读
- `Uniquely mapped reads %`：通常希望 bulk RNA-seq 高于 70%，低于 60% 要检查污染、参考基因组或文库质量。
- `% of reads mapped to multiple loci`：重复序列或同源基因多时会升高。
- `SJ.out.tab`：可用于剪接事件、novel junction 和 rMATS 上游检查。
- BAM 可进入 IGV 查看目标基因覆盖度和 junction 支持。

## 常见错误
| 问题 | 可能原因 | 解决办法 |
| --- | --- | --- |
| 建索引内存不足 | 基因组过大 | 提高内存或使用 HISAT2 |
| 比对率很低 | 物种/参考版本错误 | 检查 FASTQ 物种、接头污染和 genome.fa |
| junction 异常少 | GTF 不匹配或未提供 | 统一 genome 与 GTF 来源 |

## 关联流程
- Bulk RNA-seq 标准差异表达分析增强版
- 可变剪接分析 rMATS/SUPPA2
- 融合基因检测 STAR-Fusion/Arriba
""",
        "Salmon": """# Salmon 转录本定量

## 工具定位
Salmon 是快速 transcript-level quantification 工具，常用于 `Salmon -> tximport -> DESeq2` 流程。它不需要传统 genome BAM，适合大批量样本快速定量。

## 适用场景
- 适合：bulk RNA-seq 快速定量、转录本层面 TPM、gene-level DEG 上游输入。
- 不适合：必须检查 read coverage、剪接位点、融合基因或 IGV 可视化的项目。

## 输入与输出
| 类型 | 文件 | 说明 |
| --- | --- | --- |
| 输入 | `transcripts.fa` | 转录本序列 |
| 输入 | `sample_R1.fq.gz`, `sample_R2.fq.gz` | 双端 FASTQ |
| 输出 | `quant.sf` | TPM、NumReads、EffectiveLength |
| 输出 | `aux_info/` | 运行信息和偏倚模型 |

## 安装方式
```bash
mamba create -n salmon-rnaseq -c bioconda -c conda-forge salmon fastqc multiqc
conda activate salmon-rnaseq
salmon --version
```

## 推荐项目目录
```text
project_salmon/
├── 00_rawdata/
├── 01_reference/
│   └── transcripts.fa
├── 02_salmon_index/
├── 03_quant/
└── scripts/
```

## 最小可运行示例
```bash
salmon index \\
  -t 01_reference/transcripts.fa \\
  -i 02_salmon_index \\
  -k 31

salmon quant \\
  -i 02_salmon_index \\
  -l A \\
  -1 00_rawdata/sample_R1.fq.gz \\
  -2 00_rawdata/sample_R2.fq.gz \\
  -p 12 \\
  --validateMappings \\
  -o 03_quant/sample
```

## 常用参数表
| 参数 | 含义 | 推荐值 | 注意事项 |
| --- | --- | --- | --- |
| `-t` | 转录本 FASTA | Ensembl/GENCODE transcriptome | 与 tx2gene 注释保持一致 |
| `-i` | 索引目录 | `02_salmon_index` | 同一参考只建一次 |
| `-k` | k-mer 长度 | 31 | reads 很短时可适当降低 |
| `-l` | 文库类型 | `A` | 自动推断，正式项目仍建议记录 |
| `--validateMappings` | selective alignment | 建议开启 | 提高定量准确性 |
| `--gcBias` | GC 偏倚校正 | 可开启 | 样本偏倚明显时有帮助 |
| `--seqBias` | 序列偏倚校正 | 可开启 | 常用于正式 RNA-seq 项目 |
| `-p` | 线程数 | 8-16 | 大队列可并行样本 |

## 结果解读
- `TPM`：适合样本内或展示表达量，不建议直接用于 DESeq2 差异检验。
- `NumReads`：可通过 tximport 汇总到 gene 层面，作为 DESeq2 输入。
- `EffectiveLength`：反映转录本有效长度，受 bias correction 影响。

## 常见错误
| 问题 | 可能原因 | 解决办法 |
| --- | --- | --- |
| mapping rate 低 | transcriptome 版本或物种错误 | 检查 FASTQ 来源和 transcript FASTA |
| tximport 基因 ID 对不上 | tx2gene 表不匹配 | 从同一 GTF 生成 tx2gene |
| DEG 与 STAR 流程差异大 | isoform 汇总策略不同 | 检查 tximport 参数和过滤策略 |

## 关联流程
- Salmon + tximport + DESeq2
- Bulk RNA-seq 标准差异表达分析增强版
""",
        "featureCounts": """# featureCounts 基因计数

## 工具定位
featureCounts 用于把 STAR/HISAT2 得到的 BAM 按 GTF 注释汇总成 gene count matrix，是 `STAR -> featureCounts -> DESeq2` 流程的关键节点。

## 适用场景
- 适合：bulk RNA-seq gene-level count、ChIP/CUT&Tag 区域计数、标准差异分析上游。
- 不适合：isoform-level 定量，此时 Salmon/StringTie 更合适。

## 输入与输出
| 类型 | 文件 | 说明 |
| --- | --- | --- |
| 输入 | `*.bam` | 排序后的比对文件 |
| 输入 | `genes.gtf` | 基因注释 |
| 输出 | `counts.txt` | gene count matrix |
| 输出 | `counts.txt.summary` | reads 分配统计 |

## 安装方式
```bash
mamba create -n featurecounts -c bioconda -c conda-forge subread samtools
conda activate featurecounts
featureCounts -v
```

## 推荐项目目录
```text
project_featurecounts/
├── 04_bam/
├── 05_counts/
├── reference/
│   └── genes.gtf
└── scripts/
```

## 最小可运行示例
```bash
mkdir -p 05_counts

featureCounts \\
  -T 8 \\
  -p \\
  -t exon \\
  -g gene_id \\
  -a reference/genes.gtf \\
  -o 05_counts/gene_counts.txt \\
  04_bam/*.bam
```

## 常用参数表
| 参数 | 含义 | 推荐值 | 注意事项 |
| --- | --- | --- | --- |
| `-T` | 线程数 | 4-12 | 通常很快，不必过高 |
| `-p` | 双端 reads | PE 数据开启 | 单端数据不要加 |
| `-t` | feature 类型 | `exon` | 与 GTF 第三列匹配 |
| `-g` | 汇总 ID | `gene_id` | 做 gene-level DEG 最常用 |
| `-s` | 链特异性 | 0/1/2 | 必须按建库方式设置 |
| `-Q` | MAPQ 阈值 | 10 或 20 | 可过滤低质量比对 |
| `-M` | 计入 multi-mapping reads | 谨慎开启 | 默认不计入更稳妥 |
| `--fraction` | 多重比对分数计数 | 视项目而定 | 与 `-M` 搭配使用 |

## 结果解读
- `Assigned` 比例越高，说明 reads 更好地落在注释 feature 上。
- `Unassigned_NoFeatures` 高可能是注释版本不匹配、物种错误或 rRNA/lncRNA 比例高。
- `Unassigned_Ambiguity` 高常见于重叠基因或复杂注释区域。

## 常见错误
| 问题 | 可能原因 | 解决办法 |
| --- | --- | --- |
| count 很低 | `-s` 链特异设置错误 | 用 RSeQC 或文库说明确认 |
| 所有样本列名太长 | BAM 路径进入列名 | 后续在 R 中重命名列 |
| gene_id 缺失 | GTF 字段不同 | 改用 `-g gene_name` 或整理 GTF |

## 关联流程
- Bulk RNA-seq 标准差异表达分析增强版
- STAR + featureCounts + DESeq2 + TPM
""",
        "DESeq2": """# DESeq2 差异表达分析

## 工具定位
DESeq2 是 bulk RNA-seq 差异表达分析最常用的 R 包之一，用于对 count matrix 建模，输出 log2FoldChange、pvalue 和 padj。

## 适用场景
- 适合：有生物学重复的 bulk RNA-seq、标准两组比较、多因素实验设计。
- 不适合：无重复样本的正式统计检验、TPM/FPKM 直接差异分析。

## 输入与输出
| 类型 | 文件 | 说明 |
| --- | --- | --- |
| 输入 | `gene_counts.txt` | raw counts，不能是 TPM |
| 输入 | `metadata.tsv` | 样本分组、批次、时间等信息 |
| 输出 | `DEG_results.tsv` | 差异表达结果 |
| 输出 | `normalized_counts.tsv` | 标准化 counts |
| 输出 | PCA/MA/volcano plot | 质量控制和结果展示 |

## 安装方式
```r
if (!requireNamespace("BiocManager", quietly = TRUE)) install.packages("BiocManager")
BiocManager::install(c("DESeq2", "apeglm", "pheatmap"))
```

## 推荐项目目录
```text
project_deseq2/
├── 00_counts/
│   └── gene_counts.txt
├── 01_metadata/
│   └── metadata.tsv
├── 02_results/
├── 03_plots/
└── scripts/
```

## 最小可运行示例
```r
library(DESeq2)

counts <- read.table("00_counts/gene_counts.txt", header = TRUE, row.names = 1, check.names = FALSE)
meta <- read.table("01_metadata/metadata.tsv", header = TRUE, sep = "\t", row.names = 1)
counts <- counts[, rownames(meta)]

dds <- DESeqDataSetFromMatrix(
  countData = round(counts),
  colData = meta,
  design = ~ group
)

dds <- dds[rowSums(counts(dds)) >= 10, ]
dds <- DESeq(dds)
res <- results(dds, contrast = c("group", "treat", "control"))
res <- lfcShrink(dds, contrast = c("group", "treat", "control"), res = res, type = "apeglm")
write.csv(as.data.frame(res), "02_results/DESeq2_treat_vs_control.csv")
```

## 常用参数表
| 参数/函数 | 含义 | 推荐用法 | 注意事项 |
| --- | --- | --- | --- |
| `design` | 实验设计公式 | `~ group` 或 `~ batch + group` | 批次和分组不能完全混杂 |
| `contrast` | 指定比较 | `c("group","treat","control")` | 顺序决定 log2FC 方向 |
| `DESeq()` | 主分析函数 | 默认 | 包含 size factor、dispersion 和 GLM |
| `lfcShrink()` | log2FC 收缩 | `type="apeglm"` | 排序和展示更稳健 |
| `alpha` | FDR 阈值 | 0.05 | 与 padj 判断一致 |
| `independentFiltering` | 独立过滤 | 默认 TRUE | 通常保留默认 |
| `blind` | vst/rlog 是否盲化 | PCA 用 TRUE/视情况 | 强处理效应项目可设 FALSE |

## 结果解读
- `log2FoldChange > 0`：在 contrast 的第一个水平中更高。
- `padj < 0.05`：经过多重检验校正后显著。
- `baseMean` 很低的基因即使 log2FC 大，也要谨慎解释。
- PCA 如果按批次分开而不是处理组分开，需要考虑批次校正或设计公式。

## 常见错误
| 问题 | 可能原因 | 解决办法 |
| --- | --- | --- |
| 报错 counts 不是整数 | 输入用了 TPM/FPKM | 换 raw counts |
| 样本顺序错 | count 列名和 metadata 行名不一致 | 强制 `counts <- counts[, rownames(meta)]` |
| 结果方向反了 | contrast 顺序写反 | 明确 treat/control 顺序 |
| padj 全 NA | 低表达太多或样本太少 | 过滤低表达，检查重复数 |

## 关联流程
- Bulk RNA-seq 标准差异表达分析增强版
- Salmon + tximport + DESeq2
- STAR + featureCounts + DESeq2 + TPM
""",
        "Cell Ranger": """# Cell Ranger 10x 单细胞预处理

## 工具定位
Cell Ranger 是 10x Genomics 官方单细胞预处理软件，用于从 BCL/FASTQ 生成可被 Seurat 或 Scanpy 读取的 feature-barcode matrix。

## 适用场景
- 适合：10x 3' Gene Expression、5' Gene Expression、Feature Barcode、VDJ 等官方体系。
- 不适合：非 10x 平台或自定义 barcode 结构数据。

## 输入与输出
| 类型 | 文件/目录 | 说明 |
| --- | --- | --- |
| 输入 | FASTQ 目录 | `cellranger mkfastq` 或 bcl-convert 输出 |
| 输入 | transcriptome reference | 10x 官方 reference 或自建 reference |
| 输出 | `filtered_feature_bc_matrix/` | 常用下游表达矩阵 |
| 输出 | `raw_feature_bc_matrix/` | 原始 barcode-feature 矩阵 |
| 输出 | `web_summary.html` | 最重要的 QC 报告 |
| 输出 | `cloupe.cloupe` | Loupe Browser 可视化文件 |

## 安装方式
```bash
# Cell Ranger 需从 10x Genomics 官网下载后加入 PATH
tar -xzvf cellranger-*.tar.gz
export PATH=$PWD/cellranger-*/:$PATH
cellranger --version
```

## 推荐项目目录
```text
project_cellranger/
├── 00_fastq/
├── 01_reference/
│   └── refdata-gex-GRCh38-2024-A/
├── 02_cellranger_count/
└── scripts/
```

## 最小可运行示例
```bash
cellranger count \\
  --id=sample01 \\
  --transcriptome=01_reference/refdata-gex-GRCh38-2024-A \\
  --fastqs=00_fastq \\
  --sample=sample01 \\
  --localcores=24 \\
  --localmem=128 \\
  --create-bam=true
```

## 常用参数表
| 参数 | 含义 | 推荐值 | 注意事项 |
| --- | --- | --- | --- |
| `--id` | 输出目录名 | 样本 ID | 不能包含复杂特殊字符 |
| `--transcriptome` | 参考目录 | 官方或自建 reference | 版本要全项目统一 |
| `--fastqs` | FASTQ 路径 | `00_fastq` | 可包含多个 lane |
| `--sample` | FASTQ sample 前缀 | 样本名 | 必须匹配 FASTQ 文件名 |
| `--localcores` | CPU 核数 | 16-32 | 与服务器资源匹配 |
| `--localmem` | 内存 GB | 64-128 | 细胞数多时提高 |
| `--expect-cells` | 预期细胞数 | 可选 | 细胞捕获数异常时使用 |
| `--create-bam` | 是否输出 BAM | true/false | BAM 很大，不需要可关闭 |

## 结果解读
- `Estimated Number of Cells`：估计细胞数，需和上机目标接近。
- `Mean Reads per Cell`：测序深度，过低会影响低表达基因检测。
- `Median Genes per Cell`：细胞复杂度，低值可能代表细胞质量差。
- `Fraction Reads in Cells`：reads 落入细胞 barcode 的比例，低值提示背景 RNA 或建库问题。

## 常见错误
| 问题 | 可能原因 | 解决办法 |
| --- | --- | --- |
| No input FASTQs found | `--sample` 与文件名不匹配 | 检查 FASTQ 命名 |
| 细胞数远低于预期 | 上样失败或细胞质量差 | 查看 web_summary 和 wet lab 信息 |
| reference 不合适 | 物种或版本错误 | 使用正确物种 reference 或自建 |

## 关联流程
- 10x 单细胞基础降维聚类
- 单细胞高级下游：拟时序、通讯、RNA velocity
""",
        "Seurat v5": """# Seurat v5 单细胞分析框架

## 工具定位
Seurat v5 是 R 生态中最常用的单细胞分析框架之一，负责从 feature-barcode matrix 出发完成 QC、归一化、降维、聚类、marker 鉴定、整合和注释。

## 适用场景
- 适合：10x scRNA-seq、整合多样本、marker gene 分析、细胞类型注释。
- 不适合：极大规模百万细胞项目的纯内存分析，此时可结合 BPCells、Sketch 或 Scanpy。

## 输入与输出
| 类型 | 文件/对象 | 说明 |
| --- | --- | --- |
| 输入 | `filtered_feature_bc_matrix/` | Cell Ranger 输出 |
| 输入 | sample metadata | 分组、批次、处理信息 |
| 输出 | Seurat object | 保存完整分析对象 |
| 输出 | UMAP/tSNE 图 | 细胞群可视化 |
| 输出 | marker gene 表 | 注释和机制分析依据 |

## 安装方式
```r
install.packages("Seurat")
install.packages(c("patchwork", "dplyr", "ggplot2"))
library(Seurat)
packageVersion("Seurat")
```

## 推荐项目目录
```text
project_seurat/
├── 00_cellranger/
│   └── sample01/outs/filtered_feature_bc_matrix/
├── 01_objects/
├── 02_qc/
├── 03_cluster/
├── 04_markers/
└── scripts/
```

## 最小可运行示例
```r
library(Seurat)
library(dplyr)

counts <- Read10X("00_cellranger/sample01/outs/filtered_feature_bc_matrix")
obj <- CreateSeuratObject(counts = counts, project = "sample01", min.cells = 3, min.features = 200)
obj[["percent.mt"]] <- PercentageFeatureSet(obj, pattern = "^MT-")

obj <- subset(obj, subset = nFeature_RNA > 200 & nFeature_RNA < 6000 & percent.mt < 15)
obj <- SCTransform(obj, vars.to.regress = "percent.mt")
obj <- RunPCA(obj)
obj <- FindNeighbors(obj, dims = 1:30)
obj <- FindClusters(obj, resolution = 0.6)
obj <- RunUMAP(obj, dims = 1:30)

markers <- FindAllMarkers(obj, only.pos = TRUE, min.pct = 0.25, logfc.threshold = 0.25)
saveRDS(obj, "01_objects/sample01_seurat.rds")
write.csv(markers, "04_markers/all_cluster_markers.csv")
```

## 常用参数表
| 参数/函数 | 含义 | 推荐值 | 注意事项 |
| --- | --- | --- | --- |
| `min.cells` | 基因至少出现细胞数 | 3 | 过滤极低可信基因 |
| `min.features` | 细胞至少检测基因数 | 200 | 初步过滤空 droplets |
| `percent.mt` | 线粒体比例 | 人鼠常用 <10-20% | 组织差异很大，不能机械套用 |
| `SCTransform()` | 归一化方法 | 推荐 | 多样本项目更稳健 |
| `dims` | 使用 PCA 维度 | 1:20 到 1:50 | 用 ElbowPlot/JackStraw 辅助 |
| `resolution` | 聚类分辨率 | 0.2-1.2 | 越高 cluster 越多 |
| `FindAllMarkers()` | marker 鉴定 | `only.pos=TRUE` | 后续用于细胞注释 |
| `vars.to.regress` | 回归变量 | `percent.mt` 可选 | 谨慎回归 cell cycle 等真实信号 |

## 结果解读
- QC 小提琴图：看 `nFeature_RNA`、`nCount_RNA`、`percent.mt` 是否有异常细胞。
- UMAP：相邻 cluster 不一定代表谱系关系，只是低维邻近。
- marker gene：注释细胞类型时要结合多个 marker，不要只看单个基因。
- resolution：需要根据组织、研究问题和 marker 清晰度调参。

## 常见错误
| 问题 | 可能原因 | 解决办法 |
| --- | --- | --- |
| 线粒体基因识别失败 | 物种前缀不同 | 人用 `^MT-`，小鼠常用 `^mt-` |
| cluster 过碎 | resolution 太高 | 降低 resolution 并检查 marker |
| 批次混在生物分组里 | 实验设计混杂 | 分析前先画样本来源 UMAP |
| 注释不稳定 | marker 不明确 | 结合 SingleR、Azimuth 或文献 marker |

## 关联流程
- 10x 单细胞基础降维聚类
- 单细胞高级下游：拟时序、通讯、RNA velocity
""",
    }


def build_algorithm(
    name: str,
    category: str,
    category_key: str,
    category_name: str,
    summary: str,
    positioning: str,
    core_idea: str,
    command: str,
    inputs: list[str],
    outputs: list[str],
    cautions: list[str],
    x_axis: list[str],
    time_data: list[float],
    memory_data: list[float],
    environment: str,
    tool_type: str | None = None,
    markdown_docs: str | None = None,
    time_unit: str = "分钟",
    language: str = "bash",
) -> dict[str, Any]:
    inferred_tool_type = tool_type
    if inferred_tool_type is None:
        if language == "r":
            inferred_tool_type = "R 包"
        elif language == "python":
            inferred_tool_type = "Python 包"
        else:
            inferred_tool_type = "命令行软件"

    item = {
        "name": name,
        "category": category,
        "category_key": category_key,
        "category_name": category_name,
        "tool_type": inferred_tool_type,
        "summary": summary,
        "performance_json": build_performance_json(
            x_axis=x_axis,
            time_data=time_data,
            memory_data=memory_data,
            time_unit=time_unit,
            environment=environment,
        ),
        "markdown_docs": markdown_docs or build_markdown_docs(
            title=name,
            positioning=positioning,
            core_idea=core_idea,
            command=command,
            inputs=inputs,
            outputs=outputs,
            cautions=cautions,
            language=language,
        ),
    }
    item["metadata_json"] = infer_algorithm_metadata({**item, "inputs": inputs})
    return item


def build_mock_algorithms() -> list[dict[str, Any]]:
    detailed_docs = build_detailed_algorithm_docs()

    return [
        build_algorithm(
            name="BWA-MEM",
            category="Alignment",
            category_key="alignment",
            category_name="比对与索引",
            summary="面向 WGS/WES 短读长数据的经典序列比对算法，常用于变异检测前置步骤。",
            positioning="BWA-MEM 适合 70 bp 到数 Mbp reads 的基因组比对，是 WGS、WES、Panel 项目中非常常见的标准工具。",
            core_idea="使用 FM-index 快速定位最大精确匹配片段，再通过种子扩展和链式打分生成 SAM/BAM 比对结果。",
            command="bwa index GRCh38.fa\nbwa mem -t 16 GRCh38.fa sample_R1.fq.gz sample_R2.fq.gz | samtools sort -o sample.bam\nsamtools index sample.bam",
            inputs=["参考基因组 FASTA", "双端 FASTQ"],
            outputs=["排序后的 BAM", "BAM index"],
            cautions=[
                "参考基因组版本必须与后续 GATK、ANNOVAR 或 VEP 注释版本一致。",
                "大队列项目建议固定 BWA 和 samtools 版本，避免批次差异。",
                "重复区域和结构变异区域的短读长比对结果需要谨慎解释。",
            ],
            x_axis=["10GB", "50GB", "100GB"],
            time_data=[48, 234, 456],
            memory_data=[5.2, 7.4, 9.8],
            environment="16 vCPU / 64GB RAM / GRCh38 / PE150",
        ),
        build_algorithm(
            name="STAR",
            category="RNA-seq Alignment",
            category_key="alignment",
            category_name="比对与索引",
            summary="高性能 RNA-seq splice-aware 比对器，适合 bulk RNA-seq、融合基因检测和剪接分析。",
            positioning="STAR 是转录组分析中最常见的剪接感知比对工具，能够识别跨 exon junction 的 reads。",
            core_idea="先构建基因组索引和 splice junction 索引，再用 seed search 与 stitching 策略完成高速比对。",
            command="STAR --runThreadN 16 --runMode genomeGenerate --genomeDir star_index --genomeFastaFiles genome.fa --sjdbGTFfile genes.gtf\nSTAR --runThreadN 16 --genomeDir star_index --readFilesIn R1.fq.gz R2.fq.gz --readFilesCommand zcat --outSAMtype BAM SortedByCoordinate",
            inputs=["参考基因组 FASTA", "GTF 注释", "RNA-seq FASTQ"],
            outputs=["排序后的转录组 BAM", "splice junction 表"],
            cautions=[
                "索引构建会消耗较多内存，植物或大型基因组需提前评估机器配置。",
                "融合基因、rMATS 和 featureCounts 常复用 STAR 输出的 BAM。",
                "多样本项目应统一 GTF 版本，否则 junction 和 gene count 难以比较。",
            ],
            x_axis=["20M reads", "80M reads", "160M reads"],
            time_data=[18, 55, 118],
            memory_data=[28, 31, 36],
            environment="24 threads / 128GB RAM / GENCODE annotation",
            markdown_docs=detailed_docs["STAR"],
        ),
        build_algorithm(
            name="HISAT2",
            category="RNA-seq Alignment",
            category_key="alignment",
            category_name="比对与索引",
            summary="轻量级 splice-aware RNA-seq 比对器，适合资源受限环境下的大规模样本处理。",
            positioning="HISAT2 使用分层索引结构进行快速比对，常用于标准转录组表达定量和可变剪接分析前处理。",
            core_idea="结合全局 FM-index 和局部 graph FM-index，提升剪接位点附近 reads 的定位效率。",
            command="hisat2-build genome.fa genome_hisat2\nhisat2 -p 12 -x genome_hisat2 -1 R1.fq.gz -2 R2.fq.gz | samtools sort -o sample.bam",
            inputs=["参考基因组 FASTA", "RNA-seq FASTQ"],
            outputs=["BAM", "比对统计日志"],
            cautions=[
                "若项目重点是融合基因检测，优先考虑 STAR 或 Arriba 推荐流程。",
                "剪接位点注释可提升比对质量，建议提供可信 GTF。",
                "和 STAR 相比内存更友好，但某些下游工具生态略少。",
            ],
            x_axis=["20M reads", "80M reads", "160M reads"],
            time_data=[22, 72, 146],
            memory_data=[7, 9, 12],
            environment="16 threads / 64GB RAM / PE150 RNA-seq",
        ),
        build_algorithm(
            name="Salmon",
            category="Quantification",
            category_key="quantification",
            category_name="表达定量",
            summary="无需传统比对的转录本定量工具，常与 tximport 和 DESeq2 构成快速 RNA-seq 流程。",
            positioning="Salmon 适合快速完成 transcript-level abundance estimation，并能输出 TPM 和 counts-like 结果。",
            core_idea="利用准映射和偏倚校正估计转录本丰度，再通过 EM 类算法分配多重匹配 reads。",
            command="salmon index -t transcripts.fa -i salmon_index\nsalmon quant -i salmon_index -l A -1 R1.fq.gz -2 R2.fq.gz -p 12 --validateMappings -o sample_quant",
            inputs=["转录本 FASTA", "RNA-seq FASTQ"],
            outputs=["quant.sf", "TPM 与 NumReads"],
            cautions=[
                "如果要做 gene-level DESeq2，建议用 tximport 汇总到 gene 层面。",
                "转录本注释质量会直接影响 isoform-level 结果可信度。",
                "跨物种或非模式物种项目要先检查 transcriptome 构建质量。",
            ],
            x_axis=["20M reads", "80M reads", "160M reads"],
            time_data=[8, 25, 51],
            memory_data=[4, 6, 9],
            environment="12 threads / 64GB RAM / selective alignment",
            markdown_docs=detailed_docs["Salmon"],
        ),
        build_algorithm(
            name="featureCounts",
            category="Quantification",
            category_key="quantification",
            category_name="表达定量",
            summary="从 BAM 文件生成 gene count matrix 的经典工具，适合 STAR/HISAT2 后接差异分析。",
            positioning="featureCounts 是 Subread 套件中的 read summarization 工具，常用于 bulk RNA-seq gene-level 计数。",
            core_idea="根据 GTF/GFF 注释将比对 reads 分配到 exon/gene feature，并生成样本级 count 矩阵。",
            command="featureCounts -T 8 -p -t exon -g gene_id -a genes.gtf -o counts.txt *.bam",
            inputs=["排序后的 BAM", "GTF/GFF 注释"],
            outputs=["gene count matrix", "assignment summary"],
            cautions=[
                "双端数据需要加 `-p`，链特异文库需要正确设置 `-s`。",
                "GTF 中 gene_id 字段必须和后续注释表保持一致。",
                "多重比对 reads 是否计入要根据研究目的明确记录。",
            ],
            x_axis=["6 BAM", "24 BAM", "48 BAM"],
            time_data=[6, 19, 43],
            memory_data=[2, 4, 7],
            environment="8 threads / GENCODE GTF / coordinate-sorted BAM",
            markdown_docs=detailed_docs["featureCounts"],
        ),
        build_algorithm(
            name="DESeq2",
            category="Differential Expression",
            category_key="differential-expression",
            category_name="差异表达分析",
            summary="基于负二项分布的 RNA-seq 差异表达分析 R 包，适合有生物学重复的 bulk RNA-seq。",
            positioning="DESeq2 是 bulk RNA-seq DEG 分析的核心工具之一，提供 normalization、dispersion estimation 和统计检验。",
            core_idea="使用 size factor 校正测序深度，以负二项 GLM 建模 counts，并通过 shrinkage 提高 log2FC 稳定性。",
            command="library(DESeq2)\ndds <- DESeqDataSetFromMatrix(countData = counts, colData = meta, design = ~ group)\ndds <- DESeq(dds)\nres <- results(dds, contrast = c('group', 'treat', 'control'))",
            inputs=["gene count matrix", "sample metadata"],
            outputs=["DEG 表", "标准化 counts", "PCA/MA plot"],
            cautions=[
                "至少需要合理生物学重复，单重复差异分析只能作为探索。",
                "设计公式要体现批次、处理、时间等实验因素。",
                "低表达基因过滤会显著影响多重检验负担和结果稳定性。",
            ],
            x_axis=["6 samples", "24 samples", "96 samples"],
            time_data=[1.5, 4.8, 19],
            memory_data=[1.2, 3.4, 10.5],
            environment="R 4.4 / 25k genes / negative binomial GLM",
            markdown_docs=detailed_docs["DESeq2"],
            language="r",
        ),
        build_algorithm(
            name="edgeR",
            category="Differential Expression",
            category_key="differential-expression",
            category_name="差异表达分析",
            summary="适合复杂设计和小样本 RNA-seq 的差异表达 R 包，提供 TMM 标准化和 GLM 框架。",
            positioning="edgeR 常用于 bulk RNA-seq、ChIP-seq count、CRISPR screen 等离散计数型数据差异分析。",
            core_idea="用 TMM 校正 library composition bias，估计离散度后在 exact test 或 GLM 框架下完成差异检验。",
            command="library(edgeR)\ny <- DGEList(counts = counts, group = meta$group)\ny <- calcNormFactors(y)\ndesign <- model.matrix(~ group, data = meta)\ny <- estimateDisp(y, design)\nfit <- glmQLFit(y, design)\nres <- glmQLFTest(fit, coef = 2)",
            inputs=["count matrix", "sample metadata"],
            outputs=["差异表达表", "TMM normalization factor"],
            cautions=[
                "复杂实验设计建议使用 glmQLFit，提高假阳性控制能力。",
                "过滤低表达基因前后要记录阈值，便于复现。",
                "和 DESeq2 结果可交叉比较，但不要机械追求完全一致。",
            ],
            x_axis=["6 samples", "24 samples", "96 samples"],
            time_data=[1.2, 3.9, 15],
            memory_data=[1.1, 2.9, 8.8],
            environment="R 4.4 / quasi-likelihood GLM",
            language="r",
        ),
        build_algorithm(
            name="limma-voom",
            category="Differential Expression",
            category_key="differential-expression",
            category_name="差异表达分析",
            summary="将 RNA-seq counts 转换为带权重的线性模型分析，适合复杂设计和大队列。",
            positioning="limma-voom 继承 limma 成熟的线性模型体系，适合批次、配对、交互项等复杂设计。",
            core_idea="通过 voom 估计 mean-variance trend，为每个观测值生成权重，再用 empirical Bayes 进行稳定检验。",
            command="library(limma)\nlibrary(edgeR)\ny <- DGEList(counts)\ny <- calcNormFactors(y)\ndesign <- model.matrix(~ batch + group, data = meta)\nv <- voom(y, design)\nfit <- eBayes(lmFit(v, design))\ntopTable(fit, coef = 'grouptreat')",
            inputs=["count matrix", "design matrix"],
            outputs=["差异分析结果", "voom mean-variance 图"],
            cautions=[
                "大队列和复杂设计时非常稳健，但需要认真构建设计矩阵。",
                "voom 图可用于检查均值方差关系是否被合理建模。",
                "批次变量不能与分组完全混杂，否则模型不可解释。",
            ],
            x_axis=["24 samples", "96 samples", "300 samples"],
            time_data=[2, 7, 26],
            memory_data=[2.1, 5.4, 17],
            environment="R 4.4 / limma 3.x / complex design",
            language="r",
        ),
        build_algorithm(
            name="Cell Ranger",
            category="Single-cell Preprocessing",
            category_key="single-cell",
            category_name="单细胞分析",
            summary="10x Genomics 官方预处理工具，用于 demultiplex、比对、定量和生成表达矩阵。",
            positioning="Cell Ranger 是 10x 单细胞项目从 FASTQ 到 feature-barcode matrix 的标准入口。",
            core_idea="根据 barcode/UMI 结构完成 reads 解析、比对、UMI collapsing 和细胞识别。",
            command="cellranger count --id=sample01 --transcriptome=/refs/refdata-gex-GRCh38-2024-A --fastqs=/data/fastq --sample=sample01 --localcores=24 --localmem=128",
            inputs=["10x FASTQ", "Cell Ranger transcriptome reference"],
            outputs=["filtered_feature_bc_matrix", "web_summary.html", "cloupe 文件"],
            cautions=[
                "web_summary.html 是判断测序深度和细胞质量的第一入口。",
                "多样本整合前要统一 reference 版本。",
                "Feature Barcode、VDJ 或 Multiome 数据需要选择对应子流程。",
            ],
            x_axis=["25GB FASTQ", "100GB FASTQ", "200GB FASTQ"],
            time_data=[84, 348, 672],
            memory_data=[18, 42, 76],
            environment="24 cores / 128GB RAM / 10x 3' GEX",
            markdown_docs=detailed_docs["Cell Ranger"],
        ),
        build_algorithm(
            name="Seurat v5",
            category="Single-cell",
            category_key="single-cell",
            category_name="单细胞分析",
            summary="R 生态中主流的单细胞分析框架，覆盖质控、整合、降维、聚类和注释。",
            positioning="Seurat v5 适合从表达矩阵出发完成标准 scRNA-seq 下游分析和多样本整合。",
            core_idea="通过 normalization、variable features、PCA、邻接图和聚类提取细胞群结构，再结合 marker gene 解读生物学状态。",
            command="library(Seurat)\nobj <- CreateSeuratObject(counts)\nobj <- SCTransform(obj)\nobj <- RunPCA(obj)\nobj <- FindNeighbors(obj, dims = 1:30)\nobj <- FindClusters(obj, resolution = 0.6)\nobj <- RunUMAP(obj, dims = 1:30)",
            inputs=["feature-barcode matrix", "sample metadata"],
            outputs=["Seurat object", "UMAP", "cluster markers"],
            cautions=[
                "聚类分辨率会影响细胞群粒度，需要结合 marker 和实验设计判断。",
                "整合时要避免把真实生物差异过度校正掉。",
                "marker 注释最好结合公开数据库和领域知识共同验证。",
            ],
            x_axis=["10k cells", "50k cells", "100k cells"],
            time_data=[6.5, 28.4, 63.2],
            memory_data=[4.8, 14.6, 31.5],
            environment="R 4.4 / Seurat v5 / SCTransform",
            markdown_docs=detailed_docs["Seurat v5"],
            language="r",
        ),
        build_algorithm(
            name="Scanpy",
            category="Single-cell",
            category_key="single-cell",
            category_name="单细胞分析",
            summary="Python 生态的单细胞分析框架，适合大规模 AnnData 数据处理和可复现脚本化分析。",
            positioning="Scanpy 常用于 Python 工作流中的 scRNA-seq 质控、归一化、聚类、marker 和可视化。",
            core_idea="以 AnnData 为核心数据结构，结合稀疏矩阵和邻接图算法完成高通量细胞图谱分析。",
            command="import scanpy as sc\nadata = sc.read_10x_mtx('filtered_feature_bc_matrix')\nsc.pp.filter_cells(adata, min_genes=200)\nsc.pp.normalize_total(adata)\nsc.pp.log1p(adata)\nsc.pp.highly_variable_genes(adata)\nsc.tl.pca(adata)\nsc.pp.neighbors(adata)\nsc.tl.umap(adata)\nsc.tl.leiden(adata)",
            inputs=["10x matrix", "AnnData h5ad"],
            outputs=["h5ad", "UMAP", "Leiden clusters"],
            cautions=[
                "Python 环境和包版本要固化，避免 numpy/scipy 版本冲突。",
                "大规模数据建议使用 h5ad 中间文件分阶段保存。",
                "与 Seurat 互转时要检查 layer、raw、obs 和 var 字段是否一致。",
            ],
            x_axis=["50k cells", "200k cells", "1M cells"],
            time_data=[18, 66, 310],
            memory_data=[8, 24, 96],
            environment="Python 3.11 / Scanpy / sparse matrix",
            language="python",
        ),
        build_algorithm(
            name="Harmony",
            category="Batch Correction",
            category_key="single-cell",
            category_name="单细胞分析",
            summary="常用单细胞批次校正算法，在 PCA 空间中整合多样本并保留主要生物差异。",
            positioning="Harmony 适合多个样本、批次或测序平台的 scRNA-seq 数据整合，常嵌入 Seurat/Scanpy 流程。",
            core_idea="在低维空间中迭代校正 batch effect，使不同批次中相似细胞状态靠近，同时保留聚类结构。",
            command="library(harmony)\nobj <- RunHarmony(obj, group.by.vars = 'batch')\nobj <- RunUMAP(obj, reduction = 'harmony', dims = 1:30)",
            inputs=["PCA embedding", "batch metadata"],
            outputs=["Harmony embedding", "整合后的 UMAP"],
            cautions=[
                "校正变量必须是技术批次或需要去除的混杂因素。",
                "不要用 Harmony 消除真正的疾病/处理组差异。",
                "校正前后都要检查 marker gene 和样本混合情况。",
            ],
            x_axis=["20k cells", "100k cells", "300k cells"],
            time_data=[4, 16, 49],
            memory_data=[3, 8, 21],
            environment="R 4.4 / Seurat object PCA",
            language="r",
        ),
        build_algorithm(
            name="Monocle3",
            category="Trajectory",
            category_key="single-cell",
            category_name="单细胞分析",
            summary="单细胞拟时序分析工具，用于推断细胞状态转换轨迹和动态基因表达变化。",
            positioning="Monocle3 适合发育、分化、刺激响应等连续状态项目，用拟时序解释细胞状态变化。",
            core_idea="在降维空间中学习 principal graph，并沿图结构为细胞分配 pseudotime。",
            command="library(monocle3)\ncds <- new_cell_data_set(counts, cell_metadata = meta, gene_metadata = genes)\ncds <- preprocess_cds(cds)\ncds <- reduce_dimension(cds)\ncds <- cluster_cells(cds)\ncds <- learn_graph(cds)\ncds <- order_cells(cds)",
            inputs=["count matrix", "cell metadata"],
            outputs=["pseudotime", "trajectory graph", "动态基因"],
            cautions=[
                "拟时序方向需要用已知 marker 或实验时间点锚定。",
                "轨迹不等于真实谱系因果，只能作为状态转变假设。",
                "分支点附近的基因动态需要结合生物学验证。",
            ],
            x_axis=["10k cells", "50k cells", "100k cells"],
            time_data=[7, 32, 78],
            memory_data=[5, 16, 34],
            environment="R 4.4 / Monocle3 / UMAP principal graph",
            language="r",
        ),
        build_algorithm(
            name="CellChat",
            category="Cell Communication",
            category_key="single-cell",
            category_name="单细胞分析",
            summary="基于配体-受体数据库推断细胞通讯网络，适合肿瘤微环境和免疫互作分析。",
            positioning="CellChat 用于从 scRNA-seq 表达矩阵推断细胞群之间的信号通路和 ligand-receptor 互作。",
            core_idea="聚合细胞群表达，匹配配体受体数据库，并估计不同细胞群之间的通讯概率。",
            command="library(CellChat)\ncellchat <- createCellChat(object = data.input, meta = meta, group.by = 'celltype')\ncellchat <- identifyOverExpressedGenes(cellchat)\ncellchat <- identifyOverExpressedInteractions(cellchat)\ncellchat <- computeCommunProb(cellchat)\ncellchat <- computeCommunProbPathway(cellchat)",
            inputs=["表达矩阵", "细胞类型注释"],
            outputs=["配体-受体互作表", "通讯网络图", "通路层面通讯强度"],
            cautions=[
                "细胞类型注释质量决定通讯结果可信度。",
                "通讯预测不代表真实物理接触，需要空间或实验验证。",
                "不同物种要选择对应配体受体数据库。",
            ],
            x_axis=["10 cell types", "30 cell types", "60 cell types"],
            time_data=[5, 18, 55],
            memory_data=[4, 12, 28],
            environment="R 4.4 / CellChatDB human",
            language="r",
        ),
        build_algorithm(
            name="scVelo",
            category="RNA Velocity",
            category_key="single-cell",
            category_name="单细胞分析",
            summary="基于 spliced/unspliced reads 的 RNA velocity 工具，用于推断细胞状态变化方向。",
            positioning="scVelo 适合单细胞高级下游分析，帮助理解细胞在状态空间中的潜在转变方向。",
            core_idea="使用剪接和未剪接转录本比例拟合动态模型，估计每个细胞的表达变化速度向量。",
            command="import scvelo as scv\nadata = scv.read('sample.loom')\nscv.pp.filter_and_normalize(adata)\nscv.pp.moments(adata)\nscv.tl.velocity(adata, mode='dynamical')\nscv.tl.velocity_graph(adata)\nscv.pl.velocity_embedding_stream(adata, basis='umap')",
            inputs=["loom/h5ad with spliced and unspliced layers"],
            outputs=["velocity graph", "velocity stream plot", "latent time"],
            cautions=[
                "需要上游正确生成 spliced/unspliced 矩阵。",
                "velocity 方向受数据质量、细胞状态连续性和模型假设影响很大。",
                "最好与拟时序、marker 和实验时间点一起解释。",
            ],
            x_axis=["10k cells", "50k cells", "100k cells"],
            time_data=[12, 58, 140],
            memory_data=[8, 28, 62],
            environment="Python 3.11 / scVelo dynamical mode",
            language="python",
        ),
        build_algorithm(
            name="GATK HaplotypeCaller",
            category="Variant Calling",
            category_key="variant-calling",
            category_name="变异检测",
            summary="GATK 体系中用于 germline SNV/Indel 检测的核心工具，常见于 WGS/WES 流程。",
            positioning="HaplotypeCaller 是标准 germline variant calling 的核心模块，适合单样本或 GVCF 联合分析流程。",
            core_idea="在活跃区域局部重组装 haplotype，再对 reads 与候选 haplotype 进行概率建模并输出变异。",
            command="gatk HaplotypeCaller -R GRCh38.fa -I sample.bam -O sample.g.vcf.gz -ERC GVCF\ngatk GenotypeGVCFs -R GRCh38.fa -V cohort.g.vcf.gz -O cohort.vcf.gz",
            inputs=["BQSR 后 BAM", "参考基因组 FASTA"],
            outputs=["GVCF", "cohort VCF"],
            cautions=[
                "GATK 参考资源、known-sites 和基因组版本必须一致。",
                "队列项目建议使用 GVCF joint genotyping。",
                "硬过滤或 VQSR 阈值要按项目规模和物种资源选择。",
            ],
            x_axis=["30x WGS", "100 exomes", "500 exomes"],
            time_data=[210, 780, 3600],
            memory_data=[12, 32, 96],
            environment="GATK 4 / 32 threads / GRCh38 resource bundle",
        ),
        build_algorithm(
            name="MACS2",
            category="Peak Calling",
            category_key="epigenomics",
            category_name="表观组学分析",
            summary="ChIP-seq/CUT&Tag/CUT&RUN 常用 peak calling 工具，用于定位蛋白-DNA 结合或组蛋白修饰区域。",
            positioning="MACS2 常用于从免疫沉淀类测序数据中识别 enriched regions，是表观组学流程中的关键节点。",
            core_idea="通过动态背景模型估计 reads 富集显著性，并输出 narrowPeak 或 broadPeak。",
            command="macs2 callpeak -t sample.bam -c input.bam -f BAMPE -g hs -n sample_H3K27ac --outdir peaks -q 0.01",
            inputs=["去重 BAM", "input/control BAM"],
            outputs=["narrowPeak/broadPeak", "summits", "peak annotation 输入"],
            cautions=[
                "转录因子通常使用 narrow peak，组蛋白修饰可能需要 broad peak 模式。",
                "CUT&Tag 数据是否提供 input/control 要结合实验方案判断。",
                "peak 数量异常通常提示抗体、测序深度或去重策略问题。",
            ],
            x_axis=["10M reads", "50M reads", "100M reads"],
            time_data=[3, 14, 31],
            memory_data=[1.2, 3.1, 6.4],
            environment="MACS2 / BAMPE / human genome size",
        ),
        build_algorithm(
            name="clusterProfiler",
            category="Enrichment",
            category_key="enrichment-network",
            category_name="富集与网络分析",
            summary="R 生态常用功能富集分析工具，支持 GO、KEGG、GSEA 和多种可视化。",
            positioning="clusterProfiler 适合 DEG、WGCNA 模块基因、marker gene 等列表的功能解释。",
            core_idea="将基因列表映射到功能数据库，通过超几何检验或排序统计评估通路富集。",
            command="library(clusterProfiler)\nlibrary(org.Hs.eg.db)\nego <- enrichGO(gene = genes, OrgDb = org.Hs.eg.db, keyType = 'ENTREZID', ont = 'BP')\ndotplot(ego)\ngsea <- gseKEGG(geneList = ranked_gene_list, organism = 'hsa')",
            inputs=["gene list", "ranked gene list", "ID mapping table"],
            outputs=["GO/KEGG 富集表", "dotplot", "GSEA 曲线"],
            cautions=[
                "基因 ID 类型转换是最常见错误来源。",
                "背景基因集应与实验可检测基因范围一致。",
                "富集结果需要合并相似 term，避免重复解释。",
            ],
            x_axis=["200 genes", "2000 genes", "ranked 20k genes"],
            time_data=[0.5, 1.8, 8.5],
            memory_data=[1, 2, 4],
            environment="R 4.4 / org.Hs.eg.db / KEGG online cache",
            language="r",
        ),
        build_algorithm(
            name="WGCNA",
            category="Network Analysis",
            category_key="enrichment-network",
            category_name="富集与网络分析",
            summary="加权基因共表达网络分析工具，用于识别模块、hub genes 和表型相关表达结构。",
            positioning="WGCNA 适合多样本表达矩阵，常用于寻找与性状、时间、疾病严重度相关的共表达模块。",
            core_idea="根据基因表达相关性构建加权网络，进行拓扑重叠计算和模块切分，再关联外部表型。",
            command="library(WGCNA)\ndatExpr <- t(vst_counts)\npowers <- pickSoftThreshold(datExpr)\nnet <- blockwiseModules(datExpr, power = 8, TOMType = 'signed', minModuleSize = 30)\nmoduleTraitCor <- cor(net$MEs, traits, use = 'p')",
            inputs=["标准化表达矩阵", "样本表型表"],
            outputs=["共表达模块", "module-trait correlation", "hub genes"],
            cautions=[
                "样本数太少会导致网络不稳定，通常建议至少 15-20 个样本。",
                "输入表达矩阵要先过滤低表达和低变异基因。",
                "hub gene 需要结合模块相关性、连接度和生物学证据筛选。",
            ],
            x_axis=["5k genes", "15k genes", "30k genes"],
            time_data=[6, 38, 160],
            memory_data=[4, 18, 72],
            environment="R 4.4 / signed network / blockwiseModules",
            language="r",
        ),
    ]


def seed_algorithms(db: Session) -> None:
    # Algorithm Gallery 按 name 做稳定 upsert，方便重复执行 init_db.py 刷新分类、文档和 benchmark。
    for item in build_mock_algorithms():
        item["metadata_json"] = item.get("metadata_json") or infer_algorithm_metadata(item)
        algorithm = db.scalar(select(Algorithm).where(Algorithm.name == item["name"]))
        if algorithm is None:
            db.add(Algorithm(**item))
            continue

        algorithm.category = item["category"]
        algorithm.category_key = item["category_key"]
        algorithm.category_name = item["category_name"]
        algorithm.tool_type = item["tool_type"]
        algorithm.summary = item["summary"]
        algorithm.performance_json = item["performance_json"]
        algorithm.metadata_json = item["metadata_json"]
        algorithm.markdown_docs = item["markdown_docs"]

    db.commit()
