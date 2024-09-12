import json
from pathlib import Path

from typer import Option, Typer

from lta.api.configuration import Environment, get_survey_repository, set_environment
from lta.domain.survey_repository import SurveyCreation

app = Typer()


@app.command()
def add_surveys(
    source: Path = Option(..., help="path to the source JSON file"),
) -> None:
    set_environment(Environment.LOCAL_DEV)
    surveys = json.load(source.open())
    survey_repository = get_survey_repository()
    for survey in surveys:
        survey_repository.create_survey(survey["id"], SurveyCreation(**survey))


@app.command()
def list_surveys() -> None:
    set_environment(Environment.LOCAL_DEV)
    survey_repository = get_survey_repository()
    for survey in survey_repository.list_surveys():
        print(survey)


if __name__ == "__main__":
    app()
