import sys
import os
import tomlkit
import re
import requests
from slugify import slugify
from rich import print

from .base import BaseImporter


class CTFImporter(BaseImporter):
    BASE_URL = "http://note.yctf.ch"

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

    def add_arguments(self, parser):
        parser.add_argument("-c", "--ctf", help="CTF Name")
        parser.add_argument("-i", "--id", help="CTF ID")
        parser.add_argument("-a", "--auth", help="Authorization token", required=True)
        parser.add_argument("-o", "--output", help="Output directory", default=".")
        parser.add_argument("-f", "--force", help="Force download", action="store_true")
        parser.add_argument("--remove-header", help="Remove header (h1)", action="store_true")

    def download_note(self, pad_url):
        url = f"{self.BASE_URL}{pad_url}/download"
        response = requests.get(url)
        response.raise_for_status()
        return response.text

    def execute_query(self, op, query, variables, token):
        url = f"{self.BASE_URL}/graphql"
        headers = {"Authorization": f"Bearer {token}"}
        data = [
            {
                "operationName": op,
                "variables": variables,
                "query": query,
            }
        ]
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        response = response.json()[0]
        if "errors" in response:
            print(response["errors"])
            sys.exit(1)
        return response["data"]

    def get_ctf_tasks(self, ctf_id, token):
        return self.execute_query("GetFullCtf", self.GET_CTF_QUERY, {"id": ctf_id}, token)["ctf"]

    def get_team(self, token):
        return self.execute_query("getTeam", self.GET_TEAM_QUERY, {}, token)["publicProfiles"]["nodes"]

    def get_past_ctfs(self, token):
        return self.execute_query("PastCtfs", self.GET_PAST_CTFS_QUERY, {}, token)["pastCtf"]["nodes"]

    def run(self, args):
        if args.ctf:
            ctf_data = self.get_past_ctfs(args.auth)
            ctf = next(
                (c for c in ctf_data if c["title"].lower() == args.ctf.lower()), None
            )
            if not ctf:
                print(f"CTF [bold]{args.ctf}[/bold] not found")
                sys.exit(1)
            args.id = ctf["id"]
            print(f"Found CTF [bold]{ctf['title']}[/bold] ({args.id})")

        if not args.id:
            print("CTF ID is required")
            sys.exit(1)
        if not args.output.endswith("/"):
            args.output += "/"

        if not os.path.exists(args.output):
            os.makedirs(args.output)

        ctf_data = self.get_ctf_tasks(int(args.id), args.auth)
        team = self.get_team(args.auth)
        for task in ctf_data["tasks"]["nodes"]:
            dir_path = f"{args.output}{slugify(task['title'])}"
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            path = f"{dir_path}/index.md"
            if os.path.exists(path) and not args.force:
                print(f"Skipping {task['title']}")
                continue

            tags = [tag["tag"]["tag"] for tag in task["assignedTags"]["nodes"]]
            authors = [
                author["username"]
                for author in team
                if author["id"] in [w["profileId"] for w in task["workOnTasks"]["nodes"]]
            ]

            if not authors:
                authors = ["Unknown"]
                print(f"Authors not found for {task['title']}")

            frontmatter = {
                "title": task["title"],
                "description": task["description"],
                "taxonomies": {
                    "categories": tags,
                },
                "authors": authors,
                "date": tomlkit.date(
                    ctf_data["startTime"].split("T")[0],
                ),
            }

            frontmatter = tomlkit.dumps(frontmatter)

            download_note_url = task["padUrl"]
            note = self.download_note(download_note_url)
            if args.remove_header:
                note = re.sub(r"^# .*\n", "", note)

            with open(path, "w") as f:
                f.write(f"+++\n{frontmatter}+++\n")
                f.write(note)

            print(f"Downloaded {task['title']}")