# Manages configuration for this repository.

variable "github_owner" {
  default = "kmontag"
}

variable "github_repository_name" {
  default = "NK2Reshift"
}

terraform {
  required_version = ">= 1.0.0"
  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> 6.0"
    }
  }
}

provider "github" {
  # Owner for e.g. repository resources.
  owner = var.github_owner
}

resource "github_repository" "default" {
  name       = var.github_repository_name
  visibility = "public"

  description = "Ableton Live 12 control surface for the Korg nanoKONTROL 2"

  vulnerability_alerts = true

  # Suggest updating PR branches.
  allow_update_branch = true

  # Don't allow merge commits from PRs (they should be squashed or rebased instead).
  allow_merge_commit = false

  # Allow squash merges and use the PR body as the default commit content.
  allow_squash_merge          = true
  squash_merge_commit_title   = "PR_TITLE"
  squash_merge_commit_message = "PR_BODY"

  # Clean up branches after merge.
  delete_branch_on_merge = true

  has_downloads = true
  has_issues    = true
  has_projects  = false
  has_wiki      = false
}

data "github_rest_api" "rulesets" {
  endpoint = "/repos/${var.github_owner}/${var.github_repository_name}/rulesets"

  lifecycle {
    postcondition {
      condition     = self.code == 200
      error_message = "Expected status code 200, but got ${self.code}"
    }
  }
}

locals {
  # Array containing entries like:
  #
  #  {"id": 12345, "name": "some name", ...}.
  #
  rulesets = jsondecode(data.github_rest_api.rulesets.body)

  # Get the existing main ruleset ID. This will be used to import the ruleset resource.
  #
  # If the ruleset ever gets deleted for some reason, this will be `null`, and the associated import
  # block can simply be commented out temporarily.
  main_ruleset_name = "main"
  main_ruleset_id   = one([for ruleset in local.rulesets : ruleset.id if ruleset.name == local.main_ruleset_name])
}

resource "github_repository_ruleset" "main" {
  name        = local.main_ruleset_name
  repository  = github_repository.default.name
  target      = "branch"
  enforcement = "active"

  conditions {
    ref_name {
      include = ["~DEFAULT_BRANCH"]
      exclude = []
    }
  }

  rules {
    # Require bypass permission to create/delete the default branch.
    creation = true
    deletion = true

    # Don't allow merge commits.
    required_linear_history = true

    # Prevent force-pushes to the default branch.
    non_fast_forward = true

    # Note - it would be nice to have required status checks, but this would add some
    # additional overhead to support automatic release commits with
    # `python-semantic-release`.  See
    # https://github.com/python-semantic-release/python-semantic-release/issues/311.
  }
}

# Import statements allowing the entire workspace to be imported. If re-creating
# resources from scratch, some or all of these will need to be commented out.
import {
  to = github_repository.default
  id = var.github_repository_name
}

import {
  to = github_repository_ruleset.main
  id = "${var.github_repository_name}:${local.main_ruleset_id}"
}
