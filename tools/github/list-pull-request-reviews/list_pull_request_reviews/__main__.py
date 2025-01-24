import json
import os
import sys
from typing import List, Tuple

from github import Auth, Github
from pydantic import BaseModel, Field

auth = Auth.Token(os.environ.get("GITHUB_TOKEN", ""))
client = Github(auth=auth)


class GithubListPRReviewsRequest(BaseModel):
    owner: str = Field(..., description="The owner of the repository")
    repo: str = Field(..., description="The name of the repository")
    pr_number: int = Field(..., description="The number of the pull request")
    number_of_reviews: int = Field(10, description="The number of reviews to return")


def list_pr_reviews(req: GithubListPRReviewsRequest) -> List[Tuple[int, str]]:
    repo = client.get_repo(f"{req.owner}/{req.repo}")
    res = repo.get_pull(req.pr_number).get_reviews()

    reviews = []
    page_number = 0

    while len(reviews) < req.number_of_reviews:
        page = res.get_page(page_number)
        if len(page) == 0:
            break

        reviews.extend([review.raw_data for review in page])
        page_number += 1

    return reviews


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = GithubListPRReviewsRequest.model_validate(req)
    response = list_pr_reviews(req_typed)

    print(json.dumps(response))


if __name__ == "__main__":
    main()
