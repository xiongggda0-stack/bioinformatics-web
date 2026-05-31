export interface DatabaseResource {
  id: string;
  name: string;
  fullName: string;
  categoryKey: string;
  categoryName: string;
  description: string;
  useCases: string[];
  dataTypes: string[];
  species: string[];
  tags: string[];
  url: string;
  downloadUrl?: string;
  apiUrl?: string;
  tutorials?: DatabaseTutorial[];
  region: string;
  rating: 1 | 2 | 3 | 4 | 5;
}

export interface DatabaseTutorial {
  id: string;
  title: string;
  scenario: string;
  steps: string[];
  exampleQuery?: string;
  entryUrl: string;
  content: string;
}

export const databaseCategories = [
  { key: "portal", name: "综合门户", description: "跨数据库检索、序列、文献、基因和蛋白的一站式入口。" },
  { key: "literature", name: "文献与知识", description: "检索论文、PMID、方法证据和综述。" },
  { key: "genome", name: "基因组与注释", description: "参考基因组、基因结构、坐标、同源基因和浏览器。" },
  { key: "raw-sequence", name: "原始测序数据", description: "下载 SRA/ENA/DRA 等 FASTQ 和原始测序项目。" },
  { key: "expression", name: "转录组表达", description: "公共表达矩阵、芯片、RNA-seq 和功能基因组数据。" },
  { key: "single-cell", name: "单细胞与空间组学", description: "单细胞图谱、空间转录组和细胞级表达数据。" },
  { key: "variant", name: "变异与临床注释", description: "SNP、群体频率、致病性、GWAS 和临床变异解释。" },
  { key: "cancer", name: "肿瘤组学", description: "癌症突变、表达、拷贝数、临床和队列数据。" },
  { key: "protein", name: "蛋白与结构", description: "蛋白功能、结构预测、蛋白表达和组织定位。" },
  { key: "pathway", name: "通路与功能富集", description: "GO、KEGG、Reactome、网络互作和基因集解释。" },
  { key: "model-organism", name: "模式生物与植物", description: "小鼠、果蝇、线虫、斑马鱼、拟南芥和作物数据库。" },
  { key: "microbiome", name: "微生物与宏基因组", description: "微生物分类、16S、宏基因组和微生物参考基因组。" }
] as const;

export const databaseResources: DatabaseResource[] = [
  {
    id: "ncbi",
    name: "NCBI",
    fullName: "National Center for Biotechnology Information",
    categoryKey: "portal",
    categoryName: "综合门户",
    description: "全球最常用的生物信息综合入口，覆盖文献、序列、基因、基因组、变异和表达数据。",
    useCases: ["查基因", "查序列", "查文献", "下载公共数据"],
    dataTypes: ["Sequence", "Genome", "Gene", "Literature"],
    species: ["Human", "Mouse", "Plant", "Microbe"],
    tags: ["Public Data", "API", "Download"],
    url: "https://www.ncbi.nlm.nih.gov/",
    apiUrl: "https://www.ncbi.nlm.nih.gov/books/NBK25501/",
    region: "USA",
    rating: 5
  },
  {
    id: "embl-ebi",
    name: "EMBL-EBI",
    fullName: "European Molecular Biology Laboratory - European Bioinformatics Institute",
    categoryKey: "portal",
    categoryName: "综合门户",
    description: "欧洲核心生物数据平台，整合基因组、蛋白、结构、表达、通路和化学信息资源。",
    useCases: ["跨库检索", "下载表达数据", "查蛋白结构", "查通路"],
    dataTypes: ["Genome", "Expression", "Protein", "Pathway"],
    species: ["Human", "Mouse", "Plant", "Microbe"],
    tags: ["Public Data", "API", "Download"],
    url: "https://www.ebi.ac.uk/",
    apiUrl: "https://www.ebi.ac.uk/ebisearch/documentation.ebi",
    region: "Europe",
    rating: 5
  },
  {
    id: "ddbj",
    name: "DDBJ",
    fullName: "DNA Data Bank of Japan",
    categoryKey: "portal",
    categoryName: "综合门户",
    description: "日本 DNA 数据库，与 NCBI 和 ENA 共同组成国际核酸序列数据库合作体系。",
    useCases: ["提交序列", "检索核酸数据", "下载 DRA 数据"],
    dataTypes: ["Sequence", "Raw Reads", "Genome"],
    species: ["Human", "Plant", "Microbe"],
    tags: ["Public Data", "Download"],
    url: "https://www.ddbj.nig.ac.jp/",
    region: "Japan",
    rating: 4
  },
  {
    id: "pubmed",
    name: "PubMed",
    fullName: "PubMed Literature Database",
    categoryKey: "literature",
    categoryName: "文献与知识",
    description: "生命科学和医学文献检索首选入口，适合查方法论文、PMID 和研究证据。",
    useCases: ["查论文", "查方法出处", "找综述"],
    dataTypes: ["Literature", "PMID"],
    species: ["All"],
    tags: ["Literature", "Evidence"],
    url: "https://pubmed.ncbi.nlm.nih.gov/",
    apiUrl: "https://www.ncbi.nlm.nih.gov/books/NBK25501/",
    region: "USA",
    rating: 5
  },
  {
    id: "europe-pmc",
    name: "Europe PMC",
    fullName: "Europe PubMed Central",
    categoryKey: "literature",
    categoryName: "文献与知识",
    description: "开放文献平台，适合检索全文、预印本、基金信息和文献引用网络。",
    useCases: ["查开放全文", "查预印本", "追踪引用"],
    dataTypes: ["Literature", "Full Text"],
    species: ["All"],
    tags: ["Open Access", "API"],
    url: "https://europepmc.org/",
    apiUrl: "https://europepmc.org/RestfulWebService",
    region: "Europe",
    rating: 4
  },
  {
    id: "ensembl",
    name: "Ensembl",
    fullName: "Ensembl Genome Browser",
    categoryKey: "genome",
    categoryName: "基因组与注释",
    description: "常用脊椎动物基因组浏览器，提供基因结构、转录本、坐标、同源基因和 BioMart 下载。",
    useCases: ["查基因坐标", "下载 GTF", "查同源基因", "ID 转换"],
    dataTypes: ["Genome", "Gene Annotation", "GTF"],
    species: ["Human", "Mouse", "Vertebrates"],
    tags: ["Genome Browser", "BioMart", "Download"],
    url: "https://www.ensembl.org/",
    downloadUrl: "https://ftp.ensembl.org/pub/",
    apiUrl: "https://rest.ensembl.org/",
    tutorials: [
      {
        id: "ensembl-gtf-download",
        title: "下载参考基因组与 GTF",
        scenario: "构建 STAR/HISAT2 索引或做 featureCounts 计数前，先统一 genome FASTA 与 GTF 注释版本。",
        steps: [
          "进入 Ensembl FTP，选择物种目录和 release 版本。",
          "从 fasta 目录下载 genome FASTA，从 gtf 目录下载对应 GTF。",
          "记录 release 号，并在流程文档中固定该版本。"
        ],
        exampleQuery: "Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz + Homo_sapiens.GRCh38.*.gtf.gz",
        entryUrl: "https://ftp.ensembl.org/pub/",
        content: `# 下载 Ensembl 参考基因组与 GTF

## 适用场景
当你要构建 STAR/HISAT2 索引、运行 featureCounts、做基因坐标注释或统一 RNA-seq 项目的参考版本时，需要同时下载同一 release 的 genome FASTA 和 GTF。

## 准备目录
\`\`\`bash
mkdir -p reference/ensembl_GRCh38
cd reference/ensembl_GRCh38
\`\`\`

## 操作步骤
1. 进入 Ensembl FTP：\`https://ftp.ensembl.org/pub/\`。
2. 选择固定 release，例如 \`release-112\`。
3. 在 \`fasta/homo_sapiens/dna/\` 下载 primary assembly FASTA。
4. 在 \`gtf/homo_sapiens/\` 下载同一 release 的 GTF。
5. 解压后记录 release、物种、assembly 名称。

## 示例命令
\`\`\`bash
wget https://ftp.ensembl.org/pub/release-112/fasta/homo_sapiens/dna/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz
wget https://ftp.ensembl.org/pub/release-112/gtf/homo_sapiens/Homo_sapiens.GRCh38.112.gtf.gz

gunzip *.gz
\`\`\`

## 结果检查
\`\`\`bash
grep -c '^>' Homo_sapiens.GRCh38.dna.primary_assembly.fa
head Homo_sapiens.GRCh38.112.gtf
\`\`\`

## 常见问题
| 问题 | 原因 | 解决 |
| --- | --- | --- |
| STAR 建索引后 featureCounts 计数很低 | FASTA 和 GTF 版本不一致 | 使用同一 Ensembl release |
| 染色体命名不一致 | \`1\` 与 \`chr1\` 混用 | 全流程统一 Ensembl 或 UCSC 命名 |
| 下载文件太多 | 选错目录 | FASTA 只选 primary_assembly 或 toplevel 之一 |
`
      },
      {
        id: "ensembl-biomart-id-conversion",
        title: "用 BioMart 做 ID 转换",
        scenario: "把 Ensembl gene ID 转换为 gene symbol、Entrez ID 或描述信息。",
        steps: [
          "进入 Ensembl BioMart，选择 Ensembl Genes 数据集。",
          "选择目标物种，并上传或粘贴 gene ID 列表。",
          "在 Attributes 中勾选 Gene stable ID、Gene name 和 Description 后导出。"
        ],
        exampleQuery: "ENSG00000141510 -> TP53",
        entryUrl: "https://www.ensembl.org/biomart/martview",
        content: `# 用 Ensembl BioMart 做 ID 转换

## 适用场景
当你的表达矩阵是 Ensembl gene ID，但下游富集、作图或报告需要 gene symbol、Entrez ID、描述信息时，可以用 BioMart 批量转换。

## 操作步骤
1. 打开 Ensembl BioMart。
2. Database 选择 \`Ensembl Genes\`。
3. Dataset 选择目标物种，例如 \`Human genes\`。
4. Filters 中选择 \`Gene stable ID(s)\`，粘贴基因 ID。
5. Attributes 中选择 \`Gene stable ID\`、\`Gene name\`、\`NCBI gene ID\`、\`Gene description\`。
6. 导出 TSV 文件并与表达矩阵合并。

## 示例输入
\`\`\`text
ENSG00000141510
ENSG00000157764
ENSG00000012048
\`\`\`

## R 合并示例
\`\`\`r
expr <- read.csv("deg_results.csv")
anno <- read.delim("ensembl_biomart.tsv")
merged <- merge(expr, anno, by.x = "gene_id", by.y = "Gene.stable.ID", all.x = TRUE)
write.csv(merged, "deg_results_annotated.csv", row.names = FALSE)
\`\`\`

## 注意事项
- ID 转换必须匹配物种。
- Ensembl ID 带版本号时，如 \`ENSG00000141510.18\`，通常需要先去掉 \`.18\`。
- 多对一映射需要保留原始 ID，避免误合并。
`
      }
    ],
    region: "Europe",
    rating: 5
  },
  {
    id: "ucsc",
    name: "UCSC Genome Browser",
    fullName: "University of California Santa Cruz Genome Browser",
    categoryKey: "genome",
    categoryName: "基因组与注释",
    description: "经典基因组浏览器，适合查看基因坐标、peak、保守性、表观组和自定义 track。",
    useCases: ["看基因组区域", "上传自定义 track", "查保守性", "看 ENCODE track"],
    dataTypes: ["Genome Browser", "Tracks", "Annotation"],
    species: ["Human", "Mouse", "Model Organisms"],
    tags: ["Genome Browser", "Visualization", "Download"],
    url: "https://genome.ucsc.edu/",
    downloadUrl: "https://hgdownload.soe.ucsc.edu/",
    region: "USA",
    rating: 5
  },
  {
    id: "ncbi-genome",
    name: "NCBI Genome",
    fullName: "NCBI Genome Database",
    categoryKey: "genome",
    categoryName: "基因组与注释",
    description: "NCBI 参考基因组和组装信息入口，适合查物种 genome assembly 和下载 FASTA/GFF。",
    useCases: ["下载参考基因组", "查 assembly", "查物种基因组版本"],
    dataTypes: ["Genome", "Assembly", "FASTA", "GFF"],
    species: ["Human", "Plant", "Microbe", "Animal"],
    tags: ["Reference", "Download"],
    url: "https://www.ncbi.nlm.nih.gov/genome/",
    downloadUrl: "https://ftp.ncbi.nlm.nih.gov/genomes/",
    region: "USA",
    rating: 5
  },
  {
    id: "refseq",
    name: "RefSeq",
    fullName: "NCBI Reference Sequence Database",
    categoryKey: "genome",
    categoryName: "基因组与注释",
    description: "NCBI 人工维护参考序列集合，常用于基因、转录本、蛋白和参考注释。",
    useCases: ["查标准转录本", "查蛋白序列", "参考注释"],
    dataTypes: ["Transcript", "Protein", "Genome"],
    species: ["Human", "Mouse", "Microbe"],
    tags: ["Reference", "Curated"],
    url: "https://www.ncbi.nlm.nih.gov/refseq/",
    downloadUrl: "https://ftp.ncbi.nlm.nih.gov/refseq/",
    region: "USA",
    rating: 5
  },
  {
    id: "sra",
    name: "SRA",
    fullName: "Sequence Read Archive",
    categoryKey: "raw-sequence",
    categoryName: "原始测序数据",
    description: "NCBI 原始测序 reads 数据库，适合下载公开 FASTQ/SRA 用于复现或再分析。",
    useCases: ["下载 FASTQ", "复现论文数据", "批量公共数据挖掘"],
    dataTypes: ["Raw Reads", "FASTQ", "SRA"],
    species: ["Human", "Mouse", "Plant", "Microbe"],
    tags: ["Download", "Public Data"],
    url: "https://www.ncbi.nlm.nih.gov/sra",
    downloadUrl: "https://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?view=software",
    tutorials: [
      {
        id: "sra-fastq-download",
        title: "从 SRR 编号下载 FASTQ",
        scenario: "复现论文测序数据，或把公开 reads 接入自己的 RNA-seq / WGS 流程。",
        steps: [
          "在 SRA 页面检索 BioProject、GSE 或 SRR 编号。",
          "记录 SRR run accession，并使用 SRA Toolkit 下载。",
          "用 fasterq-dump 转换 FASTQ，再用 gzip 压缩并进入质控流程。"
        ],
        exampleQuery: "fasterq-dump SRRxxxxxxx --split-files -e 8",
        entryUrl: "https://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?view=software",
        content: `# 从 SRA 的 SRR 编号下载 FASTQ

## 适用场景
当论文或 GEO 页面只给出 SRR 编号时，可以用 SRA Toolkit 下载原始 reads，再接入 RNA-seq、WGS、BSA 或单细胞流程。

## 安装工具
\`\`\`bash
mamba create -n sra-tools -c bioconda -c conda-forge sra-tools pigz
conda activate sra-tools
fasterq-dump --version
\`\`\`

## 推荐目录
\`\`\`text
public_data_project/
├── 00_sra/
├── 01_fastq/
├── 02_logs/
└── metadata/
\`\`\`

## 单个样本下载
\`\`\`bash
mkdir -p 00_sra 01_fastq

prefetch SRRxxxxxxx --output-directory 00_sra
fasterq-dump 00_sra/SRRxxxxxxx/SRRxxxxxxx.sra \\
  --split-files \\
  -e 8 \\
  -O 01_fastq

pigz -p 8 01_fastq/SRRxxxxxxx_*.fastq
\`\`\`

## 批量下载模板
\`\`\`bash
cat metadata/srr_list.txt | while read srr
do
  prefetch "$srr" --output-directory 00_sra
  fasterq-dump "00_sra/$srr/$srr.sra" --split-files -e 8 -O 01_fastq
done

pigz -p 8 01_fastq/*.fastq
\`\`\`

## 结果检查
\`\`\`bash
ls -lh 01_fastq
fastqc 01_fastq/*.fastq.gz -o 02_logs
\`\`\`

## 常见问题
| 问题 | 原因 | 解决 |
| --- | --- | --- |
| 下载速度慢 | NCBI 网络距离或限速 | 优先尝试 ENA fastq_ftp |
| 磁盘爆满 | fasterq-dump 会产生临时文件 | 预留 FASTQ 体积 2-3 倍空间 |
| 单端/双端混乱 | 未检查 RunInfo | 先导出 RunInfo，确认 Layout |
`
      }
    ],
    region: "USA",
    rating: 5
  },
  {
    id: "ena",
    name: "ENA",
    fullName: "European Nucleotide Archive",
    categoryKey: "raw-sequence",
    categoryName: "原始测序数据",
    description: "欧洲核酸和原始测序数据仓库，下载 FASTQ 链接清晰，适合批量下载公共数据。",
    useCases: ["下载 FASTQ", "检索测序项目", "跨库获取原始数据"],
    dataTypes: ["Raw Reads", "FASTQ", "Sequence"],
    species: ["Human", "Mouse", "Plant", "Microbe"],
    tags: ["Download", "API", "Public Data"],
    url: "https://www.ebi.ac.uk/ena/browser/home",
    apiUrl: "https://www.ebi.ac.uk/ena/portal/api/",
    tutorials: [
      {
        id: "ena-fastq-ftp",
        title: "通过 ENA 获取 FASTQ 直链",
        scenario: "批量下载公开测序数据时，ENA 通常能直接提供 fastq_ftp 字段。",
        steps: [
          "进入 ENA Browser，输入 SRR/ERR/DRR 或 BioProject 编号。",
          "在 Run 信息中查看 FASTQ FTP 链接。",
          "使用 wget、aria2c 或脚本批量下载 fastq_ftp 文件。"
        ],
        exampleQuery: "fields=run_accession,fastq_ftp,fastq_md5",
        entryUrl: "https://www.ebi.ac.uk/ena/portal/api/",
        content: `# 通过 ENA 获取 FASTQ 直链

## 适用场景
当你已经知道 SRR/ERR/DRR 编号，想用 wget 或 aria2c 直接下载 FASTQ 时，ENA 的 \`fastq_ftp\` 字段很方便。

## 查询单个 Run
\`\`\`bash
wget -O ena_run.tsv "https://www.ebi.ac.uk/ena/portal/api/filereport?accession=SRRxxxxxxx&result=read_run&fields=run_accession,fastq_ftp,fastq_md5&format=tsv"
cat ena_run.tsv
\`\`\`

## 批量下载 FASTQ
\`\`\`bash
cut -f2 ena_run.tsv | tail -n +2 | tr ';' '\\n' | while read url
do
  wget -c "ftp://$url"
done
\`\`\`

## 推荐字段
| 字段 | 说明 |
| --- | --- |
| \`run_accession\` | SRR/ERR/DRR 编号 |
| \`sample_accession\` | 样本编号 |
| \`fastq_ftp\` | FASTQ FTP 下载链接 |
| \`fastq_md5\` | 文件校验值 |
| \`library_layout\` | SINGLE 或 PAIRED |

## 常见问题
- \`fastq_ftp\` 为空：部分数据未开放 FASTQ 直链，可退回 SRA Toolkit。
- 一个 run 有两个链接：通常表示双端测序 R1/R2。
- 下载后建议用 md5 校验文件完整性。
`
      }
    ],
    region: "Europe",
    rating: 5
  },
  {
    id: "geo",
    name: "GEO",
    fullName: "Gene Expression Omnibus",
    categoryKey: "expression",
    categoryName: "转录组表达",
    description: "NCBI 功能基因组数据仓库，收录 RNA-seq、芯片、甲基化、ChIP-seq 等项目。",
    useCases: ["找表达数据", "下载表达矩阵", "复现论文"],
    dataTypes: ["RNA-seq", "Microarray", "Expression Matrix"],
    species: ["Human", "Mouse", "Plant"],
    tags: ["Expression", "Public Data", "Download"],
    url: "https://www.ncbi.nlm.nih.gov/geo/",
    apiUrl: "https://www.ncbi.nlm.nih.gov/geo/info/geo_paccess.html",
    tutorials: [
      {
        id: "geo-expression-matrix",
        title: "下载 GEO 表达矩阵",
        scenario: "快速获取论文已整理好的表达矩阵，用于差异分析、WGCNA 或验证候选基因。",
        steps: [
          "用 GSE 编号进入 GEO Series 页面。",
          "查看 Supplementary files 是否包含表达矩阵或 count matrix。",
          "下载 matrix 后检查样本分组、探针注释和基因 ID 类型。"
        ],
        exampleQuery: "GSE + expression matrix + sample metadata",
        entryUrl: "https://www.ncbi.nlm.nih.gov/geo/",
        content: `# 下载 GEO 表达矩阵

## 适用场景
当你想快速复用公开表达数据做差异分析、WGCNA、免疫浸润或候选基因验证时，优先查看 GEO 是否提供整理好的表达矩阵。

## 操作步骤
1. 打开 GEO，输入 GSE 编号。
2. 在 Series 页面查看实验设计、样本分组和平台信息。
3. 找到 Supplementary files，下载 count matrix、TPM matrix 或 normalized matrix。
4. 下载 sample metadata，整理 group、batch、treatment 等字段。
5. 检查表达矩阵是 raw counts、TPM 还是芯片 normalized intensity。

## R 读取示例
\`\`\`r
expr <- read.delim("GSE_expression_matrix.tsv", row.names = 1, check.names = FALSE)
meta <- read.delim("GSE_sample_metadata.tsv")

dim(expr)
head(meta)
\`\`\`

## 判断能否用于 DESeq2
| 数据类型 | 能否直接用于 DESeq2 |
| --- | --- |
| raw counts | 可以 |
| TPM/FPKM | 不建议 |
| normalized microarray | 不可以，用 limma |

## 常见问题
- GEO 矩阵列名与样本表不一致时，先建立 GSM 到 sample name 的映射。
- 芯片数据需要探针注释，不要直接把 probe ID 当 gene symbol。
- 如果只有 SRA 链接，没有矩阵，需要走 SRA/ENA 下载 FASTQ 重新分析。
`
      },
      {
        id: "geo-to-sra-run-selector",
        title: "从 GEO 追踪到 SRA 原始数据",
        scenario: "当 GEO 只提供样本信息时，需要跳转 SRA 下载 FASTQ 重新分析。",
        steps: [
          "在 GEO 样本页面查找 SRA Run Selector 链接。",
          "导出 RunInfo 表，获得 SRR 编号和样本对应关系。",
          "按样本分组整理 metadata，再进入 SRA/ENA 下载。"
        ],
        exampleQuery: "GSE accession -> SRA Run Selector -> SRR list",
        entryUrl: "https://www.ncbi.nlm.nih.gov/Traces/study/",
        content: `# 从 GEO 追踪到 SRA 原始数据

## 适用场景
GEO 页面没有可直接使用的表达矩阵，或者你希望统一用自己的流程重新分析公开 RNA-seq、WGS、CUT&Tag 数据。

## 操作步骤
1. 进入 GEO Series 页面，找到 SRA Run Selector 链接。
2. 在 Run Selector 中下载 \`RunInfo.csv\`。
3. 提取 \`Run\`、\`SampleName\`、\`LibraryLayout\`、\`Platform\` 等字段。
4. 根据 SRR 编号用 SRA Toolkit 或 ENA 下载 FASTQ。
5. 建立 \`metadata.tsv\`，记录样本分组和 SRR 对应关系。

## 元数据整理示例
\`\`\`r
runinfo <- read.csv("SraRunInfo.csv")
metadata <- runinfo[, c("Run", "SampleName", "LibraryLayout", "Platform")]
write.table(metadata, "metadata.tsv", sep = "\\t", row.names = FALSE, quote = FALSE)
\`\`\`

## 下载衔接
\`\`\`bash
cut -f1 metadata/srr_list.txt | while read srr
do
  fasterq-dump "$srr" --split-files -e 8 -O fastq
done
\`\`\`

## 注意事项
- 一个 GSM 可能对应多个 SRR，需要合并同一样本的多个 lane。
- 先检查 LibraryLayout，避免单端数据误按双端流程跑。
- 公开数据再分析必须记录原始 accession，方便结果追溯。
`
      }
    ],
    region: "USA",
    rating: 5
  },
  {
    id: "arrayexpress",
    name: "ArrayExpress",
    fullName: "ArrayExpress Archive",
    categoryKey: "expression",
    categoryName: "转录组表达",
    description: "EMBL-EBI 表达实验归档库，包含芯片和测序表达项目。",
    useCases: ["检索表达实验", "下载补充矩阵", "查实验设计"],
    dataTypes: ["Expression", "Microarray", "RNA-seq"],
    species: ["Human", "Mouse", "Plant"],
    tags: ["Expression", "Archive"],
    url: "https://www.ebi.ac.uk/biostudies/arrayexpress",
    region: "Europe",
    rating: 4
  },
  {
    id: "expression-atlas",
    name: "Expression Atlas",
    fullName: "EMBL-EBI Expression Atlas",
    categoryKey: "expression",
    categoryName: "转录组表达",
    description: "提供跨组织、物种、条件的基因表达查询，适合快速查看基因表达模式。",
    useCases: ["查基因表达", "看组织特异性", "表达模式探索"],
    dataTypes: ["Expression", "Baseline", "Differential"],
    species: ["Human", "Mouse", "Plant"],
    tags: ["Expression", "Visualization"],
    url: "https://www.ebi.ac.uk/gxa/home",
    region: "Europe",
    rating: 4
  },
  {
    id: "hca",
    name: "Human Cell Atlas",
    fullName: "Human Cell Atlas Data Portal",
    categoryKey: "single-cell",
    categoryName: "单细胞与空间组学",
    description: "人类细胞图谱数据入口，适合寻找组织级单细胞参考数据和细胞类型图谱。",
    useCases: ["查人类单细胞图谱", "找参考数据", "细胞类型注释参考"],
    dataTypes: ["scRNA-seq", "Spatial", "Cell Atlas"],
    species: ["Human"],
    tags: ["Single-cell", "Atlas", "Download"],
    url: "https://data.humancellatlas.org/",
    region: "Global",
    rating: 5
  },
  {
    id: "cellxgene",
    name: "CELLxGENE",
    fullName: "CZ CELLxGENE Discover",
    categoryKey: "single-cell",
    categoryName: "单细胞与空间组学",
    description: "交互式单细胞数据浏览和下载平台，适合查看公开 h5ad 数据和细胞注释。",
    useCases: ["浏览单细胞数据", "下载 h5ad", "比较细胞类型"],
    dataTypes: ["scRNA-seq", "h5ad", "Cell Annotation"],
    species: ["Human", "Mouse"],
    tags: ["Single-cell", "Visualization", "Download"],
    url: "https://cellxgene.cziscience.com/",
    apiUrl: "https://chanzuckerberg.github.io/cellxgene-census/",
    region: "USA",
    rating: 5
  },
  {
    id: "single-cell-portal",
    name: "Single Cell Portal",
    fullName: "Broad Institute Single Cell Portal",
    categoryKey: "single-cell",
    categoryName: "单细胞与空间组学",
    description: "Broad Institute 单细胞研究数据平台，适合查找研究项目、marker 和可视化结果。",
    useCases: ["查单细胞研究", "看 marker", "下载数据"],
    dataTypes: ["scRNA-seq", "Metadata", "Visualization"],
    species: ["Human", "Mouse"],
    tags: ["Single-cell", "Visualization"],
    url: "https://singlecell.broadinstitute.org/single_cell",
    region: "USA",
    rating: 4
  },
  {
    id: "10x-datasets",
    name: "10x Datasets",
    fullName: "10x Genomics Public Datasets",
    categoryKey: "single-cell",
    categoryName: "单细胞与空间组学",
    description: "10x 官方示例数据集合，适合学习 Cell Ranger、Seurat、Scanpy 和 Visium 流程。",
    useCases: ["下载示例数据", "练习单细胞流程", "测试软件参数"],
    dataTypes: ["scRNA-seq", "Visium", "Multiome"],
    species: ["Human", "Mouse"],
    tags: ["Tutorial Data", "Download"],
    url: "https://www.10xgenomics.com/datasets",
    region: "USA",
    rating: 5
  },
  {
    id: "hubmap",
    name: "HuBMAP",
    fullName: "Human BioMolecular Atlas Program",
    categoryKey: "single-cell",
    categoryName: "单细胞与空间组学",
    description: "人体组织空间和单细胞多组学图谱项目，适合空间组学和组织定位参考。",
    useCases: ["查空间组学数据", "组织图谱", "多组学参考"],
    dataTypes: ["Spatial", "Single-cell", "Proteomics"],
    species: ["Human"],
    tags: ["Atlas", "Spatial", "Download"],
    url: "https://portal.hubmapconsortium.org/",
    region: "USA",
    rating: 4
  },
  {
    id: "clinvar",
    name: "ClinVar",
    fullName: "ClinVar",
    categoryKey: "variant",
    categoryName: "变异与临床注释",
    description: "临床变异解释数据库，提供变异与疾病、致病性和证据提交记录。",
    useCases: ["查变异致病性", "临床注释", "遗传病解释"],
    dataTypes: ["Variant", "Clinical Significance"],
    species: ["Human"],
    tags: ["Clinical", "Variant", "Download"],
    url: "https://www.ncbi.nlm.nih.gov/clinvar/",
    downloadUrl: "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/",
    region: "USA",
    rating: 5
  },
  {
    id: "gnomad",
    name: "gnomAD",
    fullName: "Genome Aggregation Database",
    categoryKey: "variant",
    categoryName: "变异与临床注释",
    description: "大规模人群变异频率数据库，适合过滤常见变异和解释稀有变异。",
    useCases: ["查人群频率", "过滤常见变异", "稀有病分析"],
    dataTypes: ["Variant", "Allele Frequency", "VCF"],
    species: ["Human"],
    tags: ["Population", "Variant", "Download"],
    url: "https://gnomad.broadinstitute.org/",
    downloadUrl: "https://gnomad.broadinstitute.org/downloads",
    region: "USA",
    rating: 5
  },
  {
    id: "dbsnp",
    name: "dbSNP",
    fullName: "Database of Single Nucleotide Polymorphisms",
    categoryKey: "variant",
    categoryName: "变异与临床注释",
    description: "NCBI SNP 和小变异数据库，适合查询 rsID、变异坐标和基础注释。",
    useCases: ["查 rsID", "变异坐标转换", "基础 SNP 注释"],
    dataTypes: ["SNP", "Variant", "rsID"],
    species: ["Human", "Mouse", "Plant"],
    tags: ["Variant", "Reference"],
    url: "https://www.ncbi.nlm.nih.gov/snp/",
    region: "USA",
    rating: 4
  },
  {
    id: "1000genomes",
    name: "1000 Genomes",
    fullName: "1000 Genomes Project",
    categoryKey: "variant",
    categoryName: "变异与临床注释",
    description: "经典人群基因组项目，提供不同人群的公开变异数据。",
    useCases: ["查人群变异", "下载 VCF", "方法测试"],
    dataTypes: ["WGS", "Variant", "VCF"],
    species: ["Human"],
    tags: ["Population", "Download"],
    url: "https://www.internationalgenome.org/",
    downloadUrl: "https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/",
    region: "Global",
    rating: 4
  },
  {
    id: "gwas-catalog",
    name: "GWAS Catalog",
    fullName: "NHGRI-EBI GWAS Catalog",
    categoryKey: "variant",
    categoryName: "变异与临床注释",
    description: "GWAS 研究和性状关联变异数据库，适合查 SNP 与疾病/性状关联。",
    useCases: ["查性状关联", "候选位点解释", "遗传关联证据"],
    dataTypes: ["GWAS", "Variant", "Trait"],
    species: ["Human"],
    tags: ["GWAS", "Trait", "API"],
    url: "https://www.ebi.ac.uk/gwas/",
    apiUrl: "https://www.ebi.ac.uk/gwas/rest/docs/api",
    region: "Europe",
    rating: 5
  },
  {
    id: "gdc",
    name: "GDC / TCGA",
    fullName: "Genomic Data Commons",
    categoryKey: "cancer",
    categoryName: "肿瘤组学",
    description: "NCI 癌症组学数据门户，整合 TCGA 等项目的表达、突变、CNV 和临床数据。",
    useCases: ["下载 TCGA", "肿瘤表达分析", "突变和临床关联"],
    dataTypes: ["Cancer", "RNA-seq", "Mutation", "Clinical"],
    species: ["Human"],
    tags: ["Cancer", "TCGA", "Download", "API"],
    url: "https://portal.gdc.cancer.gov/",
    apiUrl: "https://docs.gdc.cancer.gov/API/Users_Guide/Getting_Started/",
    tutorials: [
      {
        id: "gdc-tcga-expression",
        title: "下载 TCGA 表达矩阵",
        scenario: "做肿瘤差异表达、生存分析或免疫浸润分析前，获取 TCGA RNA-seq 数据。",
        steps: [
          "进入 GDC Portal，选择 Program = TCGA 和目标癌种项目。",
          "在 Data Category 中选择 Transcriptome Profiling。",
          "选择 HTSeq Counts 或 STAR Counts 后加入 Cart，并下载 manifest。"
        ],
        exampleQuery: "TCGA-LUAD + Transcriptome Profiling + STAR Counts",
        entryUrl: "https://portal.gdc.cancer.gov/repository",
        content: `# 下载 TCGA 表达矩阵

## 适用场景
当你要做肿瘤差异表达、生存分析、分型比较、免疫浸润或候选基因验证时，可以从 GDC 下载 TCGA RNA-seq 数据。

## Portal 操作步骤
1. 打开 GDC Repository。
2. Program 选择 \`TCGA\`。
3. Project 选择癌种，例如 \`TCGA-LUAD\`。
4. Data Category 选择 \`Transcriptome Profiling\`。
5. Data Type 选择 \`Gene Expression Quantification\`。
6. Workflow Type 选择 \`STAR - Counts\`。
7. Add to Cart，下载 Manifest。

## GDC Client 下载
\`\`\`bash
gdc-client download -m gdc_manifest.txt -d gdc_download
\`\`\`

## 下游整理思路
1. 合并每个样本的 gene count 文件。
2. 区分 primary tumor 和 solid tissue normal。
3. 用 DESeq2 或 edgeR 做差异分析。
4. 结合临床表做生存或分期关联。

## 注意事项
- TCGA barcode 前 12 位代表 patient，前 16 位区分样本类型。
- Tumor/Normal 比较必须检查样本类型代码。
- 不同 GDC workflow 版本不要混用。
`
      },
      {
        id: "gdc-tcga-maf-clinical",
        title: "获取突变 MAF 与临床信息",
        scenario: "分析癌症突变谱、驱动基因或突变与生存/分型的关系。",
        steps: [
          "在 Repository 里选择 Simple Nucleotide Variation。",
          "下载 Masked Somatic Mutation MAF 文件。",
          "同步下载 Clinical Supplement 或通过 GDC API 获取病例信息。"
        ],
        exampleQuery: "TCGA-BRCA + Masked Somatic Mutation + Clinical",
        entryUrl: "https://portal.gdc.cancer.gov/repository",
        content: `# 获取 TCGA 突变 MAF 与临床信息

## 适用场景
用于分析癌症突变谱、驱动基因、TMB、突变与表达/生存/分型之间的关系。

## MAF 下载步骤
1. 打开 GDC Repository。
2. Program 选择 \`TCGA\`，Project 选择目标癌种。
3. Data Category 选择 \`Simple Nucleotide Variation\`。
4. Data Type 选择 \`Masked Somatic Mutation\`。
5. 下载 MAF 文件和 manifest。

## 临床信息
可以在 GDC Portal 的 Clinical 或 Case 页面下载，也可以通过 API 获取病例、生存、分期等字段。

## R 读取示例
\`\`\`r
library(data.table)
maf <- fread("tcga.maf.gz", skip = "Hugo_Symbol")
table(maf$Variant_Classification)
\`\`\`

## 常见分析
- 高频突变基因统计。
- TMB 计算。
- 突变型 vs 野生型表达差异。
- 突变状态与总生存期关联。

## 注意事项
- MAF 中样本 barcode 要和表达矩阵 barcode 统一截取规则。
- 临床字段缺失较常见，需要做缺失值统计。
- TMB 计算要明确外显子区域大小和过滤规则。
`
      }
    ],
    region: "USA",
    rating: 5
  },
  {
    id: "cbioportal",
    name: "cBioPortal",
    fullName: "cBioPortal for Cancer Genomics",
    categoryKey: "cancer",
    categoryName: "肿瘤组学",
    description: "癌症多组学可视化和探索平台，适合快速查看突变、表达、CNV 和生存关联。",
    useCases: ["癌症基因查询", "突变频率", "生存分析", "队列探索"],
    dataTypes: ["Cancer", "Mutation", "CNV", "Expression"],
    species: ["Human"],
    tags: ["Cancer", "Visualization", "API"],
    url: "https://www.cbioportal.org/",
    apiUrl: "https://www.cbioportal.org/api/swagger-ui/",
    region: "USA",
    rating: 5
  },
  {
    id: "icgc",
    name: "ICGC",
    fullName: "International Cancer Genome Consortium",
    categoryKey: "cancer",
    categoryName: "肿瘤组学",
    description: "国际癌症基因组联盟数据资源，适合跨癌种、跨项目查找癌症组学数据。",
    useCases: ["查癌症队列", "跨项目比较", "癌症变异"],
    dataTypes: ["Cancer", "WGS", "Mutation"],
    species: ["Human"],
    tags: ["Cancer", "Cohort"],
    url: "https://dcc.icgc.org/",
    region: "Global",
    rating: 4
  },
  {
    id: "uniprot",
    name: "UniProt",
    fullName: "Universal Protein Resource",
    categoryKey: "protein",
    categoryName: "蛋白与结构",
    description: "蛋白序列、功能、结构域、GO 注释和交叉引用的核心数据库。",
    useCases: ["查蛋白功能", "查结构域", "ID 转换", "下载蛋白序列"],
    dataTypes: ["Protein", "Function", "FASTA"],
    species: ["Human", "Mouse", "Plant", "Microbe"],
    tags: ["Protein", "Curated", "API"],
    url: "https://www.uniprot.org/",
    apiUrl: "https://www.uniprot.org/help/api",
    region: "Europe",
    rating: 5
  },
  {
    id: "pdb",
    name: "PDB",
    fullName: "Protein Data Bank",
    categoryKey: "protein",
    categoryName: "蛋白与结构",
    description: "实验解析蛋白和核酸三维结构数据库，适合结构生物学和功能解释。",
    useCases: ["查蛋白结构", "下载 PDB", "结构功能解释"],
    dataTypes: ["Protein Structure", "PDB"],
    species: ["All"],
    tags: ["Structure", "Download", "API"],
    url: "https://www.rcsb.org/",
    apiUrl: "https://data.rcsb.org/",
    region: "USA",
    rating: 5
  },
  {
    id: "alphafold",
    name: "AlphaFold DB",
    fullName: "AlphaFold Protein Structure Database",
    categoryKey: "protein",
    categoryName: "蛋白与结构",
    description: "大规模蛋白结构预测数据库，适合没有实验结构时快速查看结构预测。",
    useCases: ["查预测结构", "下载 PDB/mmCIF", "结构域判断"],
    dataTypes: ["Predicted Structure", "Protein"],
    species: ["Human", "Mouse", "Plant", "Microbe"],
    tags: ["Structure", "AI", "Download"],
    url: "https://alphafold.ebi.ac.uk/",
    apiUrl: "https://alphafold.ebi.ac.uk/api-docs",
    region: "Europe",
    rating: 5
  },
  {
    id: "hpa",
    name: "Human Protein Atlas",
    fullName: "Human Protein Atlas",
    categoryKey: "protein",
    categoryName: "蛋白与结构",
    description: "人类蛋白表达、组织定位、细胞定位和病理表达数据库。",
    useCases: ["查组织表达", "查细胞定位", "肿瘤蛋白表达"],
    dataTypes: ["Protein Expression", "Tissue", "Pathology"],
    species: ["Human"],
    tags: ["Protein", "Expression", "Visualization"],
    url: "https://www.proteinatlas.org/",
    downloadUrl: "https://www.proteinatlas.org/about/download",
    region: "Europe",
    rating: 5
  },
  {
    id: "go",
    name: "Gene Ontology",
    fullName: "Gene Ontology Resource",
    categoryKey: "pathway",
    categoryName: "通路与功能富集",
    description: "基因功能注释标准体系，覆盖生物过程、分子功能和细胞组分。",
    useCases: ["GO 富集", "功能注释", "基因集解释"],
    dataTypes: ["Ontology", "Annotation"],
    species: ["Human", "Mouse", "Plant", "Microbe"],
    tags: ["Enrichment", "Ontology"],
    url: "https://geneontology.org/",
    downloadUrl: "https://geneontology.org/docs/download-ontology/",
    region: "Global",
    rating: 5
  },
  {
    id: "kegg",
    name: "KEGG",
    fullName: "Kyoto Encyclopedia of Genes and Genomes",
    categoryKey: "pathway",
    categoryName: "通路与功能富集",
    description: "通路、代谢、疾病和药物知识库，常用于 KEGG pathway 富集分析。",
    useCases: ["KEGG 富集", "代谢通路", "通路图解释"],
    dataTypes: ["Pathway", "Gene Set", "Metabolism"],
    species: ["Human", "Mouse", "Plant", "Microbe"],
    tags: ["Pathway", "Enrichment"],
    url: "https://www.kegg.jp/",
    apiUrl: "https://www.kegg.jp/kegg/rest/keggapi.html",
    region: "Japan",
    rating: 5
  },
  {
    id: "reactome",
    name: "Reactome",
    fullName: "Reactome Pathway Database",
    categoryKey: "pathway",
    categoryName: "通路与功能富集",
    description: "人工审核通路数据库，适合人类和模式生物通路富集与机制解释。",
    useCases: ["通路富集", "机制解释", "通路层级浏览"],
    dataTypes: ["Pathway", "Reaction", "Gene Set"],
    species: ["Human", "Mouse", "Model Organisms"],
    tags: ["Pathway", "Curated", "API"],
    url: "https://reactome.org/",
    apiUrl: "https://reactome.org/dev/content-service",
    region: "Global",
    rating: 5
  },
  {
    id: "msigdb",
    name: "MSigDB",
    fullName: "Molecular Signatures Database",
    categoryKey: "pathway",
    categoryName: "通路与功能富集",
    description: "常用基因集数据库，适合 GSEA、GSVA、通路打分和功能解释。",
    useCases: ["GSEA", "GSVA", "通路打分", "基因集下载"],
    dataTypes: ["Gene Set", "Pathway"],
    species: ["Human", "Mouse"],
    tags: ["Gene Set", "GSEA"],
    url: "https://www.gsea-msigdb.org/gsea/msigdb/",
    region: "USA",
    rating: 5
  },
  {
    id: "string",
    name: "STRING",
    fullName: "STRING Protein Interaction Networks",
    categoryKey: "pathway",
    categoryName: "通路与功能富集",
    description: "蛋白互作网络数据库，适合候选基因网络分析和 hub gene 解释。",
    useCases: ["蛋白互作", "网络分析", "hub gene 解释"],
    dataTypes: ["PPI", "Network"],
    species: ["Human", "Mouse", "Plant", "Microbe"],
    tags: ["Network", "Protein", "API"],
    url: "https://string-db.org/",
    apiUrl: "https://string-db.org/help/api/",
    region: "Europe",
    rating: 5
  },
  {
    id: "tair",
    name: "TAIR",
    fullName: "The Arabidopsis Information Resource",
    categoryKey: "model-organism",
    categoryName: "模式生物与植物",
    description: "拟南芥核心数据库，适合植物基因功能、注释和突变体信息查询。",
    useCases: ["拟南芥基因", "植物注释", "突变体查询"],
    dataTypes: ["Gene", "Annotation", "Mutant"],
    species: ["Arabidopsis"],
    tags: ["Plant", "Model Organism"],
    url: "https://www.arabidopsis.org/",
    region: "USA",
    rating: 5
  },
  {
    id: "gramene",
    name: "Gramene",
    fullName: "Gramene Plant Genomics",
    categoryKey: "model-organism",
    categoryName: "模式生物与植物",
    description: "植物比较基因组数据库，适合作物基因组、同源基因和通路查询。",
    useCases: ["作物基因组", "植物同源基因", "比较基因组"],
    dataTypes: ["Plant Genome", "Gene", "Pathway"],
    species: ["Rice", "Maize", "Wheat", "Plant"],
    tags: ["Plant", "Genome"],
    url: "https://www.gramene.org/",
    region: "USA",
    rating: 4
  },
  {
    id: "mgi",
    name: "MGI",
    fullName: "Mouse Genome Informatics",
    categoryKey: "model-organism",
    categoryName: "模式生物与植物",
    description: "小鼠基因组和功能注释核心数据库，适合小鼠基因、表型和模型查询。",
    useCases: ["小鼠基因", "表型", "疾病模型"],
    dataTypes: ["Mouse Gene", "Phenotype", "Model"],
    species: ["Mouse"],
    tags: ["Mouse", "Model Organism"],
    url: "https://www.informatics.jax.org/",
    region: "USA",
    rating: 5
  },
  {
    id: "flybase",
    name: "FlyBase",
    fullName: "FlyBase",
    categoryKey: "model-organism",
    categoryName: "模式生物与植物",
    description: "果蝇遗传和基因组数据库，适合果蝇基因、突变和表型查询。",
    useCases: ["果蝇基因", "突变体", "表型"],
    dataTypes: ["Gene", "Genetics", "Phenotype"],
    species: ["Drosophila"],
    tags: ["Model Organism"],
    url: "https://flybase.org/",
    region: "Global",
    rating: 4
  },
  {
    id: "wormbase",
    name: "WormBase",
    fullName: "WormBase",
    categoryKey: "model-organism",
    categoryName: "模式生物与植物",
    description: "线虫基因组和遗传学数据库，适合 C. elegans 基因和功能查询。",
    useCases: ["线虫基因", "功能注释", "遗传学信息"],
    dataTypes: ["Gene", "Genome", "Phenotype"],
    species: ["C. elegans"],
    tags: ["Model Organism"],
    url: "https://wormbase.org/",
    region: "Global",
    rating: 4
  },
  {
    id: "zfin",
    name: "ZFIN",
    fullName: "Zebrafish Information Network",
    categoryKey: "model-organism",
    categoryName: "模式生物与植物",
    description: "斑马鱼模型生物数据库，适合基因、表达、突变体和表型查询。",
    useCases: ["斑马鱼基因", "表达模式", "突变体"],
    dataTypes: ["Gene", "Expression", "Phenotype"],
    species: ["Zebrafish"],
    tags: ["Model Organism"],
    url: "https://zfin.org/",
    region: "USA",
    rating: 4
  },
  {
    id: "gtdb",
    name: "GTDB",
    fullName: "Genome Taxonomy Database",
    categoryKey: "microbiome",
    categoryName: "微生物与宏基因组",
    description: "基于基因组的细菌和古菌分类数据库，适合宏基因组物种注释和系统发育。",
    useCases: ["微生物分类", "宏基因组注释", "系统发育"],
    dataTypes: ["Microbial Genome", "Taxonomy"],
    species: ["Bacteria", "Archaea"],
    tags: ["Microbiome", "Taxonomy"],
    url: "https://gtdb.ecogenomic.org/",
    region: "Australia",
    rating: 5
  },
  {
    id: "silva",
    name: "SILVA",
    fullName: "SILVA rRNA Database",
    categoryKey: "microbiome",
    categoryName: "微生物与宏基因组",
    description: "高质量 rRNA 序列数据库，常用于 16S/18S 扩增子分析的物种注释。",
    useCases: ["16S 注释", "rRNA 分类", "扩增子分析"],
    dataTypes: ["rRNA", "Taxonomy"],
    species: ["Bacteria", "Archaea", "Eukaryotes"],
    tags: ["16S", "Microbiome"],
    url: "https://www.arb-silva.de/",
    region: "Europe",
    rating: 5
  },
  {
    id: "mgnify",
    name: "MGnify",
    fullName: "EMBL-EBI MGnify",
    categoryKey: "microbiome",
    categoryName: "微生物与宏基因组",
    description: "宏基因组数据分析和归档平台，适合查环境样本、微生物群落和功能注释。",
    useCases: ["宏基因组项目", "环境微生物", "功能注释"],
    dataTypes: ["Metagenomics", "Amplicon", "Assembly"],
    species: ["Microbiome"],
    tags: ["Metagenomics", "API"],
    url: "https://www.ebi.ac.uk/metagenomics/",
    apiUrl: "https://www.ebi.ac.uk/metagenomics/api/v1/",
    region: "Europe",
    rating: 5
  },
  {
    id: "ncbi-taxonomy",
    name: "NCBI Taxonomy",
    fullName: "NCBI Taxonomy Database",
    categoryKey: "microbiome",
    categoryName: "微生物与宏基因组",
    description: "NCBI 物种分类体系入口，适合查询 taxid、物种层级和分类名称标准化。",
    useCases: ["查 taxid", "物种名称标准化", "分类层级"],
    dataTypes: ["Taxonomy", "Species"],
    species: ["All"],
    tags: ["Taxonomy", "Reference"],
    url: "https://www.ncbi.nlm.nih.gov/taxonomy",
    region: "USA",
    rating: 5
  }
];

export interface DatabaseTutorialDetail {
  resource: DatabaseResource;
  tutorial: DatabaseTutorial;
}

export function getAllDatabaseTutorials(): DatabaseTutorialDetail[] {
  return databaseResources.flatMap((resource) =>
    (resource.tutorials ?? []).map((tutorial) => ({ resource, tutorial }))
  );
}

export function getDatabaseTutorialById(
  tutorialId: string
): DatabaseTutorialDetail | null {
  return (
    getAllDatabaseTutorials().find(
      (item) => item.tutorial.id === tutorialId
    ) ?? null
  );
}
