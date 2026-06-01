export interface TrustApplicability {
  species?: string[];
  data_types?: string[];
  experiment_types?: string[];
}

export interface TrustMetadata {
  validation_status?: string;
  last_reviewed_at?: string;
  difficulty?: string;
  official_docs_url?: string | null;
  version?: string;
  installation?: string;
  applicability?: TrustApplicability;
  disclaimer?: string;
}

export function hasTrustValue(value?: string | null): value is string {
  return Boolean(value?.trim());
}

export function getTrustValue(value?: string | null): string {
  return value?.trim() ? value : "待补充";
}

export function getTrustList(values?: string[] | null): string[] {
  const populatedValues = values?.filter((value) => value.trim());

  return populatedValues?.length ? populatedValues : ["待补充"];
}
