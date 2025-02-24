# Hyperpocket Tools

## Available Tools

### Activeloop

- **[activeloop_query_data](activeloop/query-data)**
    - Query data from Deep Lake datasets using Activeloop's REST API
    - Auth: activeloop-token

### AgentQL

- **[agentql_query_data](agentql/query-data)**
    - Query data from a webpage using AgentQL
    - Auth: agentql-token

### Calendly

- **[calendly_create_one_off_event_type](calendly/create-one-off-event-type)**
    - Create calendly one off event type
    - Auth: calendly-oauth2

### GitHub

- **[github_create_issue](github/create-issue)**
    - Create a GitHub issue
    - Auth: github-oauth2 (scopes: repo)
- **[github_create_issue_comment](github/create-issue-comment)**
    - Create a GitHub issue comment
    - Auth: github-oauth2 (scopes: repo)
- **[github_create_pull_request](github/create-pull-request)**
    - Create a GitHub pull request
    - Auth: github-oauth2 (scopes: repo)
- **[github_list_issue_comments](github/list-issue-comments)**
    - List GitHub issue comments
    - Auth: github-oauth2 (scopes: repo)
- **[github_list_issues](github/list-issues)**
    - List GitHub issues
    - Auth: github-oauth2 (scopes: repo)
- **[github_list_pull_request_reviews](github/list-pull-request-reviews)**
    - List GitHub pull request reviews
    - Auth: github-oauth2 (scopes: repo)
- **[github_list_pull_requests](github/list-pull-requests)**
    - List GitHub pull requests
    - Auth: github-oauth2 (scopes: repo)
- **[github_merge_pull_request](github/merge-pull-request)**
    - Merge a GitHub pull request
    - Auth: github-oauth2 (scopes: repo)
- **[github_read_issue](github/read-issue)**
    - Read a GitHub issue
    - Auth: github-oauth2 (scopes: repo)
- **[github_read_pull_request](github/read-pull-request)**
    - Read a GitHub pull request
    - Auth: github-oauth2 (scopes: repo)
- **[github_search_commit](github/search-commit)**
    - Search GitHub commits
    - Auth: github-oauth2 (scopes: repo, user)
- **[github_search_user](github/search-user)**
    - Search GitHub users
    - Auth: github-oauth2 (scopes: repo, user)
- **[github_star_repo](github/star-repo)**
    - Star a GitHub repository
    - Auth: github-oauth2 (scopes: user, repo)
- **[github_update_issue](github/update-issue)**
    - Update a GitHub issue
    - Auth: github-oauth2 (scopes: repo)
- **[github_update_pull_request](github/update-pull-request)**
    - Update a GitHub pull request
    - Auth: github-oauth2 (scopes: repo)
- **[github_watch_repo](github/watch-repo)**
    - Watch a GitHub repository
    - Auth: github-oauth2 (scopes: user, repo)

### Google

- **[google_delete_calendar_events](google/delete-calendar-events)**
    - Delete google calendar events
    - Auth: google-oauth2 (scopes: calendar)
- **[google_get_calendar_events](google/get-calendar-events)**
    - Get google calendar events
    - Auth: google-oauth2 (scopes: calendar)
- **[google_get_calendar_list](google/get-calendar-list)**
    - Get google calendar list
    - Auth: google-oauth2 (scopes: calendar)
- **[google_insert_calendar_events](google/insert-calendar-events)**
    - Insert google calendar events
    - Auth: google-oauth2 (scopes: calendar)
- **[google_list_gmail](google/list-gmail)**
    - Get gmail list
    - Auth: google-oauth2 (scopes: gmail.readonly)

### Gumloop

- **[gumloop_list_saved_flows](gumloop/list-saved-flows)**
    - List saved flows in gumloop
    - Auth: gumloop
- **[gumloop_retrieve_input_schema](gumloop/retrieve-input-schema)**
    - Retrieve the input schema for flows in Gumloop
    - Auth: gumloop
- **[gumloop_start_flow_run](gumloop/start-flow-run)**
    - Start a flow run in gumloop
    - Auth: gumloop

### Linear

- **[linear_get_issues](linear/get-issues)**
    - Get linear issues by filters
    - Auth: linear

### Notion

- **[notion_search](notion/post-search)**
    - Search notion contents
    - Auth: notion-token

### SerpAPI

- **[apple_app_store](serpapi/apple-app-store)**
    - SERP API Apple App Store search API
    - Auth: serpapi
- **[baidu_search](serpapi/baidu-search)**
    - SERP API Baidu search API
    - Auth: serpapi
- **[bing_search](serpapi/bing-search)**
    - SERP API Bing search API
    - Auth: serpapi
- **[duckduckgo_search](serpapi/duckduckgo-search)**
    - SERP API DuckDuckGo search API
    - Auth: serpapi
- **[ebay_search](serpapi/ebay-search)**
    - SERP API eBay search API
    - Auth: serpapi
- **[google_finance](serpapi/google-finance)**
    - SERP API Google Finance API
    - Auth: serpapi
- **[google_flights](serpapi/google-flights)**
    - SERP API Google Flights API
    - Auth: serpapi
- **[google_hotels](serpapi/google-hotels)**
    - SERP API Google Hotels search API
    - Auth: serpapi
- **[google_scholar](serpapi/google-scholar)**
    - SERP API Google Scholar search API
    - Auth: serpapi
- **[google_search](serpapi/google-search)**
    - SERP API Google search API
    - Auth: serpapi
- **[naver_search](serpapi/naver-search)**
    - SERP API Naver search API
    - Auth: serpapi
- **[yahoo_search](serpapi/yahoo-search)**
    - SERP API Yahoo search API
    - Auth: serpapi
- **[yandex_search](serpapi/yandex-search)**
    - SERP API Yandex search API
    - Auth: serpapi
- **[yelp_search](serpapi/yelp-search)**
    - SERP API Yelp search API
    - Auth: serpapi
- **[youtube_search](serpapi/youtube-search)**
    - SERP API YouTube search API
    - Auth: serpapi

### Slack

- **[slack_get_messages](slack/get-messages)**
    - Get slack messages
    - Auth: slack (scopes: channels:history)
- **[slack_send_messages](slack/post-message)**
    - Send slack messages
    - Auth: slack (scopes: channels:history, chat:write)

### X (Twitter)

- **[x_create_post](x/create-post)**
    - Create X post
    - Auth: x (scopes: tweet.read, tweet.write, users.read)
- **[x_list_home_posts](x/list-home-posts-timeline)**
    - List X home posts in user timeline
    - Auth: x (scopes: tweet.read, users.read)
- **[x_user_lookup_me](x/user-lookup-me)**
    - Get my user data
    - Auth: x (scopes: tweet.read, users.read)

### Semantic Scholars

- **[semantic_scholars_get_graph_get_paper](semantic_scholar/get-graph-get-paper)**
- **[semantic_scholars_get_graph_paper_relevance_search](semantic_scholar/get-graph-paper-relevance-search)**

### Zinc

- **[zinc_create_orders](zinc/create-orders)**
    - Create Zinc Orders
    - Auth: zinc

### No Auth Required

- **[simple_echo_text](none/simple-echo-tool)**
    - Echo text
    - Auth: none
