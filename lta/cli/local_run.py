import json
import os
from pathlib import Path

from typer import Option, Typer

from lta.api.configuration import get_survey_repository
from lta.domain.survey_repository import SurveyCreation

app = Typer()


@app.command()
def add_surveys(
    source: Path = Option(..., help="path to the source JSON file"),
) -> None:
    surveys = json.load(source.open())
    survey_repository = get_survey_repository()
    for survey in surveys:
        survey_repository.create_survey(survey["id"], SurveyCreation(**survey))


@app.command()
def list_surveys() -> None:
    survey_repository = get_survey_repository()
    for survey in survey_repository.list_surveys():
        print(survey)


if __name__ == "__main__":
    if os.environ.get("LOCAL_RUN", "").casefold() != "true":
        raise RuntimeError(
            "This script can only be run locally.  Add LOCAL_RUN=true to your environment variables."
        )

    app()
