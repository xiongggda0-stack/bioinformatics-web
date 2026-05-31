import { readFile, writeFile } from "node:fs/promises";
import vm from "node:vm";
import ts from "typescript";

const [, , sourcePath, resourcesOutputPath, tutorialsOutputPath] = process.argv;

if (!sourcePath || !resourcesOutputPath || !tutorialsOutputPath) {
  throw new Error(
    "Usage: node export-database-resources.mjs <source> <resources-output> <tutorials-output>"
  );
}

const source = await readFile(sourcePath, "utf8");
const compiled = ts.transpileModule(source, {
  compilerOptions: {
    module: ts.ModuleKind.CommonJS,
    target: ts.ScriptTarget.ES2020
  }
}).outputText;
const module = { exports: {} };

vm.runInNewContext(compiled, {
  exports: module.exports,
  module,
  require: () => {
    throw new Error("Unexpected require in database resource source.");
  }
});

const resources = module.exports.databaseResources;

if (!Array.isArray(resources)) {
  throw new Error("databaseResources export was not found.");
}

const resourceSeeds = resources.map((resource) => ({
  slug: resource.id,
  name: resource.name,
  full_name: resource.fullName,
  category_key: resource.categoryKey,
  category_name: resource.categoryName,
  description: resource.description,
  use_cases_json: resource.useCases,
  data_types_json: resource.dataTypes,
  species_json: resource.species,
  tags_json: resource.tags,
  url: resource.url,
  download_url: resource.downloadUrl ?? null,
  api_url: resource.apiUrl ?? null,
  region: resource.region,
  rating: resource.rating
}));

const tutorialSeeds = resources.flatMap((resource) =>
  (resource.tutorials ?? []).map((tutorial) => ({
    slug: tutorial.id,
    resource_slug: resource.id,
    title: tutorial.title,
    scenario: tutorial.scenario,
    steps_json: tutorial.steps,
    example_query: tutorial.exampleQuery ?? null,
    entry_url: tutorial.entryUrl,
    content: tutorial.content
  }))
);

await writeFile(resourcesOutputPath, `${JSON.stringify(resourceSeeds, null, 2)}\n`);
await writeFile(tutorialsOutputPath, `${JSON.stringify(tutorialSeeds, null, 2)}\n`);

console.log(
  `Exported ${resourceSeeds.length} database resources and ${tutorialSeeds.length} tutorials.`
);
