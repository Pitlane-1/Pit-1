"""
Generate skill — produce IaC, Dockerfiles, and architecture diagrams.
"""
from pathlib import Path
from utils.logger import log


def run_generate(analysis: dict, recommendation: dict, diagram_only: bool = False) -> dict:
    from skills.generate.diagram import generate_diagram

    # output 폴더를 분석한 프로젝트 경로 기준으로 설정
    project_path = Path(analysis.get("project_path", ".")).resolve()
    out_dir = project_path / "pit1-output"
    out_dir.mkdir(parents=True, exist_ok=True)

    output = {
        "iac": None,
        "dockerfile": None,
        "diagram_ascii": None,
        "diagram_mermaid": None,
        "files_written": [],
    }

    diagrams = generate_diagram(analysis, recommendation)
    output["diagram_ascii"] = diagrams["ascii"]
    output["diagram_mermaid"] = diagrams["mermaid"]

    if diagram_only:
        return output

    if recommendation.get("iac_support"):
        log.info("Generating Terraform HCL...")
        from skills.generate.iac import generate_iac
        output["iac"] = generate_iac(analysis, recommendation)
        p = _write(out_dir / "main.tf", output["iac"])
        output["files_written"].append(str(p))

    if analysis.get("runtime") == "dynamic" and not (project_path / "Dockerfile").exists():
        log.info("Generating Dockerfile...")
        from skills.generate.dockerfile import generate_dockerfile
        output["dockerfile"] = generate_dockerfile(analysis)
        p = _write(out_dir / "Dockerfile", output["dockerfile"])
        output["files_written"].append(str(p))

    p = _write(out_dir / "architecture.mmd", diagrams["mermaid"])
    output["files_written"].append(str(p))

    return output


def _write(path: Path, content: str) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    log.info(f"Written: {path}")
    return path
