import { createFileRoute } from "@tanstack/react-router";
import { parseShowcaseTableSearch } from "../showcase-table-search";
import { ShowcaseView } from "../views/showcase-view";

export const Route = createFileRoute("/showcase")({
  validateSearch: parseShowcaseTableSearch,
  component: ShowcaseView,
});
