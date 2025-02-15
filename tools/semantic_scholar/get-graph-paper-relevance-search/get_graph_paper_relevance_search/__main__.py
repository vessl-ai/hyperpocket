import json
import os
import sys
import requests

from pydantic import BaseModel, Field

token = os.getenv('SEMANTIC_SCHOLAR_TOKEN')


class GetGraphPaperRelevanceSearchRequest(BaseModel):
    query: str = Field(description="A plain-text search query string. No special query syntax is supported. Hyphenated query terms yield no matches (replace it with space to find matches).")
    fields: str = Field(description="A comma-separated list of the fields to be returned. If omitted, only the paperId and title will be returned.")
    publicationTypes: str = Field(description="Restricts results to any of the following paper publication types: Review, JournalArticle, CaseReport, ClinicalTrial, Conference, Dataset, Editorial, LettersAndComments, MetaAnalysis, News, Study, Book, BookSection.")
    openAccessPdf: str = Field(description="Restricts results to only include papers with a public PDF. This parameter does not accept any values.")
    minCitationCount: str = Field(description="Restricts results to only include papers with the minimum number of citations.")
    publicationDateOrYear: str = Field(description="Restricts results to the given range of publication dates or years (inclusive). Accepts the format <startDate>:<endDate> with each date in YYYY-MM-DD format.")
    year: str = Field(description="Restricts results to the given publication year or range of years (inclusive).")
    venue: str = Field(description="Restricts results to papers published in the given venues, formatted as a comma-separated list.")
    fieldsOfStudy: str = Field(description="Restricts results to papers in the given fields of study, formatted as a comma-separated list.")
    offset: int = Field(default=0, description="Used for pagination. When returning a list of results, start with the element at this position in the list.")
    limit: int = Field(default=100, description="The maximum number of results to return. Must be <= 100.")


def get_graph_paper_relevance_search(req: GetGraphPaperRelevanceSearchRequest):
    response = requests.get(
        url="https://api.semanticscholar.org/graph/v1/paper/search",
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": "2022-06-28",
        },
        json = req.model_dump(),
    )
    
    if response.status_code != 200:
        return f"failed to insert calendar events. error : {response.text}"

    return response.json()


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = GetGraphPaperRelevanceSearchRequest.model_validate(req)
    response = get_graph_paper_relevance_search(req_typed)

    print(response)


if __name__ == '__main__':
    main()