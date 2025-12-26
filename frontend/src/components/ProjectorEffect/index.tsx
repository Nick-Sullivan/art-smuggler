import { ProjectorEffectView } from "./view";
import { useProjectorEffectViewModel } from "./viewModel";

export default function ProjectorEffect() {
  const viewModel = useProjectorEffectViewModel();
  return <ProjectorEffectView viewModel={viewModel} />;
}
