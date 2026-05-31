from pydantic import BaseModel, ConfigDict


class RelatedPipeline(BaseModel):
    id: int
    title: str
    description: str
    omics_type: str

    model_config = ConfigDict(from_attributes=True)


class RelatedAlgorithm(BaseModel):
    id: int
    name: str
    category: str
    summary: str

    model_config = ConfigDict(from_attributes=True)


class RelatedLiterature(BaseModel):
    id: int
    title: str
    journal: str
    publication_year: int
    doi: str

    model_config = ConfigDict(from_attributes=True)


class PipelineRelationsResponse(BaseModel):
    pipeline_id: int
    algorithms: list[RelatedAlgorithm]
    literatures: list[RelatedLiterature]


class AlgorithmRelationsResponse(BaseModel):
    algorithm_id: int
    pipelines: list[RelatedPipeline]
    literatures: list[RelatedLiterature]


class LiteratureRelationsResponse(BaseModel):
    literature_id: int
    pipeline: RelatedPipeline | None
    algorithm: RelatedAlgorithm | None
