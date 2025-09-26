"""Constants and templates for the Y-CTF CLI tool."""

# GraphQL Queries for CTFNote
GET_CTF_QUERY = """
query GetFullCtf($id: Int!) {
  ctf(id: $id) {
    ...FullCtfFragment
    __typename
  }
}

fragment FullCtfFragment on Ctf {
  ...CtfFragment
  tasks {
    nodes {
      ...TaskFragment
      __typename
    }
    __typename
  }
  secrets {
    ...CtfSecretFragment
    __typename
  }
  invitations {
    nodes {
      ...InvitationFragment
      __typename
    }
    __typename
  }
  __typename
}

fragment CtfFragment on Ctf {
  nodeId
  id
  granted
  ctfUrl
  ctftimeUrl
  description
  endTime
  logoUrl
  startTime
  weight
  title
  discordEventLink
  __typename
}

fragment TaskFragment on Task {
  nodeId
  id
  title
  ctfId
  padUrl
  description
  flag
  solved
  assignedTags {
    nodes {
      ...AssignedTagsFragment
      __typename
    }
    __typename
  }
  workOnTasks {
    nodes {
      ...WorkingOnFragment
      __typename
    }
    __typename
  }
  __typename
}

fragment AssignedTagsFragment on AssignedTag {
  nodeId
  taskId
  tagId
  tag {
    ...TagFragment
    __typename
  }
  __typename
}

fragment TagFragment on Tag {
  nodeId
  id
  tag
  __typename
}

fragment WorkingOnFragment on WorkOnTask {
  nodeId
  profileId
  active
  taskId
  __typename
}

fragment CtfSecretFragment on CtfSecret {
  nodeId
  credentials
  __typename
}

fragment InvitationFragment on Invitation {
  nodeId
  ctfId
  profileId
  __typename
}"""

GET_TEAM_QUERY = """
query getTeam {
  publicProfiles {
    nodes {
      ...PublicProfileFragment
      __typename
    }
    __typename
  }
}

fragment PublicProfileFragment on PublicProfile {
  id
  username
  color
  description
  role
  nodeId
  __typename
}
"""

GET_PAST_CTFS_QUERY = """
query PastCtfs($first: Int, $offset: Int) {
  pastCtf(first: $first, offset: $offset) {
    nodes {
      ...CtfFragment
      __typename
    }
    totalCount
    __typename
  }
}

fragment CtfFragment on Ctf {
  nodeId
  id
  granted
  ctfUrl
  ctftimeUrl
  description
  endTime
  logoUrl
  startTime
  weight
  title
  discordEventLink
  __typename
}
"""

# Writeup template
WRITEUP_TEMPLATE = """+++
title = "{challenge}"
description = "[Brief description of the challenge]"
authors = ["{author}"]
date = {date}

[taxonomies]
categories = ["{category}"]

[extra]
ctf = "{ctf}"
difficulty = "{difficulty}"
points = {points}
+++

## Description

[Describe the challenge here]

## Solution

[Explain your solution approach]

### Analysis

[Detail your analysis steps]

### Exploit

[Show the exploit code/steps]

### Flag

```
[FLAG_HERE]
```

## Files

[List any relevant files in the files/ directory]

## References

- [Any references or links]
"""

# CTF index template
CTF_INDEX_TEMPLATE = """+++
title = "{ctf}"
transparent = true
template = "ctf.html"
+++
"""

# HTTP headers for image downloading
IMAGE_DOWNLOAD_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}